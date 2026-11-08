# -*- coding: utf-8 -*-
"""
╔════════════════════════════════════════════════════════════════╗
║   PRISMAS LÍRICOS - Aplicación Web Completa                   ║
║   Jesús Ignacio Guerra Figueroa                               ║
╚════════════════════════════════════════════════════════════════╝
"""

import json
import os
import glob
import streamlit as st
import re
import asyncio
import hashlib
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
    
    .stApp { background: #f5f1e8; }
    .main-title { font-family: 'Cormorant Garamond', serif; font-size: 3.5em; color: #4a2c17; text-align: center; margin-bottom: 0.2em; font-weight: 600; letter-spacing: 0.05em; }
    .subtitle { font-family: 'EB Garamond', serif; font-size: 1.5em; color: #6b4423; text-align: center; font-style: italic; margin-bottom: 2em; }
    .poem-container { background: rgba(255, 253, 247, 0.95); padding: 3em 2em; border-radius: 10px; border-left: 6px solid #8b6f47; box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin: 1em 0; }
    .poem-title { font-family: 'Cormorant Garamond', serif; font-size: 2.2em; color: #4a2c17; text-align: center; margin-bottom: 0.5em; font-weight: 600; letter-spacing: 0.05em; }
    .poem-author { font-family: 'EB Garamond', serif; font-style: italic; color: #6b4423; text-align: center; margin-bottom: 2em; font-size: 1.1em; }
    .poem-content { font-family: 'EB Garamond', serif; font-size: 1.3em; line-height: 2.2; color: #2c1810; white-space: pre-wrap; text-align: left; margin: 0 auto; max-width: 800px; }
    .audio-container { background: #f0e6d2; padding: 1.5em; border-radius: 8px; margin: 2em 0; text-align: center; border: 2px solid #d4c4b0; }
    .stButton>button { background-color: #8b6f47; color: white; border: none; border-radius: 5px; padding: 0.7em 2em; font-family: 'EB Garamond', serif; font-size: 1.1em; width: 100%; transition: all 0.3s ease; }
    .stButton>button:hover { background-color: #6b4423; transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.2); }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# DICCIONARIO DE CANCIONES
# ═══════════════════════════════════════════════════════

CANCIONES = {
    "Romance Anónimo - Gonza Nico": "https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/tracks/1882653678&color=%238b6f47&auto_play=false&hide_related=true&show_comments=false&show_user=false&show_reposts=false&show_teaser=false",
    "Asturias (Leyenda) - Bob Culbertson": "https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/tracks/41253731&color=%238b6f47&auto_play=false&hide_related=true&show_comments=false&show_user=false&show_reposts=false&show_teaser=false",
    "Nocturno Op. 9 No. 2 - Chopin": "https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/tracks/155469656&color=%238b6f47&auto_play=false&hide_related=true&show_comments=false&show_user=false&show_reposts=false&show_teaser=false",
    "Clair de Lune - Debussy (Luiz Mallet)": "https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/tracks/46472531&color=%238b6f47&auto_play=false&hide_related=true&show_comments=false&show_user=false&show_reposts=false&show_teaser=false",
    "Recuerdos de la Alhambra - Tárrega (Adel Rouhnavaz)": "https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/tracks/68346177&color=%238b6f47&auto_play=false&hide_related=true&show_comments=false&show_user=false&show_reposts=false&show_teaser=false",
    "Concierto de Aranjuez - Adagio": "https://w.soundcloud.com/player/?url=https%3A//soundcloud.com/fhgitarre/adagio-concierto-de-aranjuez&color=%238b6f47&auto_play=false&hide_related=true&show_comments=false&show_user=false&show_reposts=false&show_teaser=false",
    "🌹 Pavane pour une infante défunte - Ravel (Classical)": "https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/tracks/155466346&color=%238b6f47&auto_play=false&hide_related=true&show_comments=false&show_user=false&show_reposts=false&show_teaser=false",
}

# ═══════════════════════════════════════════════════════
# FUNCIONES DE AUDIO CON CACHÉ
# ═══════════════════════════════════════════════════════

@st.cache_data(show_spinner="Generando o cargando audio...")
def generar_audio_poema(texto, voz="es-CO-SalomeNeural", rate="-15%", volumen="+0%"):
    hash_input = f"{texto}_{voz}_{rate}_{volumen}"
    hash_id = hashlib.md5(hash_input.encode('utf-8')).hexdigest()
    cache_dir = "audio_cache"
    if not os.path.exists(cache_dir): os.makedirs(cache_dir)
    archivo_mp3 = os.path.join(cache_dir, f"{hash_id}.mp3")
    if os.path.exists(archivo_mp3): return archivo_mp3
    try:
        import edge_tts
        async def generar():
            communicate = edge_tts.Communicate(texto, voz, rate=rate, volume=volumen)
            await communicate.save(archivo_mp3)
        asyncio.run(generar())
        return archivo_mp3
    except Exception as e:
        st.error(f"Error al generar audio: {e}")
        return None

def limpiar_texto_para_audio(texto):
    texto = re.sub(r'[*═╔╗╚╝║┌┐└┘├┤┬┴┼─│]', '', texto)
    texto = texto.replace('...', ', ')
    lineas = texto.split('\n')
    lineas_limpias = [re.sub(r'\s+', ' ', linea).strip() for linea in lineas]
    return '\n'.join(lineas_limpias).strip()

def limpiar_caracteres(texto):
    reemplazos = {'\u2014': '-', '\u2013': '-', '\u2018': "'", '\u2019': "'", '\u201c': '"', '\u201d': '"', '\u2026': '...', '\u00a0': ' ', '\u2022': '*', '\u2021': '+', '\u00b0': 'o', '\u00e1': 'a', '\u00e9': 'e', '\u00ed': 'i', '\u00f3': 'o', '\u00fa': 'u', '\u00f1': 'n', '\u00c1': 'A', '\u00c9': 'E', '\u00cd': 'I', '\u00d3': 'O', '\u00da': 'U', '\u00d1': 'N'}
    for char, replacement in reemplazos.items(): texto = texto.replace(char, replacement)
    return texto

def generar_pdf_poema(poema):
    class PDFPoema(FPDF):
        def header(self):
            self.set_font('Times', 'I', 9); self.set_text_color(120, 120, 120); self.cell(0, 10, 'Prismas Líricos - Jesús Ignacio Guerra Figueroa', 0, 1, 'C'); self.ln(5)
        def footer(self):
            self.set_y(-15); self.set_font('Times', 'I', 9); self.set_text_color(150, 150, 150); self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')
    pdf = PDFPoema(); pdf.add_page(); pdf.set_auto_page_break(auto=True, margin=25); pdf.ln(20)
    pdf.set_font('Times', 'B', 18); pdf.set_text_color(40, 40, 40); pdf.multi_cell(0, 10, limpiar_caracteres(poema['titulo'].strip().upper()), 0, 'C'); pdf.ln(5)
    pdf.set_font('Times', 'I', 11); pdf.set_text_color(100, 100, 100)
    autor = limpiar_caracteres(poema.get('autor', 'Jesús Ignacio Guerra Figueroa').strip())
    año = limpiar_caracteres(poema.get('año', '').strip())
    if año: pdf.cell(0, 8, f'{autor} - {año}', 0, 1, 'C')
    else: pdf.cell(0, 8, autor, 0, 1, 'C')
    pdf.ln(15); pdf.set_draw_color(180, 180, 180); pdf.set_line_width(0.3); pdf.line(65, pdf.get_y(), 145, pdf.get_y()); pdf.ln(15)
    pdf.set_font('Times', '', 12); pdf.set_text_color(30, 30, 30)
    for linea in poema['contenido'].strip().split('\n'):
        linea_limpia = limpiar_caracteres(linea.strip())
        if not linea_limpia: pdf.ln(8)
        else:
            espacios = len(linea) - len(linea.lstrip())
            if espacios > 0: pdf.set_x(30 + min(espacios * 1.5, 35)); pdf.multi_cell(150, 7, linea_limpia, 0, 'L')
            else: pdf.multi_cell(0, 7, linea_limpia, 0, 'C')
            pdf.ln(1)
    pdf.ln(15); pdf.line(65, pdf.get_y(), 145, pdf.get_y()); pdf.ln(8)
    pdf.set_font('Times', 'I', 9); pdf.set_text_color(120, 120, 120); pdf.cell(0, 6, 'Homenaje a Victoria Rodríguez de Guerra (1939-1991)', 0, 1, 'C')
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file: archivo_pdf = tmp_file.name
    pdf.output(archivo_pdf); return archivo_pdf

@st.cache_data
def cargar_libro():
    with open("prismas_liricos_completo.json", 'r', encoding='utf-8') as f: return json.load(f)

def limpiar_texto(texto):
    texto = texto.lower()
    for o, r in {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ñ': 'n'}.items(): texto = texto.replace(o, r)
    return texto

def formatear_versos(contenido):
    lineas = contenido.strip().split('\n')
    while lineas and not lineas[0].strip(): lineas.pop(0)
    while lineas and not lineas[-1].strip(): lineas.pop()
    return '\n'.join(lineas)

def mostrar_galeria():
    st.markdown("## 📸 Galería de Recuerdos\n---")
    url_base = "https://raw.githubusercontent.com/faustotoasaromo-source/prismas-liricos/main/"
    try: st.image(f"{url_base}Portada.jpg", caption="Prismas Líricos - Segunda Edición (1996)", width=400)
    except: st.warning("📷 Portada no disponible.")
    st.markdown("---")
    try: st.image(f"{url_base}Contra%20portada.jpg", caption="Contraportada del libro", width=400)
    except: st.warning("📷 Contraportada no disponible.")
    st.markdown("---\n### 👨‍👩‍👧‍👦 Recuerdos Familiares")
    col1, col2 = st.columns(2)
    with col1:
        try: st.image(f"{url_base}Familia1.jpg", caption="Recuerdo familiar 1", width=350)
        except: st.info("📷 No disponible")
    with col2:
        try: st.image(f"{url_base}Familia2.jpg", caption="Recuerdo familiar 2", width=350)
        except: st.info("📷 No disponible")
    st.markdown("---\n*Homenaje a Victoria Rodríguez de Guerra (1939-1991)*")

# ═══════════════════════════════════════════════════════
# MÚSICA CON API DE SOUNDCLOUD (VOLUMEN REAL)
# ═══════════════════════════════════════════════════════

def mostrar_musica():
    st.markdown("## 🎵 Música de Fondo\n---\n### 🎸 Selección Musical\n\nDisfruta de música clásica mientras lees los poemas.\n---")
    cancion_url = st.session_state.get('cancion_url', CANCIONES["Romance Anónimo - Gonza Nico"])
    cancion_nombre = st.session_state.get('cancion_nombre', "Romance Anónimo - Gonza Nico")
    volumen = st.session_state.get('volumen_musica', 40)
    
    st.markdown(f"### 🎧 Reproduciendo: **{cancion_nombre}**")
    
    volumen_slider = st.slider("🔊 Volumen de la música:", 0, 100, volumen, 5, key="slider_volumen_principal", help="Ajusta el volumen en tiempo real.")
    st.session_state.volumen_musica = volumen_slider
    
    # API REAL DE SOUNDCLOUD PARA CONTROLAR VOLUMEN
    sc_widget_code = f"""
    <iframe id="sc-player" width="100%" height="300" scrolling="no" frameborder="no" allow="autoplay" src="{cancion_url}"></iframe>
    <script src="https://w.soundcloud.com/player/api.js"></script>
    <script>
        var widgetIframe = document.getElementById('sc-player');
        var widget = SC.Widget(widgetIframe);
        widget.bind(SC.Widget.Events.READY, function() {{ widget.setVolume({volumen_slider}); }});
        widget.setVolume({volumen_slider});
    </script>
    """
    st.components.v1.html(sc_widget_code, height=350)
    st.markdown("---\n*\"La música es el lenguaje del espíritu...\" - Kahlil Gibran*")

def mostrar_inicio(libro):
    st.markdown("""<div style="text-align: center;"><h1 style="font-family: 'Cormorant Garamond', serif; font-size: 3.5em; color: #4a2c17;">PRISMAS LÍRICOS</h1><p style="font-family: 'EB Garamond', serif; font-size: 1.5em; color: #6b4423; font-style: italic;">Jesús Ignacio Guerra Figueroa</p></div>""", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1.5, 2, 1])
    with col2:
        st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
        try: st.image("Peonias.jpg", width=280)
        except: st.warning("📷 Imagen no disponible")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("""<div style="text-align: center; margin-top: 1em;"><p style="font-family: 'EB Garamond', serif; font-size: 1.2em; color: #8b4513; font-style: italic;">Victoria Rodríguez de Guerra (1939-1991)</p></div><hr style="border: none; height: 1px; background: linear-gradient(to right, transparent, #8b6f47, transparent); margin: 2em 0;">""", unsafe_allow_html=True)
    st.markdown("## 🌹 Bienvenido a Prismas Líricos")
    col1, col2 = st.columns(2)
    with col1: st.markdown("### Sobre la Obra\n\n**Prismas Líricos** es una obra poética escrita por **Jesús Ignacio Guerra Figueroa**, un homenaje póstumo a su esposa **Victoria Rodríguez de Guerra** (1939-1991).")
    with col2: st.markdown("### 🎙️ Lector de Voz\n\n- ✅ 7 piezas de música clásica\n- ✅ Voces de familiares (MP3/MP4)\n- ✅ Más de 25 voces neuronales\n- ✅ Descarga de MP3 y PDF")

# ═══════════════════════════════════════════════════════
# VISUALIZACIÓN DE POEMA (CON VOZ FAMILIAR Y VOLUMEN REAL)
# ═══════════════════════════════════════════════════════

def mostrar_poema(poema):
    contenido_formateado = formatear_versos(poema['contenido'])
    st.markdown(f"""<div class="poem-container"><div class="poem-title">{poema['titulo']}</div><div class="poem-author">{poema.get('autor', 'Jesús Ignacio Guerra Figueroa')} — {poema.get('año', '')}</div><div class="poem-content">{contenido_formateado}</div></div>""", unsafe_allow_html=True)
    
    st.markdown("---\n### 🎙️ Escuchar este poema")
    carpeta_familiar = "audio_familiar"
    titulo_poema = poema['titulo'].strip()
    archivo_familiar = None
    
    if os.path.exists(carpeta_familiar):
        for extension in ['*.mp3', '*.mp4', '*.wav', '*.m4a', '*.ogg']:
            patron = os.path.join(carpeta_familiar, extension)
            for archivo in glob.glob(patron):
                if os.path.splitext(os.path.basename(archivo))[0].lower() == titulo_poema.lower():
                    archivo_familiar = archivo; break
            if archivo_familiar: break
    
    if archivo_familiar:
        nombre_archivo = os.path.basename(archivo_familiar)
        extension = os.path.splitext(archivo_familiar)[1].lower()
        st.markdown(f"🎧 **Voz de un familiar:** {poema['titulo']}")
        st.info(f"Reproduciendo grabación personalizada: `{nombre_archivo}`")
        st.markdown('<div class="audio-container">', unsafe_allow_html=True)
        if extension == '.mp4': st.video(archivo_familiar)
        else: st.audio(archivo_familiar, format=f'audio/{extension[1:]}')
        st.markdown('</div>', unsafe_allow_html=True)
        with open(archivo_familiar, 'rb') as f: st.download_button(label=f"💾 Descargar {nombre_archivo}", data=f, file_name=nombre_archivo, mime="audio/mpeg")
    else:
        st.markdown("🤖 **Voz Neuronal (IA):** Seleccionada en el menú lateral")
        texto_audio = f"{poema['titulo']}. . . . " + limpiar_texto_para_audio(poema['contenido'])
        if poema.get('autor') or poema.get('año'):
            texto_audio += " . . . . "
            if poema.get('autor') and poema.get('año'): texto_audio += f"Por {poema['autor']}, año {poema['año']}."
            elif poema.get('autor'): texto_audio += f"Por {poema['autor']}."
            elif poema.get('año'): texto_audio += f"Año {poema['año']}."
        if st.button("🔊 Generar audio con voz neuronal", key=f"audio_{poema['titulo']}"):
            archivo = generar_audio_poema(texto_audio, st.session_state.get('voz_id', 'es-CO-SalomeNeural'), st.session_state.get('velocidad', '-15%'), st.session_state.get('volumen_voz', '+0%'))
            if archivo:
                st.success("✅ Audio generado")
                st.markdown('<div class="audio-container">', unsafe_allow_html=True); st.audio(archivo, format='audio/mp3'); st.markdown('</div>', unsafe_allow_html=True)
                with open(archivo, 'rb') as f: st.download_button(label="💾 Descargar MP3 (Voz IA)", data=f, file_name=f"{poema['titulo']}_IA.mp3", mime="audio/mpeg")

    # SECCIÓN DE MÚSICA CON API DE SOUNDCLOUD
    st.markdown("---\n### 🎵 Música de Fondo")
    cancion_url = st.session_state.get('cancion_url', CANCIONES["Romance Anónimo - Gonza Nico"])
    cancion_nombre = st.session_state.get('cancion_nombre', "Romance Anónimo - Gonza Nico")
    volumen = st.session_state.get('volumen_musica', 40)
    st.markdown(f"**Canción actual:** {cancion_nombre}")
    
    volumen_slider = st.slider("🔊 Volumen de la música:", 0, 100, volumen, 5, key=f"slider_volumen_poema_{poema['titulo']}", help="Ajusta el volumen de la música de fondo.")
    st.session_state.volumen_musica = volumen_slider
    
    sc_widget_code_poema = f"""
    <iframe id="sc-player-poema" width="100%" height="166" scrolling="no" frameborder="no" allow="autoplay" src="{cancion_url}"></iframe>
    <script src="https://w.soundcloud.com/player/api.js"></script>
    <script>
        var widgetIframe = document.getElementById('sc-player-poema');
        var widget = SC.Widget(widgetIframe);
        widget.bind(SC.Widget.Events.READY, function() {{ widget.setVolume({volumen_slider}); }});
        widget.setVolume({volumen_slider});
    </script>
    """
    st.components.v1.html(sc_widget_code_poema, height=200)

    st.markdown("---\n### 📄 Descargar en PDF")
    if st.button("📥 Generar PDF del poema", key=f"pdf_{poema['titulo']}"):
        with st.spinner("Generando PDF..."):
            try:
                archivo_pdf = generar_pdf_poema(poema); st.success("✅ PDF generado")
                with open(archivo_pdf, 'rb') as f: st.download_button("📥 Descargar PDF", f, f"{poema['titulo']}.pdf", "application/pdf")
            except Exception as e: st.error(f"❌ Error: {e}")

def mostrar_busqueda(libro):
    st.markdown("## 🔍 Búsqueda Avanzada")
    tipo = st.radio("Tipo:", ["Por contenido", "Por título", "Por autor", "Por año"], horizontal=True)
    termino = st.text_input("Búsqueda:")
    if termino:
        resultados = []
        for p in libro['poemas']:
            if tipo == "Por contenido" and termino.lower() in limpiar_texto(p['titulo'] + " " + p['contenido']): resultados.append(p)
            elif tipo == "Por título" and termino.lower() in limpiar_texto(p['titulo']): resultados.append(p)
            elif tipo == "Por autor" and termino.lower() in limpiar_texto(p.get('autor', '')): resultados.append(p)
            elif tipo == "Por año" and termino in p.get('año', ''): resultados.append(p)
        if resultados:
            sel = st.selectbox("Selecciona:", [f"{p['titulo']} ({p.get('año', '')})" for p in resultados])
            mostrar_poema(resultados[[f"{p['titulo']} ({p.get('año', '')})" for p in resultados].index(sel)])
        else: st.info("No se encontraron resultados.")

def mostrar_por_seccion(libro):
    st.markdown("## 📚 Por Sección")
    secciones = {}
    for p in libro['poemas']: secciones.setdefault(p.get('seccion', 'Sin sección'), []).append(p)
    sec = st.selectbox("Sección:", list(secciones.keys()))
    poema = next(p for p in secciones[sec] if p['titulo'] == st.selectbox("Poema:", [p['titulo'] for p in secciones[sec]]))
    mostrar_poema(poema)

def mostrar_por_tema(libro):
    st.markdown("## 🏷️ Por Tema")
    temas = sorted(set(t for p in libro['poemas'] for t in p.get('temas', [])))
    tema = st.selectbox("Tema:", temas)
    filtrados = [p for p in libro['poemas'] if tema in p.get('temas', [])]
    if filtrados:
        sel = st.selectbox("Poema:", [f"{p['titulo']} ({p.get('año', '')})" for p in filtrados])
        mostrar_poema(filtrados[[f"{p['titulo']} ({p.get('año', '')})" for p in filtrados].index(sel)])

def mostrar_todos(libro):
    st.markdown("## 📜 Todos los Poemas")
    sel = st.selectbox("Poema:", [f"{p['titulo']} — {p.get('autor', '')} ({p.get('año', '')})" for p in libro['poemas']])
    poema = next((p for p in libro['poemas'] if p['titulo'] == sel.split(' — ')[0]), None)
    if poema: mostrar_poema(poema)

def mostrar_estadisticas(libro):
    st.markdown("## 📊 Estadísticas")
    secciones, autores, temas = {}, {}, {}
    for p in libro['poemas']:
        secciones[p.get('seccion', 'Sin sección')] = secciones.get(p.get('seccion', 'Sin sección'), 0) + 1
        autores[p.get('autor', 'Desconocido')] = autores.get(p.get('autor', 'Desconocido'), 0) + 1
        for t in p.get('temas', []): temas[t] = temas.get(t, 0) + 1
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📂 Por Sección")
        for s, c in sorted(secciones.items(), key=lambda x: x[1], reverse=True): st.write(f"- {s}: {c}")
    with col2:
        st.markdown("### ✍️ Por Autor")
        for a, c in sorted(autores.items(), key=lambda x: x[1], reverse=True): st.write(f"- {a}: {c}")
    import pandas as pd
    st.markdown("### 🏷️ Temas")
    st.bar_chart(pd.DataFrame(sorted(temas.items(), key=lambda x: x[1], reverse=True)[:20], columns=['Tema', 'Frecuencia']).set_index('Tema'))

# ═══════════════════════════════════════════════════════
# FUNCIÓN PRINCIPAL
# ═══════════════════════════════════════════════════════

def main():
    if 'cancion_url' not in st.session_state:
        st.session_state.cancion_url = CANCIONES["Romance Anónimo - Gonza Nico"]
        st.session_state.cancion_nombre = "Romance Anónimo - Gonza Nico"
    if 'voz_id' not in st.session_state: st.session_state.voz_id = "es-CO-SalomeNeural"
    if 'velocidad' not in st.session_state: st.session_state.velocidad = "-15%"
    if 'volumen_voz' not in st.session_state: st.session_state.volumen_voz = "+0%"
    if 'volumen_musica' not in st.session_state: st.session_state.volumen_musica = 40
    
    try: libro = cargar_libro()
    except FileNotFoundError: st.error("❌ No se encontró 'prismas_liricos_completo.json'"); return
    
    with st.sidebar:
        st.markdown("## 📖 Navegación")
        modo = st.radio("Explorar:", ["🏠 Inicio", "🔍 Buscar", "📚 Por Sección", "🏷️ Por Tema", "📜 Todos", "📊 Estadísticas", "📸 Galería", "🎵 Música"], index=0)
        st.markdown("---\n### 🎵 Música")
        cancion_sel = st.selectbox("Canción:", list(CANCIONES.keys()), index=0)
        if cancion_sel and CANCIONES[cancion_sel]:
            st.session_state.cancion_url = CANCIONES[cancion_sel]
            st.session_state.cancion_nombre = cancion_sel
        
        st.markdown("---\n### 🎙️ Voz Lector")
        voces_map = {
            "🇪🇸 Helena (España - Femenina)": "es-ES-HelenaNeural", "🇪🇸 Álvaro (España - Masculino)": "es-ES-AlvaroNeural", "🇪🇸 Elvira (España - Femenina)": "es-ES-ElviraNeural",
            "🇲🇽 Dalia (México - Femenina)": "es-MX-DaliaNeural", "🇲🇽 Jorge (México - Masculino)": "es-MX-JorgeNeural", "🇲🇽 Lupe (México - Femenina)": "es-MX-LupeNeural",
            "🇲🇽 Beatriz (México - Femenina)": "es-MX-BeatrizNeural", "🇲🇽 Candelaria (México - Femenina)": "es-MX-CandelariaNeural", "🇲🇽 Carlota (México - Femenina)": "es-MX-CarlotaNeural",
            "🇲🇽 Cecilio (México - Masculino)": "es-MX-CecilioNeural", "🇲🇽 Gerardo (México - Masculino)": "es-MX-GerardoNeural", "🇲🇽 Liberto (México - Masculino)": "es-MX-LibertoNeural",
            "🇲🇽 Pelayo (México - Masculino)": "es-MX-PelayoNeural", "🇲🇽 Yago (México - Masculino)": "es-MX-YagoNeural",
            "🇨🇴 Salomé (Colombia - Femenina)": "es-CO-SalomeNeural", "🇨🇴 Gonzalo (Colombia - Masculino)": "es-CO-GonzaloNeural",
            "🇦🇷 Elena (Argentina - Femenina)": "es-AR-ElenaNeural", "🇦🇷 Tomás (Argentina - Masculino)": "es-AR-TomasNeural",
            "🇨🇱 Catalina (Chile - Femenina)": "es-CL-CatalinaNeural", "🇨🇱 Lorenzo (Chile - Masculino)": "es-CL-LorenzoNeural",
            "🇺🇸 Paloma (EE.UU. - Femenina)": "es-US-PalomaNeural", "🇺🇸 Alonso (EE.UU. - Masculino)": "es-US-AlonsoNeural",
            "🇻🇪 Paola (Venezuela - Femenina)": "es-VE-PaolaNeural", "🇻🇪 Sebastián (Venezuela - Masculino)": "es-VE-SebastianNeural",
            "🇵🇪 Camila (Perú - Femenina)": "es-PE-CamilaNeural", "🇵🇪 Alex (Perú - Masculino)": "es-PE-AlexNeural",
            "🇪🇨 Andrea (Ecuador - Femenina)": "es-EC-AndreaNeural", "🇪🇨 Luis (Ecuador - Masculino)": "es-EC-LuisNeural",
            "🇧🇴 Marcelo (Bolivia - Masculino)": "es-BO-MarceloNeural", "🇧🇴 Sofia (Bolivia - Femenina)": "es-BO-SofiaNeural",
            "🇺🇾 Mateo (Uruguay - Masculino)": "es-UY-MateoNeural", "🇺🇾 Valentina (Uruguay - Femenina)": "es-UY-ValentinaNeural",
            "🇨🇷 María (Costa Rica - Femenina)": "es-CR-MariaNeural", "🇨🇷 Juan (Costa Rica - Masculino)": "es-CR-JuanNeural",
            "🇵🇷 Karina (Puerto Rico - Femenina)": "es-PR-KarinaNeural", "🇵🇷 Víctor (Puerto Rico - Masculino)": "es-PR-VictorNeural",
            "🇩🇴 Ramona (Rep. Dominicana - Femenina)": "es-DO-RamonaNeural", "🇩🇴 Emilio (Rep. Dominicana - Masculino)": "es-DO-EmilioNeural",
            "🇬🇹 Marta (Guatemala - Femenina)": "es-GT-MartaNeural", "🇬🇹 Andrés (Guatemala - Masculino)": "es-GT-AndresNeural"
        }
        opciones_voces = list(voces_map.keys())
        indice_por_defecto = opciones_voces.index("🇨🇴 Salomé (Colombia - Femenina)") if "🇨🇴 Salomé (Colombia - Femenina)" in opciones_voces else 0
        voz_sel = st.selectbox("Seleccionar Voz:", options=opciones_voces, index=indice_por_defecto, help="Elige la voz del narrador.")
        st.session_state.voz_id = voces_map[voz_sel]
        vel_slider = st.slider('Velocidad de voz:', -30, 10, -15, step=5, help="Negativo es más lento.")
        st.session_state.velocidad = f"{vel_slider}%"
        st.markdown("---")
        st.info(f"**Textos:** {len(libro['poemas'])}")
    
    if modo == "🏠 Inicio": mostrar_inicio(libro)
    else:
        st.markdown('<div class="main-title">PRISMAS LÍRICOS</div>', unsafe_allow_html=True)
        st.markdown('<div class="subtitle">Jesús Ignacio Guerra Figueroa</div>', unsafe_allow_html=True)
        st.markdown("---")
        if modo == "🔍 Buscar": mostrar_busqueda(libro)
        elif modo == "📚 Por Sección": mostrar_por_seccion(libro)
        elif modo == "🏷️ Por Tema": mostrar_por_tema(libro)
        elif modo == "📜 Todos": mostrar_todos(libro)
        elif modo == "📊 Estadísticas": mostrar_estadisticas(libro)
        elif modo == "📸 Galería": mostrar_galeria()
        elif modo == "🎵 Música": mostrar_musica()

if __name__ == "__main__":
    main()
