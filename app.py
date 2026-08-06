import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import io
import zipfile
import textwrap
import datetime

# 1. Configuración de la página y Diseño Visual
st.set_page_config(page_title="Generador Certificados COIL-UCT", layout="centered")

# Mostramos el Banner Institucional (Recuerda subir 'banner.png' a GitHub)
try:
    st.image("banner.png", use_container_width=True)
except FileNotFoundError:
    st.warning("⚠️ No se encontró el archivo 'banner.png' en GitHub. Sube la imagen para ver el diseño completo.")

st.title("🎓 Generador Automático de Certificados COIL-UCT")
st.write("Bienvenido. Sube el Excel con los datos y la imagen base del diploma para generar todos los PDFs al instante.")

# --- Sección de Ayuda para el Usuario ---
with st.expander("📊 Ver estructura requerida del Excel"):
    st.write("Tu archivo Excel (.csv) debe tener exactamente estas 5 columnas, respetando mayúsculas y tildes:")
    st.code("Nombre, Universidad, Curso, Colaborador, Semestre")
    st.write("**Ejemplo de una fila:** Juan Pérez, Universidad Nacional, Derecho, María Gómez, segundo semestre 2026")

# 2. Botones para subir archivos
archivo_excel = st.file_uploader("1. Sube tu Excel actualizado (.csv)", type=["csv"])
imagen_base = st.file_uploader("2. Sube el diseño limpio del diploma (sin textos variables, .png, .jpg)", type=["png", "jpg"])

# 3. Lógica Principal
if archivo_excel is not None and imagen_base is not None:
    
    if st.button("✨ Generar Todos los Certificados"):
        
        # Leemos el Excel
        alumnos = pd.read_csv(archivo_excel)
        
        # Definimos las 5 columnas que exigimos ahora
        columnas_necesarias = ['Nombre', 'Universidad', 'Curso', 'Colaborador', 'Semestre']
        
        # Verificamos si el Excel cumple las reglas
        if all(columna in alumnos.columns for columna in columnas_necesarias):
            
            with st.spinner("Preparando la magia... por favor espera."):
                st.success("¡Datos correctos! Iniciando generación.")
                
                # --- Preparación de Variables Globales (Fecha y Fuentes) ---
                
                # A. Generar Fecha Automática en Español
                fecha_actual = datetime.date.today()
                
                # Diccionario manual para meses en español (para mayor estabilidad en la nube)
                meses_espanol = {
                    1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio",
                    7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
                }
                
                dia = fecha_actual.day
                mes_nombre = meses_espanol[fecha_actual.month]
                anio = fecha_actual.year
                
                texto_fecha_final = f"Temuco, {dia} de {mes_nombre} de {anio}"
                
                # B. Cargar Fuentes Calibri Reales (Subidas a GitHub)
                try:
                    fuente_constancia = ImageFont.truetype("CALIBRIB.TTF", 80) # Título grande, negrita
                    fuente_nombre = ImageFont.truetype("CALIBRIB.TTF", 65)      # Nombre grande, negrita
                    fuente_parrafo = ImageFont.truetype("CALIBRI.TTF", 55)      # Párrafo normal, tamaño medio
                    fuente_fecha = ImageFont.truetype("CALIBRI.TTF",50)        # Fecha normal, tamaño pequeño
                except OSError:
                    st.error("⚠️ No se encontraron los archivos de fuente 'CALIBRI.TTF' o 'CALIBRIB.TTF' en GitHub. Revisa tus archivos.")
                    st.stop()
                
                # Creamos el archivo ZIP en memoria
                buffer_zip = io.BytesIO()
                
                with zipfile.ZipFile(buffer_zip, "w") as archivo_zip:
                    
                    # --- Ciclo de Generación de Certificados ---
                    total_certificados = len(alumnos)
                    barra_progreso = st.progress(0)
                    
                    for indice, fila in alumnos.iterrows():
                        # Actualizar barra de progreso
                        porcentaje = int((indice + 1) / total_certificados * 100)
                        barra_progreso.progress(porcentaje)
                        
                        # Extraemos las 5 variables de la fila
                        nombre_alumno = str(fila['Nombre']).strip()
                        universidad_origen = str(fila['Universidad']).strip()
                        nombre_curso = str(fila['Curso']).strip()
                        docente_colaborador = str(fila['Colaborador']).strip()
                        periodo_semestre = str(fila['Semestre']).strip()
                        
                        # Armamos el párrafo redactado completo
                        texto_parrafo_completo = f"Académico de la {universidad_origen}, desarrolló Clases Espejo del curso: “{nombre_curso}” realizado en colaboración con la docente, {docente_colaborador} de la Universidad Católica de Temuco. Este curso tuvo lugar el {periodo_semestre}. La actividad contribuyó al desarrollo de competencias interculturales de los estudiantes y a la internacionalización del currículo."
                        
                        # *** La Magia del Text Wrapping (Cortar Párrafo) ***
                        parrafo_cortado = textwrap.fill(texto_parrafo_completo, width=75)
                        
                        # Abrimos la imagen limpia
                        certificado = Image.open(imagen_base).convert('RGB')
                        dibujo = ImageDraw.Draw(certificado)
                        
                        # Obtenemos ancho y alto de la imagen para centrar
                        ancho_imagen, alto_imagen = certificado.size
                        centro_x = ancho_imagen / 2
                        
                        # --- Dibujar Textos en la Imagen ---
                        # ¡ATENCIÓN! Coordenadas (Y) ESTIMADAS. Ajustar números según tu base.
                        
                      
                        
                        
                        # 2. Nombre del Docente (Negrita, Grande, Centrado)
                        dibujo.text((centro_x, 950), nombre_alumno, fill="#0070C0", anchor="mm", font=fuente_nombre)
                        
                        # 3. Párrafo Cortado (Normal, Mediano, Centrado, align="center")
                        dibujo.text((centro_x, 1200), parrafo_cortado, fill="black", anchor="ma", align="center", font=fuente_parrafo, spacing=15)
                        
                        # 4. Fecha Automática (Esquina Inferior Derecha)
                        dibujo.text((ancho_imagen - 100, alto_imagen - 150), texto_fecha_final, fill="black", anchor="rm", font=fuente_fecha)
                        
                        # Guardamos en memoria como PDF
                        buffer_pdf = io.BytesIO()
                        certificado.save(buffer_pdf, format="PDF")
                        
                        # Metemos el PDF al ZIP
                        archivo_zip.writestr(f"Certificado_{nombre_alumno}.pdf", buffer_pdf.getvalue())
                        
                # Finalizado el ciclo
                st.balloons()
                
                # 4. Botón de Descarga del ZIP
                st.download_button(
                    label="⬇️ Descargar TODOS los certificados (.zip)",
                    data=buffer_zip.getvalue(),
                    file_name=f"Certificados_COIL_UCT_{fecha_actual}.zip",
                    mime="application/zip"
                )
            
        else:
            st.error("⚠️ El Excel no tiene las columnas correctas. Revisa la ayuda desplegable más arriba para ver el formato exigido.")
            st.stop()

# --- Firma final centrada con HTML: ¡Actualizada con tu nombre! ---
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>Sistema Automatizado de Certificados UCT<br>Temuco, 2026<br><b>Desarrollado con ❤️ por Moisés Morales</b></p>", unsafe_allow_html=True)
