# 🕷️ Smart Scraper IA

Una herramienta interactiva para extraer datos de sitios web con asistencia de inteligencia artificial.

![Smart Scraper IA](https://img.shields.io/badge/Smart%20Scraper-IA-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.25%2B-red)

## 📋 Descripción

Smart Scraper IA es una aplicación que combina web scraping con inteligencia artificial para facilitar la extracción y análisis de datos de páginas web. Con una interfaz intuitiva construida en Streamlit, permite seleccionar elementos HTML específicos, extraer su contenido, y luego analizar los resultados utilizando modelos de IA como Gemini, ChatGPT y Groq.

## ✨ Características principales

- **Extracción de datos simplificada**: Selección intuitiva de elementos HTML mediante etiquetas, clases, IDs o selectores CSS
- **Autodetección inteligente**: Detecta automáticamente elementos relevantes según el tipo de página
- **Plantillas predefinidas**: Usa plantillas para diferentes tipos de sitios web como e-commerce, noticias, o tablas de datos
- **Gestión de proyectos**: Guarda y reutiliza tus proyectos de extracción para uso futuro
- **Soporte para páginas dinámicas**: Extrae contenido de sitios con JavaScript usando Selenium y detección automática de navegadores
- **Múltiples modelos de IA**: Compatibilidad con Gemini (Google), ChatGPT (OpenAI) y una amplia variedad de modelos Groq (Llama 3.3, Gemma 2, etc.)
- **Interfaz responsiva**: Diseñada para funcionar en dispositivos móviles y de escritorio
- **Exportación flexible**: Guarda los resultados en CSV, JSON o Excel
- **Análisis inteligente**: Obtén insights sobre los datos extraídos mediante IA

## 🗂️ Estructura del proyecto

```
/smart-scraper/
├── main.py                      # Aplicación principal de Streamlit
├── requirements.txt             # Dependencias del proyecto
├── README.md                    # Documentación
├── .streamlit/                  # Configuración de Streamlit
│   └── secrets.toml             # Claves API secretas
└── utils/                       # Módulos auxiliares
    ├── __init__.py              # Inicialización del paquete
    ├── ai_helpers.py            # Funciones para interacción con IA
    ├── scraper.py               # Funciones de web scraping
    ├── validators.py            # Validadores y utilidades
    ├── autodetect.py            # Funciones para autodetección de elementos
    └── templates.py             # Plantillas predefinidas para diferentes tipos de sitios web
```

## 🛠️ Requisitos e instalación

### Prerrequisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Navegador Chrome (para el modo Selenium)

### Instalación

1. Clona este repositorio o descárgalo como ZIP y descomprímelo
2. Navega al directorio del proyecto

```bash
cd smart-scraper
```

3. Crea un entorno virtual (opcional pero recomendado)

```bash
python -m venv .venv
# Activar en Windows
.venv\Scripts\activate
# Activar en macOS/Linux
source .venv/bin/activate
```

4. Instala las dependencias

```bash
pip install -r requirements.txt
```

## ⚙️ Configuración

### Claves API

Para utilizar las funciones de IA, necesitas configurar las claves API en la aplicación:

1. Crea un archivo `.streamlit/secrets.toml` con tus claves API:

```toml
GROQ_API_KEY = "tu-clave-api-de-groq"
GENAI_API_KEY = "tu-clave-api-de-google-gemini"
OPENAI_API_KEY = "tu-clave-api-de-openai"
```

Alternativamente, puedes ingresar las claves directamente en la interfaz de la aplicación.

## 🚀 Uso

Para ejecutar la aplicación:

```bash
streamlit run main.py
```

Esto abrirá la interfaz de usuario en tu navegador (normalmente en http://localhost:8501).

### 🧩 Guía rápida

1. **Ingresa una URL**: Empieza ingresando la dirección del sitio web que deseas analizar
2. **Selecciona elementos**: Marca las etiquetas HTML que te interesan (divs, párrafos, tablas, etc.)
3. **Configura atributos**: Agrega clases, IDs o selectores CSS para afinar la búsqueda
4. **Ejecuta el scraping**: Presiona el botón "EJECUTAR SCRAPING"
5. **Explora resultados**: Visualiza los datos extraídos, filtra y busca información específica
6. **Exporta o analiza**: Descarga los resultados o consulta a los modelos de IA para análisis

## 🧠 Modelos de IA disponibles

La aplicación soporta tres motores de IA:

- **Gemini (Google)**: Modelos como gemini-2.0-flash y gemini-pro
- **ChatGPT (OpenAI)**: Acceso a GPT-3.5 Turbo
- **Groq**: Modelos como Llama 3.3 y Gemma 2

Puedes usar estos modelos para:

- Hacer preguntas sobre web scraping
- Analizar los datos extraídos
- Obtener ayuda con selectores CSS o XPath
- Transformar los datos en formatos específicos

## 🎯 Ejemplos de uso

- Extraer precios y nombres de productos de tiendas online
- Recopilar noticias o artículos de blogs
- Obtener datos tabulares de páginas web
- Extraer información de contacto de directorios
- Monitorear cambios en sitios web

## 📱 Interfaz responsiva

La aplicación ofrece dos modos de visualización:

- **Compacto**: Optimizado para dispositivos móviles y pantallas pequeñas
- **Expandido**: Aprovecha el espacio en pantallas grandes

Se adapta automáticamente a diferentes tamaños de pantalla.

## ❓ Solución de problemas

- **Error con Selenium**: Asegúrate de tener Chrome instalado y actualizado
- **Errores en API de IA**: Verifica que tus claves API sean correctas y estén activas
- **Problemas extrayendo datos dinámicos**: Activa el modo Selenium e incrementa el tiempo de espera
- **URL inválida**: Comprueba que la URL comience con http:// o https://

## 📄 Licencia

Este proyecto está licenciado bajo la licencia MIT. Ver el archivo LICENSE para más detalles.

## 👥 Contribuciones

Las contribuciones son bienvenidas. Siéntete libre de abrir issues o enviar pull requests para mejorar este proyecto.

---

Desarrollado con ❤️ usando Python y Streamlit.
