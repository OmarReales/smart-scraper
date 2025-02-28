import streamlit as st
import pandas as pd
import time
from utils.validators import is_valid_url
from utils.scraper import scrape_website_static, scrape_website_dynamic
from utils.ai_helpers import ask_chatgpt, ask_groq, ask_gemini, analyze_scraped_data

# Configuración de la página con mejor soporte para móviles
st.set_page_config(
    page_title="Smart Scraper IA",  # Nombre actualizado
    layout="wide",
    initial_sidebar_state="collapsed",  # Colapsado por defecto en dispositivos pequeños
    menu_items={
        'Get Help': 'https://github.com/tu-usuario/smart-scraper',
        'About': 'Herramienta para extraer datos de páginas web con Inteligencia Artificial'
    }
)

# CSS personalizado para mejorar la responsividad
st.markdown("""
<style>
    /* Hacer que los botones se ajusten al ancho del contenedor */
    .stButton>button {
        width: 100%;
        margin-top: 5px;
        margin-bottom: 5px;
    }
    
    /* Mejorar visualización en móvil */
    @media (max-width: 640px) {
        .main .block-container {
            padding-left: 10px;
            padding-right: 10px;
            padding-top: 20px;
        }
        
        /* Ajustar tamaño de texto en móviles */
        h1 {
            font-size: 1.5rem !important;
        }
        h2, h3 {
            font-size: 1.2rem !important;
        }
        .streamlit-expanderHeader {
            font-size: 1rem !important;
        }
    }
    
    /* Hacer que las tablas de datos sean más compactas en dispositivos pequeños */
    .stDataFrame {
        overflow-x: auto;
    }
    
    /* Ajustar inputs para mejor presentación */
    .stTextInput, .stSelectbox, .stMultiselect {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar el estado de la sesión
if 'scraping_results' not in st.session_state:
    st.session_state.scraping_results = None
if 'last_url' not in st.session_state:
    st.session_state.last_url = ""
if 'selected_tags' not in st.session_state:
    st.session_state.selected_tags = {}
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = "compact"  # Modo compacto o expandido

# Función para cambiar el modo de visualización
def change_view_mode():
    st.session_state.view_mode = "compact" if st.session_state.display_mode == "Compacto" else "expanded"

# Cargar API Keys desde secrets o inicializarlas
def load_api_keys():
    try:
        groq_key = st.secrets.get("GROQ_API_KEY", "")
        gemini_key = st.secrets.get("GENAI_API_KEY", "")
        chatgpt_key = st.secrets.get("OPENAI_API_KEY", "")
        return groq_key, gemini_key, chatgpt_key
    except Exception as e:
        st.error(f"Error cargando API keys: {e}")
        return "", "", ""

# Sidebar mejorada para dispositivos móviles
with st.sidebar:
    st.header("⚙️ Configuración")
    
    # Modo de visualización
    st.radio("Modo de visualización:", 
             ["Compacto", "Expandido"], 
             key="display_mode",
             on_change=change_view_mode)
    
    # Sección de API Keys más compacta
    with st.expander("🔑 API Keys", expanded=False):
        groq_key, gemini_key, chatgpt_key = load_api_keys()
        
        groq_api_key = st.text_input("Groq API", value=groq_key, type="password")
        gemini_api_key = st.text_input("Gemini API", value=gemini_key, type="password")
        chatgpt_api_key = st.text_input("ChatGPT API", value=chatgpt_key, type="password")
        
        if st.button("💾 Guardar"):
            st.session_state.groq_api_key = groq_api_key
            st.session_state.gemini_api_key = gemini_api_key
            st.session_state.chatgpt_api_key = chatgpt_api_key
            st.success("✅ Guardado")
    
    # Opciones avanzadas más compactas
    with st.expander("⚡ Opciones Avanzadas", expanded=False):
        use_selenium = st.checkbox("Usar Selenium", value=False,
                                  help="Para contenido dinámico con JavaScript")
        wait_time = st.slider("Tiempo espera (s)", 1, 10, 3)

# Título de la app con ícono y descripción compacta
col1, col2 = st.columns([1, 6])
with col1:
    st.markdown("# 🕷️")
with col2:
    st.markdown("# Smart Scraper IA")  # Nombre actualizado

# Separador más pequeño
st.markdown("---")

# Entrada de URL con validación - ancho completo para adaptarse a cualquier pantalla
url = st.text_input("🔗 URL a analizar:", value=st.session_state.last_url, 
                    placeholder="https://ejemplo.com",
                    help="Ingresa la dirección web que deseas analizar")
is_url_valid = is_valid_url(url) if url else False

if url and not is_url_valid:
    st.error("❌ URL inválida")
elif url:
    st.session_state.last_url = url

# Pestañas principales - nombres más cortos para mejor visualización en móvil
tab1, tab2, tab3 = st.tabs(["📊 Extracción", "🔍 Resultados", "🤖 IA"])

# Tab 1: Extracción más compacta
with tab1:
    # Versión compacta para dispositivos pequeños
    tag_select_container = st.container()
    
    with tag_select_container:
        st.subheader("Seleccionar elementos")
        
        # Versión responsiva con menos categorías
        view_mode = st.session_state.view_mode
        
        if view_mode == "compact":
            # Modo compacto: categorías desplegables
            with st.expander("Estructura (div, main, article...)"):
                struct_tags = ["div", "main", "article", "section", "aside", "header", "footer", "nav"]
                for tag in struct_tags:
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        if st.checkbox(tag, key=f"tag_{tag}"):
                            with col2:
                                class_input = st.text_input("CSS", key=f"class_{tag}", placeholder="clase")
                                st.session_state.selected_tags[tag] = {
                                    "class": class_input,
                                    "id": "",
                                    "selector": ""
                                }
                        elif tag in st.session_state.selected_tags:
                            del st.session_state.selected_tags[tag]
            
            # Otras categorías similares en formato compacto
            with st.expander("Contenido (p, h1, span...)"):
                content_tags = ["p", "span", "h1", "h2", "h3", "h4", "strong", "em", "time"]
                for tag in content_tags:
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        if st.checkbox(tag, key=f"tag_{tag}"):
                            with col2:
                                class_input = st.text_input("CSS", key=f"class_{tag}", placeholder="clase")
                                st.session_state.selected_tags[tag] = {
                                    "class": class_input,
                                    "id": "",
                                    "selector": ""
                                }
                        elif tag in st.session_state.selected_tags:
                            del st.session_state.selected_tags[tag]
                            
            with st.expander("Listas/Tablas (ul, ol, table...)"):
                list_tags = ["ul", "ol", "li", "table", "tr", "td"]
                for tag in list_tags:
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        if st.checkbox(tag, key=f"tag_{tag}"):
                            with col2:
                                class_input = st.text_input("CSS", key=f"class_{tag}", placeholder="clase")
                                st.session_state.selected_tags[tag] = {
                                    "class": class_input,
                                    "id": "",
                                    "selector": ""
                                }
                        elif tag in st.session_state.selected_tags:
                            del st.session_state.selected_tags[tag]
                            
            with st.expander("Elementos interactivos (a, button...)"):
                interact_tags = ["a", "button", "input", "form", "select"]
                for tag in interact_tags:
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        if st.checkbox(tag, key=f"tag_{tag}"):
                            with col2:
                                class_input = st.text_input("CSS", key=f"class_{tag}", placeholder="clase")
                                st.session_state.selected_tags[tag] = {
                                    "class": class_input,
                                    "id": "",
                                    "selector": ""
                                }
                        elif tag in st.session_state.selected_tags:
                            del st.session_state.selected_tags[tag]
            
            # Agregar selector CSS avanzado como opción separada
            with st.expander("Selector CSS avanzado"):
                css_query = st.text_input("Ingresa un selector CSS:", placeholder=".product-item .price")
                if st.button("Agregar selector"):
                    if css_query:
                        st.session_state.selected_tags["custom"] = {
                            "class": "",
                            "id": "",
                            "selector": css_query
                        }
        else:
            # Modo expandido: usar el diseño con pestañas
            tag_categories = st.tabs(["Estructura", "Contenido", "Tablas/Listas", "Media", "Interactivos"])
            
            # 1. Etiquetas de estructura
            with tag_categories[0]:
                struct_tags = ["div", "main", "article", "section", "aside", "header", "footer", "nav"]
                col1, col2 = st.columns(2)
                for i, tag in enumerate(struct_tags):
                    with col1 if i % 2 == 0 else col2:
                        if st.checkbox(f"{tag}", key=f"tag_{tag}"):
                            class_name = st.text_input(f"Clase CSS", key=f"class_{tag}")
                            id_name = st.text_input(f"ID", key=f"id_{tag}")
                            css_selector = st.text_input(f"Selector CSS", key=f"selector_{tag}")
                            st.session_state.selected_tags[tag] = {
                                "class": class_name, "id": id_name, "selector": css_selector
                            }
                        elif tag in st.session_state.selected_tags:
                            del st.session_state.selected_tags[tag]
            
            # 2. Etiquetas de contenido
            with tag_categories[1]:
                content_tags = ["p", "span", "h1", "h2", "h3", "h4", "strong", "em", "time"]
                col1, col2 = st.columns(2)
                for i, tag in enumerate(content_tags):
                    with col1 if i % 2 == 0 else col2:
                        if st.checkbox(f"{tag}", key=f"tag_{tag}"):
                            class_name = st.text_input(f"Clase CSS", key=f"class_{tag}")
                            id_name = st.text_input(f"ID", key=f"id_{tag}")
                            css_selector = st.text_input(f"Selector CSS", key=f"selector_{tag}")
                            st.session_state.selected_tags[tag] = {
                                "class": class_name, "id": id_name, "selector": css_selector
                            }
                        elif tag in st.session_state.selected_tags:
                            del st.session_state.selected_tags[tag]
            
            # 3. Tablas y listas
            with tag_categories[2]:
                list_tags = ["ul", "ol", "li", "table", "tr", "td", "th"]
                col1, col2 = st.columns(2)
                for i, tag in enumerate(list_tags):
                    with col1 if i % 2 == 0 else col2:
                        if st.checkbox(f"{tag}", key=f"tag_{tag}"):
                            class_name = st.text_input(f"Clase CSS", key=f"class_{tag}")
                            id_name = st.text_input(f"ID", key=f"id_{tag}")
                            css_selector = st.text_input(f"Selector CSS", key=f"selector_{tag}")
                            st.session_state.selected_tags[tag] = {
                                "class": class_name, "id": id_name, "selector": css_selector
                            }
                        elif tag in st.session_state.selected_tags:
                            del st.session_state.selected_tags[tag]
            
            # 4. Media
            with tag_categories[3]:
                media_tags = ["img", "video", "audio", "source", "picture", "figure", "figcaption"]
                col1, col2 = st.columns(2)
                for i, tag in enumerate(media_tags):
                    with col1 if i % 2 == 0 else col2:
                        if st.checkbox(f"{tag}", key=f"tag_{tag}"):
                            class_name = st.text_input(f"Clase CSS", key=f"class_{tag}")
                            id_name = st.text_input(f"ID", key=f"id_{tag}")
                            css_selector = st.text_input(f"Selector CSS", key=f"selector_{tag}")
                            st.session_state.selected_tags[tag] = {
                                "class": class_name, "id": id_name, "selector": css_selector
                            }
                        elif tag in st.session_state.selected_tags:
                            del st.session_state.selected_tags[tag]
            
            # 5. Interactivos
            with tag_categories[4]:
                interact_tags = ["a", "button", "form", "input", "select", "option", "label", "iframe"]
                col1, col2 = st.columns(2)
                for i, tag in enumerate(interact_tags):
                    with col1 if i % 2 == 0 else col2:
                        if st.checkbox(f"{tag}", key=f"tag_{tag}"):
                            class_name = st.text_input(f"Clase CSS", key=f"class_{tag}")
                            id_name = st.text_input(f"ID", key=f"id_{tag}")
                            css_selector = st.text_input(f"Selector CSS", key=f"selector_{tag}")
                            st.session_state.selected_tags[tag] = {
                                "class": class_name, "id": id_name, "selector": css_selector
                            }
                        elif tag in st.session_state.selected_tags:
                            del st.session_state.selected_tags[tag]
    
    # Mostrar elementos seleccionados de manera más compacta
    if st.session_state.selected_tags:
        st.write(f"**{len(st.session_state.selected_tags)} elementos seleccionados**")
        if st.button("Ver elementos seleccionados"):
            for tag, attrs in st.session_state.selected_tags.items():
                if attrs['selector']:
                    st.code(f"Selector: {attrs['selector']}")
                else:
                    st.code(f"<{tag}> clase='{attrs['class']}' id='{attrs['id']}'")
    else:
        st.info("Selecciona al menos un elemento")
    
    # Botón grande para ejecutar (mejor para tocar en móviles)
    st.markdown("<br>", unsafe_allow_html=True)  # Espacio extra
    if st.button("🚀 EJECUTAR SCRAPING", 
                disabled=not (is_url_valid and st.session_state.selected_tags),
                use_container_width=True,
                type="primary"):
        with st.spinner("⏱️ Extrayendo datos..."):
            try:
                if use_selenium:
                    results = scrape_website_dynamic(url, st.session_state.selected_tags, wait_time)
                else:
                    results = scrape_website_static(url, st.session_state.selected_tags)
                
                if isinstance(results, pd.DataFrame):
                    st.session_state.scraping_results = results
                    st.success(f"✅ Extracción completa! ({len(results)} elementos)")
                    # Ir a la pestaña de resultados
                    st.rerun()  # Usando st.rerun() que es la versión actualizada de experimental_rerun
                else:
                    st.error(f"❌ Error: {results}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Tab 2: Resultados más responsivos
with tab2:
    if st.session_state.scraping_results is not None and not st.session_state.scraping_results.empty:
        results = st.session_state.scraping_results
        
        # Filtros más compactos para móvil
        if st.session_state.view_mode == "compact":
            # Versión móvil: filtros en acordeón
            with st.expander("🔍 Filtros"):
                tag_filter = st.multiselect("Etiqueta:", 
                                      options=results['Etiqueta'].unique(),
                                      default=results['Etiqueta'].unique())
                search_term = st.text_input("Buscar:", "")
        else:
            # Versión desktop: filtros en columnas
            col1, col2 = st.columns(2)
            with col1:
                tag_filter = st.multiselect("Filtrar por etiqueta:", 
                                          options=results['Etiqueta'].unique(),
                                          default=results['Etiqueta'].unique())
            with col2:
                search_term = st.text_input("Buscar en contenido:", "")
        
        # Aplicar filtros
        filtered_results = results[results['Etiqueta'].isin(tag_filter)]
        if search_term:
            filtered_results = filtered_results[filtered_results['Contenido'].str.contains(search_term, case=False, na=False)]
        
        # Mostrar resultados
        st.write(f"Mostrando {len(filtered_results)} de {len(results)} resultados")
        
        # Determinar columnas a mostrar según lo que existe
        available_cols = filtered_results.columns.tolist()
        columns_to_display = ['Etiqueta', 'Contenido']
        extra_cols = []
        
        # Agregar columnas adicionales si existen
        for col in ['href', 'src', 'alt', 'texto_enlace']:
            if col in available_cols:
                extra_cols.append(col)
                
        if st.session_state.view_mode == "expanded":
            columns_to_display.extend(extra_cols)
        
        # Mostrar tabla con scroll horizontal en móviles
        st.dataframe(filtered_results[columns_to_display], 
                     use_container_width=True)
        
        # Botón para ver detalles del HTML
        if st.button("Ver detalles HTML", use_container_width=True):
            for i, row in filtered_results.iterrows():
                with st.expander(f"{row['Etiqueta']}: {row['Contenido'][:50]}..."):
                    st.code(row['HTML'], language="html")
        
        # Exportar - versión compacta
        col1, col2 = st.columns(2)
        with col1:
            csv_data = filtered_results.to_csv(index=False).encode('utf-8')
            st.download_button("📥 CSV", csv_data, "scraping_results.csv", "text/csv", use_container_width=True)
        
        with col2:
            json_data = filtered_results.to_json(orient="records")
            st.download_button("📥 JSON", json_data, "scraping_results.json", "application/json", use_container_width=True)
    else:
        st.info("Sin resultados. Ejecuta el scraping primero.")

# Tab 3: Asistente de IA más compacto
with tab3:
    ai_tabs = st.tabs(["🤖 Preguntar", "📊 Analizar"])
    
    # Tab para hacer preguntas - más responsivo
    with ai_tabs[0]:
        query = st.text_area("Tu pregunta:", placeholder="¿Cómo extraer precios de una página web?")
        
        # En modo compacto, botones en vertical
        if st.session_state.view_mode == "compact":
            if st.button("Preguntar a ChatGPT", use_container_width=True, disabled=not query):
                with st.spinner("Consultando..."):
                    response = ask_chatgpt(query, st.session_state.get('chatgpt_api_key', ''))
                    st.write(response)
                    
            if st.button("Preguntar a Groq", use_container_width=True, disabled=not query):
                with st.spinner("Consultando..."):
                    response = ask_groq(query, st.session_state.get('groq_api_key', ''))
                    st.write(response)
                    
            if st.button("Preguntar a Gemini", use_container_width=True, disabled=not query):
                with st.spinner("Consultando..."):
                    response = ask_gemini(query, st.session_state.get('gemini_api_key', ''))
                    st.write(response)
        else:
            # En modo expandido, botones en horizontal
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("Preguntar a ChatGPT", use_container_width=True, disabled=not query):
                    with st.spinner("Consultando a ChatGPT..."):
                        response = ask_chatgpt(query, st.session_state.get('chatgpt_api_key', ''))
                        st.write("### ChatGPT")
                        st.write(response)
            
            with col2:
                if st.button("Preguntar a Groq", use_container_width=True, disabled=not query):
                    with st.spinner("Consultando a Groq..."):
                        response = ask_groq(query, st.session_state.get('groq_api_key', ''))
                        st.write("### Groq")
                        st.write(response)
            
            with col3:
                if st.button("Preguntar a Gemini", use_container_width=True, disabled=not query):
                    with st.spinner("Consultando a Gemini..."):
                        response = ask_gemini(query, st.session_state.get('gemini_api_key', ''))
                        st.write("### Gemini")
                        st.write(response)
    
    # Tab para analizar datos - simplificado
    with ai_tabs[1]:
        if st.session_state.scraping_results is not None and not st.session_state.scraping_results.empty:
            ai_model = st.radio("Modelo de IA:", ["Groq", "ChatGPT", "Gemini"], horizontal=True)
            
            if st.button("Analizar datos", use_container_width=True):
                with st.spinner(f"Analizando con {ai_model}..."):
                    api_key = ""
                    model_type = ""
                    
                    if ai_model == "ChatGPT":
                        api_key = st.session_state.get('chatgpt_api_key', '')
                        model_type = "chatgpt"
                    elif ai_model == "Groq":
                        api_key = st.session_state.get('groq_api_key', '')
                        model_type = "groq"
                    else:
                        api_key = st.session_state.get('gemini_api_key', '')
                        model_type = "gemini"
                        
                    analysis = analyze_scraped_data(
                        st.session_state.scraping_results,
                        api_key,
                        model_type
                    )
                    st.write("### Análisis")
                    st.write(analysis)
        else:
            st.info("Sin datos para analizar. Ejecuta el scraping primero.")

# Footer más compacto
st.divider()
st.markdown("<div style='text-align: center; opacity: 0.7'>Smart Scraper IA | Desarrollado con ❤️</div>", unsafe_allow_html=True)
