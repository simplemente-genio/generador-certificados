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
with st.expander("📊 Ver estructura requerida del Nuevo Excel para Estudiantes"):
    st.write("Tu archivo Excel (.csv) debe tener exactamente estas 7 columnas, respetando mayúsculas y tildes:")
    st.code("Nombre, Universidad, Curso, Horas, Academico UCT, Academico Contraparte, Semestre")
    st.write("**Ejemplo de una fila:** Juan Pérez, U. de Antioquia, Derecho Ambiental, 20, María Gómez, Carlos Ruiz, segundo semestre 2026")

# 2. Botones para subir archivos
archivo_excel = st.file_uploader("1. Sube tu Excel actualizado (.csv)", type=["csv"])
imagen_base = st.file_uploader("2. Sube el diseño limpio del diploma (sin textos variables, .png, .jpg)", type=["png", "jpg"])

# 3. Lógica Principal
if archivo_excel is not None and imagen_base is not None:
    
    st.markdown("### ⚙️ Configuración del Certificado")
    # Selector interactivo para el tipo de actividad
    tipo_actividad = st.selectbox("¿Qué tipo de actividad certificamos hoy?", ["Curso COIL", "MasterClass", "Clase Espejo"])
    
    if st.button("✨ Generar Todos los Certificados"):
        
        # Leemos el Excel
        alumnos = pd.read_csv(archivo_excel)
        
        # Definimos las 7 columnas que exigimos ahora para estudiantes
        columnas_necesarias = ['Nombre', 'Universidad', 'Curso', 'Horas', 'Academico UCT', 'Academico Contraparte', 'Semestre']
        
        # Verificamos si el Excel cumple las reglas
        if all(columna in alumnos.columns for columna in columnas_necesarias):
            
            with st.spinner("Preparando la magia... por favor espera."):
                st.success("¡Datos correctos! Iniciando generación.")
                
                # --- Preparación de Variables Globales (Fecha y Fuentes) ---
                
                # A. Generar Fecha Automática en Español
                fecha_actual = datetime.date.today()
                
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
                    fuente_nombre = ImageFont.truetype("CALIBRIB.TTF", 65)      # Nombre grande, negrita
                    fuente_parrafo = ImageFont.truetype("CALIBRI.TTF", 55)      # Párrafo normal, tamaño medio
                    fuente_fecha = ImageFont.truetype("CALIBRI.TTF", 50)        # Fecha normal, tamaño pequeño
                except OSError:
                    st.error("⚠️ No se encontraron los archivos de fuente 'CALIBRI.TTF' o 'CALIBRIB.TTF' en GitHub. Revisa tus archivos.")
                    st.stop()
                
                # Creamos el archivo ZIP en memoria
                buffer_zip = io.BytesIO()
                
                with zipfile.ZipFile(buffer_zip, "w") as archivo_zip:
                    
                    # --- Ciclo de Generación de Certificados ---
                    total_certificados = len(alumnos)
                    barra_progreso = st.progress(0)
                    
                    # Inteligencia gramatical para el artículo ("el" Curso vs "la" MasterClass)
                    articulo = "el" if tipo_actividad == "Curso COIL" else "la"
                    
                    for indice, fila in alumnos.iterrows():
                        # Actualizar barra de progreso
                        porcentaje = int((indice + 1) / total_certificados * 100)
                        barra_progreso.progress(porcentaje)
                        
                        # Extraemos las variables
                        nombre_alumno = str(fila['Nombre']).strip()
                        universidad_origen = str(fila['Universidad']).strip()
                        nombre_curso = str(fila['Curso']).strip()
                        horas_curso = str(fila['Horas']).strip()
                        docente_uct = str(fila['Academico UCT']).strip()
                        docente_contraparte = str(fila['Academico Contraparte']).strip()
                        periodo_semestre = str(fila['Semestre']).strip()
                        
                        # Armamos el NUEVO párrafo redactado completo para estudiantes
                        texto_parrafo_completo = f"Estudiante de la {universidad_origen}, participó en {articulo} {tipo_actividad} “{nombre_curso}”, con una duración de {horas_curso} horas académicas. Esta actividad fue dictada en colaboración por los académicos {docente_contraparte} ({universidad_origen}) y {docente_uct} (Universidad Católica de Temuco), durante el {periodo_semestre}. Su participación contribuyó al desarrollo de competencias interculturales y a la internacionalización del currículo."
                        
                        # *** La Magia del Text Wrapping (Cortar Párrafo) ***
                        parrafo_cortado = textwrap.fill(texto_parrafo_completo, width=75)
                        
                        # Abrimos la imagen limpia
                        certificado = Image.open(imagen_base).convert('RGB')
                        dibujo = ImageDraw.Draw(certificado)
                        
                        # Obtenemos ancho y alto de la imagen para centrar
                        ancho_imagen, alto_imagen = certificado.size
                        centro_x = ancho_imagen / 2
                        
                        # --- Dibujar Textos en la Imagen ---
                        
                        # 1. Nombre del Estudiante (Negrita, Grande, Centrado, Azul Institucional)
                        dibujo.text((centro_x, 1000), nombre_alumno, fill="#0070C0", anchor="mm", font=fuente_nombre)
                        
                        # 2. Párrafo Cortado (Normal, Mediano, Centrado, Gris, con interlineado)
                        dibujo.text((centro_x, 1200), parrafo_cortado, fill="#858784", anchor="ma", align="center", font=fuente_parrafo, spacing=15)
                        
                        # 3. Fecha Automática (Esquina Inferior Derecha)
                        dibujo.text((ancho_imagen - 100, alto_imagen - 150), texto_fecha_final, fill="black", anchor="rm", font=fuente_fecha)
                        
                        # Guardamos en memoria como PDF
                        buffer_pdf = io.BytesIO()
                        certificado.save(buffer_pdf, format="PDF")
                        
                        # Metemos el PDF al ZIP
                        archivo_zip.writestr(f"Certificado_Estudiante_{nombre_alumno}.pdf", buffer_pdf.getvalue())
                        
                # Finalizado el ciclo
                st.balloons()
                
                # Botón de Descarga del ZIP
                st.download_button(
                    label=f"⬇️ Descargar TODOS los certificados ({tipo_actividad}) (.zip)",
                    data=buffer_zip.getvalue(),
                    file_name=f"Certificados_{tipo_actividad}_UCT_{fecha_actual}.zip",
                    mime="application/zip"
                )
            
        else:
            st.error("⚠️ El Excel no tiene las columnas correctas. Revisa la ayuda desplegable para ver el nuevo formato de 7 columnas.")
            st.stop()

# --- Firma final centrada ---
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>Sistema Automatizado de Certificados UCT<br>Temuco, 2026<br><b>Desarrollado con ❤️ por Moisés Morales</b></p>", unsafe_allow_html=True)
