# -*- coding: utf-8 -*-
"""
╔════════════════════════════════════════════════════════════════╗
║   PRISMAS LÍRICOS - Aplicación Web Completa                   ║
║   Jesús Ignacio Guerra Figueroa                               ║
╚════════════════════════════════════════════════════════════════╝
"""

import json
import os
import streamlit as st
import re
import asyncio
import tempfile
from fpdf import FPDF

# ═══════════════════════════════════════════════════════
# CONFIGURACIÓN INICIAL
# ═══════════════════════════════════════════════════════

st.set_page_config(
    page_title="Prismas Líricos - Jesús Ignacio Guerra Figueroa",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&family=EB+Garamond:ital@0;1&display=swap');
    
    .stApp {
        background: #f5f1e8;
    }
    
    .main-title {
        font-family: 'Cormorant Garamond', serif;
        font-size: 3.5em;
        color: #4a2c17;
        text-align: center;
        margin-bottom: 0.2em;
        font-weight: 600;
        letter-spacing: 0.05em;
    }
    
    .subtitle {
        font-family: 'EB Garamond', serif;
        font-size: 1.5em;
        color: #6b4423;
        text-align: center;
        font-style: italic;
        margin-bottom: 2em;
    }
    
    .poem-container {
        background: rgba(255, 253, 247, 0.95);
        padding: 3em 2em;
        border-radius: 10px;
        border-left: 6px solid #8b6f47;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin: 1em 0;
    }
    
    .poem-title {
        font-family: 'Cormorant Garamond', serif;
        font-size: 2.2em;
        color: #4a2c17;
        text-align: center;
        margin-bottom: 0.5em;
        font-weight: 600;
        letter-spacing: 0.05em;
    }
    
    .poem-author {
        font-family: 'EB Garamond', serif;
        font-style: italic;
        color: #6b4423;
        text-align: center;
        margin-bottom: 2em;
        font-size: 1.1em;
    }
    
    .poem-content {
        font-family: 'EB Garamond', serif;
        font-size: 1.3em;
        line-height: 2.2;
        color: #2c1810;
        white-space: pre-wrap;
        text-align: left;
        margin: 0 auto;
        max-width: 800px;
    }
    
    .audio-container {
        background: #f0e6d2;
        padding: 1.5em;
        border-radius: 8px;
        margin: 2em 0;
        text-align: center;
        border: 2px solid #d4c4b0;
    }
    
    .homenaje {
        font-family: 'EB Garamond', serif;
        font-style: italic;
        color: #8b4513;
        text-align: center;
        font-size: 1.1em;
        margin: 1em 0;
    }
    
    .stButton>button {
        background-color: #8b6f47;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.7em 2em;
        font-family: 'EB Garamond', serif;
        font-size: 1.1em;
        width: 100%;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #6b4423;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Estilo para el reproductor flotante */
    .floating-player {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 9999;
        background: rgba(255, 253, 247, 0.97);
        padding: 8px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        border: 2px solid #8b6f47;
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# DICCIONARIO DE CANCIONES
# ═══════════════════════════════════════════════════════

CANCIONES = {
    "Romance Anónimo - Gonza Nico": "https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/tracks/soundcloud%253Atracks%253A1882653678&color=%238b6f47&auto_play=false&hide_related=true&show_comments=false&show_user=false&show_reposts=false&show_teaser=false",
    "Concierto de Aranjuez - Adagio": "",
    "Asturias (Leyenda) - Albéniz": "",
    "Nocturno Op. 9 No. 2 - Chopin": "",
    "Clair de Lune - Debussy": "",
    "Recuerdos de la Alhambra - Tárrega": "",
}


# ═══════════════════════════════════════════════════════
# REPRODUCTOR FLOTANTE (VISIBLE)
# ═══════════════════════════════════════════════════════

def reproductor_flotante():
    """Reproductor de música flotante visible en la esquina inferior derecha."""
    cancion_url = st.session_state.get('cancion_url', CANCIONES["Romance Anónimo - Gonza Nico"])
    
    html_flotante = f"""
    <div class="floating-player">
        <div style="font-size: 10px; color: #8b6f47; margin-bottom: 5px; font-weight: bold;">🎵 Música de Fondo</div>
        <iframe width="280" height="60" scrolling="no" frameborder="no" 
                allow="autoplay" 
                src="{cancion_url}">
        </iframe>
    </div>
    """
    st.components.v1.html(html_flotante, height=90)


# ═══════════════════════════════════════════════════════
# FUNCIONES DE AUDIO
# ═══════════════════════════════════════════════════════

@st.cache_resource
def generar_audio_poema(texto, voz="es-ES-HelenaNeural", rate="-15%"):
    """Genera audio de un poema usando Edge-TTS."""
    try:
        import edge_tts
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            archivo_temp = tmp_file.name
        
        async def generar():
            communicate = edge_tts.Communicate(texto, voz, rate=rate)
            await communicate.save(archivo_temp)
        
        asyncio.run(generar())
        
        return archivo_temp
    
    except Exception as e:
        st.error(f"Error al generar audio: {e}")
        return None


def limpiar_texto_para_audio(texto):
    """Limpia el texto para mejor pronunciación."""
    texto = re.sub(r'[*═╔╗╚╝║┌┐└┘├┤┬┴┼─│]', '', texto)
    texto = texto.replace('...', ', ')
    texto = texto.replace('....', ', ')
    lineas = texto.split('\n')
    lineas_limpias = [re.sub(r'\s+', ' ', linea).strip() for linea in lineas]
    texto = '\n'.join(lineas_limpias)
    return texto.strip()


# ═══════════════════════════════════════════════════════
# FUNCIÓN PARA LIMPIAR CARACTERES EN PDF
# ═══════════════════════════════════════════════════════

def limpiar_caracteres(texto):
    """Reemplaza caracteres Unicode problemáticos con equivalentes ASCII."""
    reemplazos = {
        '\u2014': '-', '\u2013': '-', '\u2018': "'", '\u2019': "'",
        '\u201c': '"', '\u201d': '"', '\u2026': '...', '\u00a0': ' ',
        '\u2022': '*', '\u2021': '+', '\u00b0': 'o',
        '\u00e1': 'a', '\u00e9': 'e', '\u00ed': 'i', '\u00f3': 'o',
        '\u00fa': 'u', '\u00f1': 'n', '\u00c1': 'A', '\u00c9': 'E',
        '\u00cd': 'I', '\u00d3': 'O', '\u00da': 'U', '\u00d1': 'N',
    }
    for char, replacement in reemplazos.items():
        texto = texto.replace(char, replacement)
    return texto


# ═══════════════════════════════════════════════════════
# FUNCIÓN PARA GENERAR PDF DE UN POEMA
# ═══════════════════════════════════════════════════════

def generar_pdf_poema(poema):
    """Genera un PDF con el formato visual exacto del libro."""
    
    class PDFPoema(FPDF):
        def header(self):
            self.set_font('Times', 'I', 9)
            self.set_text_color(120, 120, 120)
            self.cell(0, 10, 'Prismas Líricos - Jesús Ignacio Guerra Figueroa', 0, 1, 'C')
            self.ln(5)
        
        def footer(self):
            self.set_y(-15)
            self.set_font('Times', 'I', 9)
            self.set_text_color(150, 150, 150)
            self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')
    
    pdf = PDFPoema()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=25)
    
    pdf.ln(20)
    pdf.set_font('Times', 'B', 18)
    pdf.set_text_color(40, 40, 40)
    titulo = limpiar_caracteres(poema['titulo'].strip().upper())
    pdf.multi_cell(0, 10, titulo, 0, 'C')
    pdf.ln(5)
    
    pdf.set_font('Times', 'I', 11)
    pdf.set_text_color(100, 100, 100)
    autor = limpiar_caracteres(poema.get('autor', 'Jesús Ignacio Guerra Figueroa').strip())
    año = limpiar_caracteres(poema.get('año', '').strip())
    
    if año:
        pdf.cell(0, 8, f'{autor} - {año}', 0, 1, 'C')
    else:
        pdf.cell(0, 8, autor, 0, 1, 'C')
    
    pdf.ln(15)
    
    pdf.set_draw_color(180, 180, 180)
    pdf.set_line_width(0.3)
    x_center = 105
    pdf.line(x_center - 40, pdf.get_y(), x_center + 40, pdf.get_y())
    pdf.ln(15)
    
    pdf.set_font('Times', '', 12)
    pdf.set_text_color(30, 30, 30)
    
    lineas = poema['contenido'].strip().split('\n')
    
    while lineas and not lineas[0].strip():
        lineas.pop(0)
    while lineas and not lineas[-1].strip():
        lineas.pop()
    
    for linea in lineas:
        linea_limpia = limpiar_caracteres(linea.strip())
        
        if not linea_limpia:
            pdf.ln(8)
        else:
            espacios_iniciales = len(linea) - len(linea.lstrip())
            
            if espacios_iniciales > 0:
                indentacion = min(espacios_iniciales * 1.5, 35)
                pdf.set_x(30 + indentacion)
                pdf.multi_cell(150, 7, linea_limpia, 0, 'L')
            else:
                pdf.multi_cell(0, 7, linea_limpia, 0, 'C')
            
            pdf.ln(1)
    
    pdf.ln(15)
    pdf.set_draw_color(180, 180, 180)
    pdf.line(x_center - 40, pdf.get_y(), x_center + 40, pdf.get_y())
    pdf.ln(8)
    
    pdf.set_font('Times', 'I', 9)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 6, 'Homenaje a Victoria Rodríguez de Guerra (1939-1991)', 0, 1, 'C')
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        archivo_pdf = tmp_file.name
    
    pdf.output(archivo_pdf)
    
    return archivo_pdf


# ═══════════════════════════════════════════════════════
# CARGA DE DATOS
# ═══════════════════════════════════════════════════════

@st.cache_data
def cargar_libro():
    """Carga el libro completo desde JSON."""
    with open("prismas_liricos_completo.json", 'r', encoding='utf-8') as f:
        return json.load(f)


def limpiar_texto(texto):
    """Elimina tildes para búsqueda."""
    texto = texto.lower()
    reemplazos = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ñ': 'n'}
    for o, r in reemplazos.items():
        texto = texto.replace(o, r)
    return texto


def formatear_versos(contenido):
    """Formatea el contenido preservando los saltos de línea."""
    lineas = contenido.strip().split('\n')
    while lineas and not lineas[0].strip():
        lineas.pop(0)
    while lineas and not lineas[-1].strip():
        lineas.pop()
    return '\n'.join(lineas)


# ═══════════════════════════════════════════════════════
# FUNCIÓN DE GALERÍA
# ═══════════════════════════════════════════════════════

def mostrar_galeria():
    """Muestra la galería de fotos del libro."""
    st.markdown("## 📸 Galería de Recuerdos")
    st.markdown("---")
    
    url_base = "https://raw.githubusercontent.com/faustotoasaromo-source/prismas-liricos/main/"
    
    st.markdown("### 📖 Portada del Libro")
    try:
        st.image(f"{url_base}Portada.jpg", caption="Prismas Líricos - Segunda Edición (1996)", width=400)
    except:
        st.warning("📷 Portada no disponible.")
    
    st.markdown("---")
    
    st.markdown("### 📖 Contraportada")
    try:
        st.image(f"{url_base}Contra%20portada.jpg", caption="Contraportada del libro", width=400)
    except:
        st.warning("📷 Contraportada no disponible.")
    
    st.markdown("---")
    
    st.markdown("### 👨‍👩‍👧‍👦 Recuerdos Familiares")
    col1, col2 = st.columns(2)
    with col1:
        try: st.image(f"{url_base}Familia1.jpg", caption="Recuerdo familiar 1", width=350)
        except: st.info("📷 Familia1.jpg no disponible")
    with col2:
        try: st.image(f"{url_base}Familia2.jpg", caption="Recuerdo familiar 2", width=350)
        except: st.info("📷 Familia2.jpg no disponible")
    
    st.markdown("---")
    
    st.markdown("### 📸 Más Recuerdos")
    col1, col2, col3 = st.columns(3)
    with col1:
        try: st.image(f"{url_base}Familia%203.jpg", caption="Recuerdo 3", width=250)
        except: st.info("📷 Familia 3.jpg no disponible")
    with col2:
        try: st.image(f"{url_base}Familia%204.jpg", caption="Recuerdo 4", width=250)
        except: st.info("📷 Familia 4.jpg no disponible")
    with col3:
        try: st.image(f"{url_base}Familia%205.jpg", caption="Recuerdo 5", width=250)
        except: st.info("📷 Familia 5.jpg no disponible")
    
    st.markdown("---")
    try: st.image(f"{url_base}Familia%206.jpg", caption="Recuerdo familiar 6", width=350)
    except: st.info("📷 Familia 6.jpg no disponible")
    
    st.markdown("---")
    st.markdown("*Homenaje a Victoria Rodríguez de Guerra (1939-1991)*")


# ═══════════════════════════════════════════════════════
# FUNCIÓN DE MÚSICA
# ═══════════════════════════════════════════════════════

def mostrar_musica():
    """Muestra la sección de música de fondo."""
    st.markdown("## 🎵 Música de Fondo")
    st.markdown("---")
    
    st.markdown("""
    ### 🎸 Romance Anónimo (Romance de Amor)
    
    Esta hermosa y atemporal pieza de guitarra clásica acompaña la lectura de los poemas, 
    evocando el amor eterno, la nostalgia y la serenidad presentes en *Prismas Líricos*.
    
    *💡 Tip: También puedes usar el reproductor flotante en la esquina inferior derecha 
    para escuchar música mientras navegas por toda la aplicación.*
    """)
    
    st.markdown("---")
    
    cancion_url = st.session_state.get('cancion_url', CANCIONES["Romance Anónimo - Gonza Nico"])
    cancion_nombre = st.session_state.get('cancion_nombre', "Romance Anónimo - Gonza Nico")
    
    st.markdown(f"### 🎧 Reproduciendo: **{cancion_nombre}**")
    
    soundcloud_html = f"""
    <iframe width="100%" height="300" scrolling="no" frameborder="no" allow="autoplay; encrypted-media" src="{cancion_url}"></iframe>
    """
    
    st.components.v1.html(soundcloud_html, height=350)
    
    st.markdown("---")
    st.markdown("*\"La música es el lenguaje del espíritu. Abre el secreto de la vida, trayendo paz, abolida la discordia.\" - Kahlil Gibran*")


# ═══════════════════════════════════════════════════════
# FUNCIÓN DE INICIO
# ═══════════════════════════════════════════════════════

def mostrar_inicio(libro):
    """Muestra la página de inicio con la imagen de peonías centrada."""
    
    # Título principal
    st.markdown("""
    <div style="text-align: center; padding-top: 0.5em;">
        <h1 style="font-family: 'Cormorant Garamond', serif; 
                   font-size: 3.5em; 
                   color: #4a2c17; 
                   margin-bottom: 0.1em;
                   font-weight: 600;
                   letter-spacing: 0.05em;">
            PRISMAS LÍRICOS
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Nombre del autor
    st.markdown("""
    <div style="text-align: center; margin-bottom: 1em;">
        <p style="font-family: 'EB Garamond', serif; 
                  font-size: 1.5em; 
                  color: #6b4423; 
                  font-style: italic;
                  margin: 0;">
            Jesús Ignacio Guerra Figueroa
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Imagen centrada usando columnas
    col1, col2, col3 = st.columns([1.5, 2, 1])
    with col2:
        st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
        st.image("Peonias.jpg", width=280)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Homenaje a Victoria
    st.markdown("""
    <div style="text-align: center; margin-top: 1em;">
        <p style="font-family: 'EB Garamond', serif; 
                  font-size: 1.2em; 
                  color: #8b4513; 
                  font-style: italic;
                  margin: 0;">
            Victoria Rodríguez de Guerra (1939-1991)
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Línea decorativa
    st.markdown("""
    <hr style="border: none; 
               height: 1px; 
               background: linear-gradient(to right, transparent, #8b6f47, transparent);
               margin: 2em 0;">
    """, unsafe_allow_html=True)
    
    # Contenido de bienvenida
    st.markdown("## 🌹 Bienvenido a Prismas Líricos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### Sobre la Obra
        
        **Prismas Líricos** es una obra poética escrita por **Jesús Ignacio Guerra Figueroa**, 
        un homenaje póstumo a su esposa **Victoria Rodríguez de Guerra** (1939-1991).
        
        Esta segunda edición, publicada en 1996 en San Juan de Pasto, Nariño, 
        recoge más de cinco décadas de creación poética (1939-1996), incluyendo:
        
        - 📖 Prosa filosófica sobre la vida, la muerte y la reencarnación
        - 🌹 Más de 200 poemas líricos
        - 👨‍👩‍👧‍👦 Versos de hijos y nietos
        - 📜 El Álbum de Recuerdos de toda una vida de amor
        - 🕊️ La Oración Fúnebre y los Cantos finales
        """)
    
    with col2:
        st.markdown("""
        ### 🎙️ Lector de Voz
        
        Esta aplicación incluye un **lector de voz neuronal** que puede leer 
        cualquier poema del libro en voz alta.
        
        **Características:**
        - ✅ 6 voces en español de alta calidad
        - ✅ Velocidad ajustable
        - ✅ Entonación natural
        - ✅ Descarga de audios MP3
        - ✅ Descarga de poemas en PDF (formato del libro)
        - ✅ Música de fondo (guitarra clásica)
        - ✅ Formato de versos preservado
        
        **Cómo usar:**
        1. Selecciona una voz en el menú lateral
        2. Ajusta la velocidad de lectura
        3. Navega a cualquier poema
        4. Haz clic en "🔊 Generar y reproducir audio" o "📥 Generar PDF"
        5. **La música de fondo sigue sonando mientras escuchas el poema**
        """)
        
        st.markdown("---")
        st.markdown("### 💡 Consejo")
        st.info("""
        Para una experiencia óptima, te recomendamos:
        - **Voz**: Helena (España - Femenina)
        - **Velocidad**: -15% (poética)
        - **Ambiente**: Lugar tranquilo para apreciar la poesía
        - **Música**: Activa el reproductor flotante para escuchar música mientras lees
        """)


# ═══════════════════════════════════════════════════════
# FUNCIONES DE VISUALIZACIÓN
# ═══════════════════════════════════════════════════════

def mostrar_poema(poema):
    """Muestra un poema individual con formato de versos, audio y PDF."""
    contenido_formateado = formatear_versos(poema['contenido'])
    
    st.markdown(f"""
    <div class="poem-container">
        <div class="poem-title">{poema['titulo']}</div>
        <div class="poem-author">
            {poema.get('autor', 'Jesús Ignacio Guerra Figueroa')} — {poema.get('año', '')}
        </div>
        <div class="poem-content">{contenido_formateado}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🎙️ Escuchar este poema")
    st.info("💡 **Tip:** La música de fondo seguirá sonando mientras escuchas el poema. Puedes pausarla desde el reproductor flotante si lo deseas.")
    
    texto_audio = f"{poema['titulo']}. "
    if poema.get('autor'):
        texto_audio += f"De {poema['autor']}. "
    if poema.get('año'):
        texto_audio += f"Año {poema['año']}. "
    
    texto_audio += ". . . "
    texto_audio += limpiar_texto_para_audio(poema['contenido'])
    
    if st.button("🔊 Generar y reproducir audio", key=f"audio_{poema['titulo']}"):
        with st.spinner("Generando audio con voz neuronal..."):
            voz_id = st.session_state.get('voz_id', 'es-ES-HelenaNeural')
            velocidad = st.session_state.get('velocidad', '-15%')
            
            archivo_audio = generar_audio_poema(texto_audio, voz_id, velocidad)
            
            if archivo_audio:
                st.success("✅ Audio generado exitosamente")
                st.markdown('<div class="audio-container">', unsafe_allow_html=True)
                st.audio(archivo_audio, format='audio/mp3')
                st.markdown('</div>', unsafe_allow_html=True)
                
                with open(archivo_audio, 'rb') as f:
                    st.download_button(
                        label="💾 Descargar MP3",
                        data=f,
                        file_name=f"{poema['titulo']}.mp3",
                        mime="audio/mpeg"
                    )
            else:
                st.error("❌ No se pudo generar el audio")
    
    st.markdown("---")
    st.markdown("### 📄 Descargar en PDF")
    st.markdown("*Imprime este poema con el formato exacto del libro original.*")
    
    if st.button("📥 Generar PDF del poema", key=f"pdf_{poema['titulo']}"):
        with st.spinner("Generando PDF con formato del libro..."):
            try:
                archivo_pdf = generar_pdf_poema(poema)
                
                st.success("✅ PDF generado exitosamente con el formato del libro")
                
                with open(archivo_pdf, 'rb') as f:
                    st.download_button(
                        label="📥 Descargar PDF",
                        data=f,
                        file_name=f"{poema['titulo']}.pdf",
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"❌ Error al generar el PDF: {e}")


def mostrar_busqueda(libro):
    """Muestra la interfaz de búsqueda."""
    st.markdown("## 🔍 Búsqueda Avanzada")
    
    tipo_busqueda = st.radio(
        "Tipo de búsqueda:",
        ["Por palabra en contenido", "Por título", "Por autor", "Por año"],
        horizontal=True
    )
    
    termino = st.text_input("Ingresa tu búsqueda:")
    
    if termino:
        resultados = []
        termino_limpio = limpiar_texto(termino)
        
        for poema in libro['poemas']:
            if tipo_busqueda == "Por palabra en contenido":
                texto = poema['titulo'] + " " + poema['contenido']
                if termino_limpio in limpiar_texto(texto):
                    resultados.append(poema)
            elif tipo_busqueda == "Por título":
                if termino_limpio in limpiar_texto(poema['titulo']):
                    resultados.append(poema)
            elif tipo_busqueda == "Por autor":
                if termino_limpio in limpiar_texto(poema.get('autor', '')):
                    resultados.append(poema)
            elif tipo_busqueda == "Por año":
                if termino in poema.get('año', ''):
                    resultados.append(poema)
        
        st.markdown(f"### 📊 {len(resultados)} resultado(s) encontrado(s)")
        
        if resultados:
            poema_seleccionado = st.selectbox(
                "Selecciona un poema:",
                [f"{p['titulo']} ({p.get('año', '')})" for p in resultados]
            )
            
            indice = [f"{p['titulo']} ({p.get('año', '')})" for p in resultados].index(poema_seleccionado)
            mostrar_poema(resultados[indice])


def mostrar_por_seccion(libro):
    """Muestra poemas agrupados por sección."""
    st.markdown("## 📚 Explorar por Sección")
    
    secciones = {}
    for poema in libro['poemas']:
        seccion = poema.get('seccion', 'Sin sección')
        if seccion not in secciones:
            secciones[seccion] = []
        secciones[seccion].append(poema)
    
    seccion_elegida = st.selectbox("Elige una sección:", list(secciones.keys()))
    
    st.markdown(f"### 📖 {seccion_elegida} ({len(secciones[seccion_elegida])} textos)")
    
    poema_elegido = st.selectbox(
        "Selecciona un texto:",
        [p['titulo'] for p in secciones[seccion_elegida]]
    )
    
    poema = next(p for p in secciones[seccion_elegida] if p['titulo'] == poema_elegido)
    mostrar_poema(poema)


def mostrar_por_tema(libro):
    """Muestra poemas agrupados por tema."""
    st.markdown("## 🏷️ Explorar por Tema")
    
    temas_unicos = set()
    for poema in libro['poemas']:
        temas_unicos.update(poema.get('temas', []))
    
    temas_ordenados = sorted(temas_unicos)
    
    tema_elegido = st.selectbox("Elige un tema:", temas_ordenados)
    
    poemas_filtrados = [
        p for p in libro['poemas']
        if tema_elegido in p.get('temas', [])
    ]
    
    st.markdown(f"### 📖 {len(poemas_filtrados)} poema(s) con el tema: **{tema_elegido}**")
    
    if poemas_filtrados:
        poema_elegido = st.selectbox(
            "Selecciona un poema:",
            [f"{p['titulo']} ({p.get('año', '')})" for p in poemas_filtrados]
        )
        
        indice = [f"{p['titulo']} ({p.get('año', '')})" for p in poemas_filtrados].index(poema_elegido)
        mostrar_poema(poemas_filtrados[indice])


def mostrar_todos(libro):
    """Muestra todos los poemas."""
    st.markdown("## 📜 Todos los Poemas")
    
    poema_elegido = st.selectbox(
        "Selecciona un poema:",
        [f"{p['titulo']} — {p.get('autor', 'Jesús Ignacio Guerra Figueroa')} ({p.get('año', '')})" 
         for p in libro['poemas']]
    )
    
    titulo_seleccionado = poema_elegido.split(' — ')[0]
    poema = next((p for p in libro['poemas'] if p['titulo'] == titulo_seleccionado), None)
    
    if poema:
        mostrar_poema(poema)


def mostrar_estadisticas(libro):
    """Muestra estadísticas del libro."""
    st.markdown("## 📊 Estadísticas del Libro")
    
    secciones = {}
    autores = {}
    años = {}
    temas = {}
    
    for poema in libro['poemas']:
        seccion = poema.get('seccion', 'Sin sección')
        secciones[seccion] = secciones.get(seccion, 0) + 1
        
        autor = poema.get('autor', 'Desconocido')
        autores[autor] = autores.get(autor, 0) + 1
        
        año = poema.get('año', 'Sin año')
        años[año] = años.get(año, 0) + 1
        
        for tema in poema.get('temas', []):
            temas[tema] = temas.get(tema, 0) + 1
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📂 Por Sección")
        for seccion, cantidad in sorted(secciones.items(), key=lambda x: x[1], reverse=True):
            st.markdown(f"- **{seccion}**: {cantidad}")
    
    with col2:
        st.markdown("### ✍️ Por Autor")
        for autor, cantidad in sorted(autores.items(), key=lambda x: x[1], reverse=True):
            st.markdown(f"- **{autor}**: {cantidad}")
    
    st.markdown("### 🏷️ Temas Más Frecuentes (Top 20)")
    temas_top = sorted(temas.items(), key=lambda x: x[1], reverse=True)[:20]
    
    import pandas as pd
    df = pd.DataFrame(temas_top, columns=['Tema', 'Frecuencia'])
    st.bar_chart(df.set_index('Tema'))
    
    st.markdown("### 📅 Distribución por Año")
    años_ordenados = {k: v for k, v in sorted(años.items()) if k.isdigit()}
    df_años = pd.DataFrame(list(años_ordenados.items()), columns=['Año', 'Textos'])
    st.line_chart(df_años.set_index('Año'))


# ═══════════════════════════════════════════════════════
# FUNCIÓN DE DESCARGA DEL LIBRO COMPLETO (OCULTA)
# ═══════════════════════════════════════════════════════

def mostrar_descarga_libro():
    """Permite descargar el libro completo en PDF (archivo pre-elaborado)."""
    st.markdown("## 📖 Descargar Libro Completo")
    st.markdown("---")
    
    st.markdown("""
    ### Prismas Líricos - Obra Completa
    
    Descarga la obra completa de **Jesús Ignacio Guerra Figueroa** en formato PDF.
    
    **Contenido:**
    - 📖 Más de 200 poemas con ortografía corregida
    - 👨‍👩‍👧‍👦 Álbum de Recuerdos
    - 🎵 Prólogos, epílogos y dedicatorias
    - ✨ Formato idéntico al libro original
    
    **Edición:** Segunda Edición (1996)  
    **San Juan de Pasto, Nariño, Colombia**
    """)
    
    st.markdown("---")
    
    nombre_archivo = "Prismas_Liricos_Corregido.pdf"
    
    try:
        with open(nombre_archivo, "rb") as pdf_file:
            pdf_bytes = pdf_file.read()
        
        st.success("✅ El libro está disponible para descarga")
        
        st.download_button(
            label="📥 Descargar Libro Completo (PDF)",
            data=pdf_bytes,
            file_name="Prismas_Liricos_Completo.pdf",
            mime="application/pdf",
            key="descargar_libro_completo_pdf"
        )
        
        st.markdown("---")
        st.markdown("*Homenaje a Victoria Rodríguez de Guerra (1939-1991)*")
        
    except FileNotFoundError:
        st.warning("⚠️ El libro completo estará disponible próximamente.")
        st.info("💡 El autor está preparando el PDF con el formato exacto del libro original y la ortografía corregida.")


# ═══════════════════════════════════════════════════════
# FUNCIÓN PRINCIPAL
# ═══════════════════════════════════════════════════════

def main():
    """Función principal de la aplicación."""
    
    # Inicializar sesión para la música
    if 'cancion_url' not in st.session_state:
        st.session_state.cancion_url = CANCIONES["Romance Anónimo - Gonza Nico"]
        st.session_state.cancion_nombre = "Romance Anónimo - Gonza Nico"
    
    # Cargar datos
    try:
        libro = cargar_libro()
    except FileNotFoundError:
        st.error("❌ No se encontró 'prismas_liricos_completo.json'")
        st.info("Asegúrate de que el archivo esté en la misma carpeta que app.py")
        return
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 📖 Navegación")
        
        modo = st.radio(
            "¿Cómo deseas explorar?",
            ["🏠 Inicio", "🔍 Buscar", "📚 Por Sección", "🏷️ Por Tema", "📜 Todos los poemas", "📊 Estadísticas", "📸 Galería", "🎵 Música"],
            index=0
        )
        
        st.markdown("---")
        
        # Selector de música
        st.markdown("### 🎵 Música de Fondo")
        
        cancion_elegida = st.selectbox(
            "Elige una canción:",
            list(CANCIONES.keys()),
            index=0,
            help="Selecciona la música que sonará de fondo"
        )
        
        if cancion_elegida and CANCIONES[cancion_elegida]:
            st.session_state.cancion_url = CANCIONES[cancion_elegida]
            st.session_state.cancion_nombre = cancion_elegida
        elif cancion_elegida and not CANCIONES[cancion_elegida]:
            st.info(f"⏳ '{cancion_elegida}' estará disponible próximamente")
        
        st.markdown("---")
        
        # Configuración de Voz
        st.markdown("### 🎙️ Configuración de Voz")
        
        voz_seleccionada = st.selectbox(
            "Elige una voz:",
            [
                "Helena (España - Femenina)",
                "Alvaro (España - Masculina)",
                "Elvira (España - Femenina)",
                "Dalia (México - Femenina)",
                "Jorge (México - Masculina)",
                "Lupe (México - Femenina)"
            ],
            index=0
        )
        
        voces_map = {
            "Helena (España - Femenina)": "es-ES-HelenaNeural",
            "Alvaro (España - Masculina)": "es-ES-AlvaroNeural",
            "Elvira (España - Femenina)": "es-ES-ElviraNeural",
            "Dalia (México - Femenina)": "es-MX-DaliaNeural",
            "Jorge (México - Masculina)": "es-MX-JorgeNeural",
            "Lupe (México - Femenina)": "es-MX-LupeNeural",
        }
        
        st.session_state.voz_id = voces_map[voz_seleccionada]
        
        velocidad = st.slider(
            "Velocidad de lectura:",
            -30, 10, -15,
            format="%d%%",
            help="-15% es ideal para poesía"
        )
        
        st.session_state.velocidad = f"{velocidad}%"
        
        st.markdown("---")
        st.markdown("### ℹ️ Información")
        st.markdown(f"**Total de textos:** {len(libro['poemas'])}")
        st.markdown(f"**Edición:** {libro.get('edicion', 'Segunda Edición')}")
        st.markdown(f"**Año:** {libro.get('anio_publicacion', '1996')}")
    
    # Contenido principal
    if modo == "🏠 Inicio":
        mostrar_inicio(libro)
    
    else:
        st.markdown('<div class="main-title">PRISMAS LÍRICOS</div>', unsafe_allow_html=True)
        st.markdown('<div class="subtitle">Jesús Ignacio Guerra Figueroa</div>', unsafe_allow_html=True)
        st.markdown("---")
        
        if modo == "🔍 Buscar":
            mostrar_busqueda(libro)
        elif modo == "📚 Por Sección":
            mostrar_por_seccion(libro)
        elif modo == "🏷️ Por Tema":
            mostrar_por_tema(libro)
        elif modo == "📜 Todos los poemas":
            mostrar_todos(libro)
        elif modo == "📊 Estadísticas":
            mostrar_estadisticas(libro)
        elif modo == "📸 Galería":
            mostrar_galeria()
        elif modo == "🎵 Música":
            mostrar_musica()
    
    # ═══════════════════════════════════════════════════
    # REPRODUCTOR FLOTANTE (SIEMPRE VISIBLE)
    # ═══════════════════════════════════════════════════
    reproductor_flotante()


if __name__ == "__main__":
    main()
