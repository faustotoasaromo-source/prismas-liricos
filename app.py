# -*- coding: utf-8 -*-
"""
╔════════════════════════════════════════════════════════════════╗
║   PRISMAS LÍRICOS - Aplicación Web con Formato de Versos     ║
║   Jesús Ignacio Guerra Figueroa                               ║
╚════════════════════════════════════════════════════════════════╝
"""

import json
import os
import streamlit as st
import re
import asyncio
import tempfile

# ═══════════════════════════════════════════════════════
# CONFIGURACIÓN INICIAL
# ═══════════════════════════════════════════════════════

st.set_page_config(
    page_title="Prismas Líricos - Jesús Ignacio Guerra Figueroa",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado con formato de versos
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&family=EB+Garamond:ital@0;1&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #f5f1e8 0%, #ebe4d4 100%);
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
    
    .verse-line {
        display: block;
        margin: 0.3em 0;
        text-indent: -2em;
        padding-left: 2em;
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
    
    .sidebar-text {
        font-family: 'EB Garamond', serif;
        color: #4a2c17;
    }
    
    /* Formato especial para versos centrados */
    .centered-verse {
        text-align: center;
        font-style: italic;
    }
    
    /* Separador entre estrofas */
    .stanza-break {
        height: 1.5em;
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# FUNCIONES DE AUDIO
# ══════════════════════════════════════════════════════

@st.cache_resource
def generar_audio_poema(texto, voz="es-ES-HelenaNeural", rate="-15%"):
    """Genera audio de un poema usando Edge-TTS."""
    try:
        import edge_tts
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            archivo_temp = tmp_file.name
        
        # Generar audio
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
    # Eliminar símbolos decorativos pero mantener saltos de línea
    texto = re.sub(r'[*═╔╗╚╝║┌┐└┘├┤┬┴┼─│]', '', texto)
    
    # Reemplazar puntos suspensivos
    texto = texto.replace('...', ', ')
    texto = texto.replace('....', ', ')
    
    # Normalizar espacios pero mantener saltos de línea
    lineas = texto.split('\n')
    lineas_limpias = [re.sub(r'\s+', ' ', linea).strip() for linea in lineas]
    texto = '\n'.join(lineas_limpias)
    
    return texto.strip()


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
    """
    Formatea el contenido preservando los saltos de línea
    y la estructura original de los versos como en el libro.
    """
    # Dividir por líneas
    lineas = contenido.strip().split('\n')
    
    # Filtrar líneas vacías al inicio y final
    while lineas and not lineas[0].strip():
        lineas.pop(0)
    while lineas and not lineas[-1].strip():
        lineas.pop()
    
    # Unir preservando saltos de línea
    return '\n'.join(lineas)


# ═══════════════════════════════════════════════════════
# INTERFAZ PRINCIPAL
# ═══════════════════════════════════════════════════════

def main():
    # Cargar datos
    try:
        libro = cargar_libro()
    except FileNotFoundError:
        st.error("❌ No se encontró 'prismas_liricos_completo.json'")
        st.info("Ejecuta primero: `python poemas_parte_3.py` para generar el archivo.")
        return
    
    # ══════════════════════════════════════════════════
    # PORTADA
    # ═══════════════════════════════════════════════════
    st.markdown('<div class="main-title">PRISMAS LÍRICOS</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Jesús Ignacio Guerra Figueroa</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="homenaje">{libro.get("homenaje", "")}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ═══════════════════════════════════════════════════
    # SIDEBAR - NAVEGACIÓN Y CONFIGURACIÓN DE VOZ
    # ═══════════════════════════════════════════════════
    with st.sidebar:
        st.markdown("## 📖 Navegación")
        
        modo = st.radio(
            "¿Cómo deseas explorar?",
            ["🏠 Inicio", " Buscar", "📚 Por Sección", "🏷️ Por Tema", "📜 Todos los poemas", "📊 Estadísticas"],
            index=0
        )
        
        st.markdown("---")
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
        
        # Mapear nombre a ID de voz
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
    
    # ═══════════════════════════════════════════════════
    # CONTENIDO PRINCIPAL
    # ═══════════════════════════════════════════════════
    
    if modo == "🏠 Inicio":
        mostrar_inicio(libro)
    
    elif modo == "🔍 Buscar":
        mostrar_busqueda(libro)
    
    elif modo == "📚 Por Sección":
        mostrar_por_seccion(libro)
    
    elif modo == "🏷️ Por Tema":
        mostrar_por_tema(libro)
    
    elif modo == "📜 Todos los poemas":
        mostrar_todos(libro)
    
    elif modo == "📊 Estadísticas":
        mostrar_estadisticas(libro)


def mostrar_poema(poema):
    """Muestra un poema individual con formato de versos y audio."""
    
    # Formatear contenido preservando versos
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
    
    # ═══════════════════════════════════════════════════
    # SECCIÓN DE AUDIO
    # ═══════════════════════════════════════════════════
    st.markdown("---")
    st.markdown("### 🎙️ Escuchar este poema")
    
    # Preparar texto para audio
    texto_audio = f"{poema['titulo']}. "
    if poema.get('autor'):
        texto_audio += f"De {poema['autor']}. "
    if poema.get('año'):
        texto_audio += f"Año {poema['año']}. "
    
    texto_audio += ". . . "
    texto_audio += limpiar_texto_para_audio(poema['contenido'])
    
    # Botón para generar y reproducir audio
    if st.button("🔊 Generar y reproducir audio", key=f"audio_{poema['titulo']}"):
        with st.spinner("Generando audio con voz neuronal..."):
            voz_id = st.session_state.get('voz_id', 'es-ES-HelenaNeural')
            velocidad = st.session_state.get('velocidad', '-15%')
            
            archivo_audio = generar_audio_poema(texto_audio, voz_id, velocidad)
            
            if archivo_audio:
                st.success("✅ Audio generado exitosamente")
                
                # Mostrar reproductor de audio
                st.markdown('<div class="audio-container">', unsafe_allow_html=True)
                st.audio(archivo_audio, format='audio/mp3')
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Opción de descarga
                with open(archivo_audio, 'rb') as f:
                    st.download_button(
                        label=" Descargar MP3",
                        data=f,
                        file_name=f"{poema['titulo']}.mp3",
                        mime="audio/mpeg"
                    )
            else:
                st.error("❌ No se pudo generar el audio")


def mostrar_inicio(libro):
    """Muestra la página de inicio."""
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
        - 👨‍‍👧‍👦 Versos de hijos y nietos
        -  El Álbum de Recuerdos de toda una vida de amor
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
        - ✅ Formato de versos preservado
        
        **Cómo usar:**
        1. Selecciona una voz en el menú lateral
        2. Ajusta la velocidad de lectura
        3. Navega a cualquier poema
        4. Haz clic en "🔊 Generar y reproducir audio"
        """)
        
        st.markdown("---")
        st.markdown("### 💡 Consejo")
        st.info("""
        Para una experiencia óptima, te recomendamos:
        - **Voz**: Helena (España - Femenina)
        - **Velocidad**: -15% (poética)
        - **Ambiente**: Lugar tranquilo para apreciar la poesía
        """)


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
    
    # Recopilar todos los temas
    temas_unicos = set()
    for poema in libro['poemas']:
        temas_unicos.update(poema.get('temas', []))
    
    temas_ordenados = sorted(temas_unicos)
    
    tema_elegido = st.selectbox("Elige un tema:", temas_ordenados)
    
    # Filtrar poemas con ese tema
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
    
    # Buscar el poema por título
    titulo_seleccionado = poema_elegido.split(' — ')[0]
    poema = next((p for p in libro['poemas'] if p['titulo'] == titulo_seleccionado), None)
    
    if poema:
        mostrar_poema(poema)


def mostrar_estadisticas(libro):
    """Muestra estadísticas del libro."""
    st.markdown("## 📊 Estadísticas del Libro")
    
    # Recopilar datos
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
    
    # Gráfico de barras con Streamlit
    import pandas as pd
    df = pd.DataFrame(temas_top, columns=['Tema', 'Frecuencia'])
    st.bar_chart(df.set_index('Tema'))
    
    st.markdown("### 📅 Distribución por Año")
    años_ordenados = {k: v for k, v in sorted(años.items()) if k.isdigit()}
    df_años = pd.DataFrame(list(años_ordenados.items()), columns=['Año', 'Textos'])
    st.line_chart(df_años.set_index('Año'))


if __name__ == "__main__":
    main()
