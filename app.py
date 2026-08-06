import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import io
import zipfile

# 1. Títulos de tu página web
st.title("🎓 Generador Automático de Certificados")
st.write("Sube tus archivos y descarga todos los diplomas en un solo clic.")

# 2. Botones para subir archivos
archivo_excel = st.file_uploader("1. Sube tu Excel (.csv)", type=["csv"])
imagen_base = st.file_uploader("2. Sube el diseño del diploma (.png, .jpg)", type=["png", "jpg"])

# 3. Solo si el usuario ya subió AMBOS archivos, mostramos el botón mágico
if archivo_excel is not None and imagen_base is not None:
    
    if st.button("Generar Certificados ✨"):
        
        # Leemos el Excel
        alumnos = pd.read_csv(archivo_excel)
        
        # 1. Definimos las columnas que exigimos
        columnas_necesarias = ['Nombre', 'Curso', 'Horas']
        
        # 2. Verificamos si el Excel cumple las reglas
        if all(columna in alumnos.columns for columna in columnas_necesarias):
            st.success("¡Datos correctos! Preparando la magia...")
            
            # [!] IMPORTANTE: Todo tu código que crea el buffer_zip, 
            # el ciclo 'for' que dibuja los certificados y el st.balloons()
            # ahora debe ir aquí adentro. Tendrás que mover todas esas líneas 
            # un espacio (un Tab) hacia la derecha para que pertenezcan a este 'if'.
            
        else:
            # Si falta alguna columna, el programa se detiene y muestra esto
            st.error("⚠️ El Excel debe tener exactamente estas 3 columnas: Nombre, Curso, Horas. ¡Por favor revisa tu archivo!")
        
            # Creamos un "archivo ZIP virtual" en la memoria
            buffer_zip = io.BytesIO()
        
            with zipfile.ZipFile(buffer_zip, "w") as archivo_zip:
            
                # Usamos la fuente por defecto de la librería PIL para no complicarnos con rutas
                fuente_texto = ImageFont.load_default()
            
                for indice, fila in alumnos.iterrows():
                nombre_alumno = fila['Nombre']
                nombre_curso = fila['Curso']
                cantidad_horas = str(fila['Horas'])
                
                    # Abrimos la imagen que subió el usuario
                    certificado = Image.open(imagen_base)
                    dibujo = ImageDraw.Draw(certificado)
                
                    # Escribimos los textos
                    dibujo.text((400, 250), nombre_alumno, fill="black", anchor="mm", font=fuente_texto)
                    dibujo.text((400, 320), f"Curso: {nombre_curso}", fill="black", anchor="mm", font=fuente_texto)
                    dibujo.text((400, 380), f"Duración: {cantidad_horas} hrs", fill="black", anchor="mm", font=fuente_texto)
                
                    # Convertimos a PDF y lo guardamos en una memoria temporal
                    certificado_pdf = certificado.convert('RGB')
                    buffer_pdf = io.BytesIO()
                    certificado_pdf.save(buffer_pdf, format="PDF")
                
                    # Metemos ese PDF dentro de nuestro archivo ZIP
                    archivo_zip.writestr(f"Certificado_{nombre_alumno}.pdf", buffer_pdf.getvalue())
        
            # Lanzamos globos de celebración en la pantalla
            st.balloons()
        
            # 4. Botón final para que el colega descargue su ZIP con todos los certificados
            st.download_button(
                label="⬇️ Descargar todos los certificados (.zip)",
                data=buffer_zip.getvalue(),
                file_name="Certificados_Generados.zip",
                mime="application/zip"
        )
