import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import io
import zipfile

# 1. Configuración de la página
st.set_page_config(page_title="Generador Certificados COIL-UCT", layout="centered")

# Banner Institucional
try:
    st.image("banner.png", use_container_width=True)
except FileNotFoundError:
    st.warning("⚠️ No se encontró 'banner.png' en GitHub. Sube la imagen para ver el diseño completo.")

st.title("🎓 Generador Automático de Certificados COIL-UCT")
st.write("Sube tu lista de nombres en Excel y la imagen base del diploma con el texto incorporado.")

st.markdown("---")

# 2. Subida de Archivos
col1, col2 = st.columns(2)

with col1:
    archivo_excel = st.file_uploader("1. Sube tu Excel (.csv) con la columna 'Nombre'", type=["csv"])

with col2:
    imagen_base = st.file_uploader("2. Sube la plantilla base del diploma (.png, .jpg)", type=["png", "jpg"])

# 3. Lógica de Generación
if archivo_excel is not None and imagen_base is not None:
    
    st.markdown("---")
    st.markdown("### 🎯 Ajuste de Posición y Tamaño del Nombre")
    st.info("Ajusta los controles si necesitas subir, bajar o cambiar el tamaño del nombre sobre tu plantilla:")

    col_pos, col_size = st.columns(2)
    with col_pos:
        pos_y = st.number_input("Posición Vertical (Eje Y en píxeles)", min_value=100, max_value=3000, value=950, step=10)
    with col_size:
        tamano_fuente = st.number_input("Tamaño de Fuente del Nombre", min_value=20, max_value=200, value=70, step=5)

    if st.button("✨ Estampar Nombres y Generar PDFs"):
        
        alumnos = pd.read_csv(archivo_excel)
        
        if 'Nombre' in alumnos.columns:
            
            with st.spinner("Estampando nombres y preparando el archivo ZIP..."):
                
                # Cargar Fuente Calibri Bold
                try:
                    fuente_nombre = ImageFont.truetype("CALIBRIB.TTF", tamano_fuente)
                except OSError:
                    st.error("⚠️ No se encontró 'CALIBRIB.TTF' en GitHub. Asegúrate de subir el archivo de fuente.")
                    st.stop()
                
                buffer_zip = io.BytesIO()
                
                with zipfile.ZipFile(buffer_zip, "w") as archivo_zip:
                    
                    total = len(alumnos)
                    barra = st.progress(0)
                    
                    for i, fila in alumnos.iterrows():
                        barra.progress(int((i + 1) / total * 100))
                        
                        nombre_alumno = str(fila['Nombre']).strip()
                        
                        # Abrir plantilla base
                        certificado = Image.open(imagen_base).convert('RGB')
                        dibujo = ImageDraw.Draw(certificado)
                        
                        ancho, alto = certificado.size
                        centro_x = ancho / 2
                        
                        # Estampar únicamente el Nombre en Azul Institucional (#0070C0)
                        dibujo.text((centro_x, pos_y), nombre_alumno, fill="#0070C0", anchor="mm", font=fuente_nombre)
                        
                        # Guardar en PDF e incluir en ZIP
                        buffer_pdf = io.BytesIO()
                        certificado.save(buffer_pdf, format="PDF")
                        archivo_zip.writestr(f"Certificado_{nombre_alumno}.pdf", buffer_pdf.getvalue())
                        
                st.balloons()
                st.success("¡Todos los certificados fueron estampados exitosamente!")
                
                st.download_button(
                    label="⬇️ Descargar Certificados (.zip)",
                    data=buffer_zip.getvalue(),
                    file_name="Certificados_COIL_UCT.zip",
                    mime="application/zip"
                )
            
        else:
            st.error("⚠️ El archivo Excel debe tener una columna llamada exactamente 'Nombre'.")
            st.stop()

# Firma final
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>Sistema Automatizado de Certificados UCT<br>Temuco, 2026<br><b>Desarrollado con ❤️ por Moisés Morales</b></p>", unsafe_allow_html=True)
