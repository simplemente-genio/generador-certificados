import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import io
import zipfile
import textwrap
import datetime

# 1. Configuración de la página y Diseño Visual
st.set_page_config(page_title="Generador Certificados COIL-UCT", layout="centered")

# Mostramos el Banner Institucional
try:
    st.image("banner.png", use_container_width=True)
except FileNotFoundError:
    st.warning("⚠️ No se encontró el archivo 'banner.png' en GitHub. Sube la imagen para ver el diseño completo.")

st.title("🎓 Generador Automático de Certificados COIL-UCT")
st.write("Sube la lista de estudiantes en Excel y completa los datos de la actividad para generar los diplomas al instante.")

# --- Sección de Ayuda para el Usuario ---
with st.expander("📊 Ver estructura requerida del Excel"):
    st.write("Ahora tu Excel (.csv) solo necesita **una sola columna** con los nombres:")
    st.code("Nombre")
    st.write("**Ejemplo:**\nJuan Esteban Orjuela González\nMaría Fernanda Silva")

# 2. Botones para subir archivos
archivo_excel = st.file_uploader("1. Sube tu Excel de estudiantes (.csv)", type=["csv"])
imagen_base = st.file_uploader("2. Sube el diseño limpio del diploma (.png, .jpg)", type=["png", "jpg"])

# 3. Formulario con datos del Curso / Actividad
if archivo_excel is not None and imagen_base is not None:
    
    st.markdown("---")
    st.markdown("### 📝 Datos de la Actividad Académica")
    st.info("Completa estos campos una sola vez y se aplicarán a todos los certificados del lote:")

    col1, col2 = st.columns(2)
    
    with col1:
        tipo_actividad = st.selectbox("Tipo de Actividad", ["curso COIL", "Masterclass", "Clase Espejo"])
        nombre_actividad = st.text_input("Nombre de la actividad / Versión", "Ortesis UCT-ULEAM”, Versión 2026")
        semestre = st.selectbox("Semestre", ["primer", "segundo"])
        anio = st.text_input("Año de ejecución", "2026")
        horas = st.text_input("Horas cronológicas totales", "12")

    with col2:
        carrera_uct = st.text_input("Carrera UCT", "Terapia Ocupacional")
        asignatura_uct = st.text_input("Asignatura UCT", "PAA-03-F-003 Ortótica y Producto de Apoyo")
        docente_uct = st.text_input("Académico(a) UCT", "Leonardo Cuevas Zepeda")
        
    st.markdown("#### 🤝 Datos de la Universidad Contraparte")
    col3, col4 = st.columns(2)
    
    with col3:
        universidad_contraparte = st.text_input("Universidad Contraparte", "Universidad Laica Eloy Alfaro de Manabí, Manta, (Ecuador)")
        carrera_contraparte = st.text_input("Carrera Contraparte", "Terapia Ocupacional")

    with col4:
        asignatura_contraparte = st.text_input("Asignatura Contraparte", "Ortótica y Apoyo")
        docente_contraparte = st.text_input("Académico(a) Contraparte", "Ricardo Bravo Zambrano")

    st.markdown("---")

    # 4. Botón de Generación
    if st.button("✨ Generar Todos los Certificados"):
        
        # Leemos el Excel
        alumnos = pd.read_csv(archivo_excel)
        
        # Verificamos que tenga la columna 'Nombre'
        if 'Nombre' in alumnos.columns:
            
            with st.spinner("Generando certificados... por favor espera."):
                
                # --- Fecha Automática en Español ---
                fecha_actual = datetime.date.today()
                meses_espanol = {
                    1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio",
                    7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
                }
                dia = fecha_actual.day
                mes_nombre = meses_espanol[fecha_actual.month]
                anio_actual = fecha_actual.year
                texto_fecha_final = f"Temuco, {dia} de {mes_nombre} de {anio_actual}"
                
                # --- Cargar Fuentes ---
                try:
                    fuente_nombre = ImageFont.truetype("CALIBRIB.TTF", 65)      # Nombre en Negrita
                    fuente_parrafo = ImageFont.truetype("CALIBRI.TTF", 42)      # Párrafo normal
                    fuente_cierre = ImageFont.truetype("CALIBRIB.TTF", 42)     # Cierre en Negrita
                    fuente_fecha = ImageFont.truetype("CALIBRI.TTF", 40)        # Fecha
                except OSError:
                    st.error("⚠️ No se encontraron los archivos de fuente 'CALIBRI.TTF' o 'CALIBRIB.TTF' en GitHub. Revisa la carpeta.")
                    st.stop()
                
                # Zip en memoria
                buffer_zip = io.BytesIO()
                
                with zipfile.ZipFile(buffer_zip, "w") as archivo_zip:
                    
                    total_certificados = len(alumnos)
                    barra_progreso = st.progress(0)
                    
                    for indice, fila in alumnos.iterrows():
                        porcentaje = int((indice + 1) / total_certificados * 100)
                        barra_progreso.progress(porcentaje)
                        
                        nombre_alumno = str(fila['Nombre']).strip()
                        
                        # Armado del Párrafo Principal con la plantilla exacta
                        texto_p1 = f"Estudiante de la carrera de {carrera_contraparte} de la {universidad_contraparte}, participó exitosamente en el {tipo_actividad} “{nombre_actividad}”, desarrollado durante el {semestre} semestre de {anio} en el marco de las asignaturas {asignatura_uct} y {asignatura_contraparte}."
                        texto_p2 = f"Esta experiencia de aprendizaje colaborativo internacional (Collaborative Online International Learning – COIL) fue implementada conjuntamente por la {universidad_contraparte} y la Universidad Católica de Temuco (Chile), promoviendo el intercambio académico e intercultural entre estudiantes de las carreras de {carrera_contraparte} y {carrera_uct} de ambas instituciones."
                        texto_p3 = f"La actividad fue coordinada por los académicos {docente_uct} y {docente_contraparte}, y contempló una dedicación total de {horas} horas cronológicas."
                        
                        texto_completo = f"{texto_p1}\n\n{texto_p2}\n\n{texto_p3}"
                        
                        # Formatear Párrafo (Wrapping)
                        parrafo_cortado = textwrap.fill(texto_completo, width=80)
                        texto_cierre = "Se extiende el presente certificado para los fines que el estudiante estime pertinentes."
                        cierre_cortado = textwrap.fill(texto_cierre, width=80)
                        
                        # Imagen y Lienzo
                        certificado = Image.open(imagen_base).convert('RGB')
                        dibujo = ImageDraw.Draw(certificado)
                        
                        ancho_imagen, alto_imagen = certificado.size
                        centro_x = ancho_imagen / 2
                        
                        # --- Dibujar Textos ---
                        # 1. Nombre del Estudiante (Azul Institucional)
                        dibujo.text((centro_x, 950), nombre_alumno, fill="#0070C0", anchor="mm", font=fuente_nombre)
                        
                        # 2. Párrafo Principal (Gris, Centrado, con interlineado)
                        dibujo.text((centro_x, 1120), parrafo_cortado, fill="#858784", anchor="ma", align="center", font=fuente_parrafo, spacing=18)
                        
                        # 3. Frase de Cierre (Azul Institucional, Párrafo Aparte)
                        dibujo.text((centro_x, 1620), cierre_cortado, fill="#0070C0", anchor="ma", align="center", font=fuente_cierre, spacing=12)
                        
                        # 4. Fecha (Esquina Inferior Derecha)
                        dibujo.text((ancho_imagen - 120, alto_imagen - 180), texto_fecha_final, fill="black", anchor="rm", font=fuente_fecha)
                        
                        # Guardar PDF en memoria
                        buffer_pdf = io.BytesIO()
                        certificado.save(buffer_pdf, format="PDF")
                        archivo_zip.writestr(f"Certificado_{nombre_alumno}.pdf", buffer_pdf.getvalue())
                        
                st.balloons()
                
                # Botón de Descarga
                st.download_button(
                    label="⬇️ Descargar TODOS los certificados (.zip)",
                    data=buffer_zip.getvalue(),
                    file_name=f"Certificados_COIL_UCT_{fecha_actual}.zip",
                    mime="application/zip"
                )
            
        else:
            st.error("⚠️ El Excel no contiene una columna llamada 'Nombre'. Revisa la cabecera del archivo.")
            st.stop()

# --- Firma final ---
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>Sistema Automatizado de Certificados UCT<br>Temuco, 2026<br><b>Desarrollado con ❤️ por Moisés Morales</b></p>", unsafe_allow_html=True)
