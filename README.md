# 🕷️ Smart Scraper IA

Una herramienta interactiva para extraer datos de sitios web con asistencia de inteligencia artificial.

![Smart Scraper IA](https://img.shields.io/badge/Smart%20Scraper-IA-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.25%2B-red)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Active-success)

## 📚 Índice

- [📋 Descripción](#-descripción)
- [✨ Características principales](#-características-principales)
- [🔍 Capturas de pantalla](#-capturas-de-pantalla)
- [🗂️ Estructura del proyecto](#️-estructura-del-proyecto)
- [🛠️ Requisitos e instalación](#️-requisitos-e-instalación)
- [⚙️ Configuración](#️-configuración)
- [🚀 Uso](#-uso)
- [🧩 Plantillas predefinidas](#-plantillas-predefinidas)
- [🧠 Modelos de IA disponibles](#-modelos-de-ia-disponibles)
- [📱 Compatibilidad móvil](#-compatibilidad-móvil)
- [🎯 Ejemplos de uso práctico](#-ejemplos-de-uso-práctico)
- [❓ Solución de problemas](#-solución-de-problemas)
- [🔜 Próximas mejoras](#-próximas-mejoras)
- [📄 Licencia](#-licencia)
- [👥 Contribuciones](#-contribuciones)

## 📋 Descripción

Smart Scraper IA es una aplicación que combina web scraping con inteligencia artificial para facilitar la extracción y análisis de datos de páginas web. Con una interfaz intuitiva construida en Streamlit, permite seleccionar elementos HTML específicos, extraer su contenido, y luego analizar los resultados utilizando modelos de IA como Gemini, ChatGPT y Groq.

A diferencia de otras herramientas de scraping, Smart Scraper IA ofrece:

- Asistencia de IA para interpretar y transformar datos
- Autodetección inteligente de elementos basada en patrones comunes
- Una interfaz visual accesible sin necesidad de programación

## ✨ Características principales

- **🧙‍♂️ Extracción de datos simplificada**: Selección intuitiva de elementos HTML mediante etiquetas, clases, IDs o selectores CSS
- **🔍 Autodetección inteligente**: Detecta automáticamente elementos relevantes según el tipo de página
- **📋 Plantillas predefinidas**: Usa plantillas para diferentes tipos de sitios web como e-commerce, noticias, o tablas de datos
- **💾 Gestión de proyectos**: Guarda y reutiliza tus proyectos de extracción para uso futuro
- **⚡ Soporte para páginas dinámicas**: Extrae contenido de sitios con JavaScript usando Selenium y detección automática de navegadores
- **🤖 Múltiples modelos de IA**: Compatibilidad con Gemini (Google), ChatGPT (OpenAI) y una amplia variedad de modelos Groq (Llama 3.3, Gemma 2, etc.)
- **📱 Interfaz responsiva**: Diseñada para funcionar en dispositivos móviles y de escritorio
- **📊 Exportación flexible**: Guarda los resultados en CSV, JSON o Excel
- **🧠 Análisis inteligente**: Obtén insights sobre los datos extraídos mediante IA
- **🔄 Filtrado y búsqueda**: Herramientas para refinar los resultados después de la extracción

## 🔍 Capturas de pantalla

<details>
<summary>Ver capturas de pantalla</summary>

_Próximamente: Capturas de pantalla que muestran la interfaz y ejemplos de uso._

<!-- Capturas de pantalla aca -->
<!-- ![Interfaz principal](./img/screenshot1.png) -->
<!-- ![Resultados del scraping](./img/screenshot2.png) -->
<!-- ![Análisis con IA](./img/screenshot3.png) -->

</details>

## 🗂️ Estructura del proyecto

```
/smart-scraper/
├── main.py                      # Aplicación principal de Streamlit
├── requirements.txt             # Dependencias del proyecto
├── README.md                    # Documentación
├── .streamlit/                  # Configuración de Streamlit
│   └── secrets.toml             # Claves API secretas (debes crear este archivo)
└── utils/                       # Módulos auxiliares
    ├── __init__.py              # Inicialización del paquete
    ├── ai_helpers.py            # Funciones para interacción con IA
    ├── auto_detect.py           # Funciones para autodetección de elementos
    ├── project_manager.py       # Gestión de proyectos guardados
    ├── scraper.py               # Funciones de web scraping
    ├── templates.py             # Plantillas predefinidas para tipos de sitios web
    └── validators.py            # Validadores y utilidades
```

## 🛠️ Requisitos e instalación

### Prerrequisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Un navegador basado en Chromium:
  - Google Chrome
  - Microsoft Edge
  - Brave
  - Opera
  - Vivaldi

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

Para utilizar las funciones de IA, necesitas configurar las claves API:

#### Opción 1: Archivo de secretos (recomendado)

1. Crea el directorio `.streamlit` en la raíz del proyecto si no existe
2. Crea un archivo `.streamlit/secrets.toml` con tus claves API:

```toml
GROQ_API_KEY = "tu-clave-api-de-groq"
GENAI_API_KEY = "tu-clave-api-de-google-gemini"
OPENAI_API_KEY = "tu-clave-api-de-openai"
```

#### Opción 2: Interfaz de usuario

Puedes ingresar tus claves API directamente en la aplicación a través de la sección de Configuración en el menú lateral.

### Dónde obtener las claves API:

- **OpenAI (ChatGPT)**: [platform.openai.com](https://platform.openai.com/)
- **Google (Gemini)**: [ai.google.dev](https://ai.google.dev/)
- **Groq**: [console.groq.com](https://console.groq.com/)

## 🚀 Uso

Para ejecutar la aplicación:

```bash
streamlit run main.py
```

Esto abrirá la interfaz de usuario en tu navegador (normalmente en http://localhost:8501).

### Guía paso a paso

1. **Configuración inicial**

   - Ingresa tus claves API en la sección de Configuración
   - Selecciona si deseas usar Selenium para contenido dinámico

2. **Selección de URL**

   - Ingresa la URL completa del sitio web que deseas analizar
   - Verifica que la URL sea válida (debe comenzar con http:// o https://)

3. **Selección de elementos**

   - Usa la autodetección para identificar elementos automáticamente, o
   - Selecciona manualmente las etiquetas HTML que deseas extraer
   - Para cada etiqueta, puedes especificar:
     - Clase CSS
     - ID
     - Selector CSS personalizado (más avanzado)

4. **Ejecución del scraping**

   - Haz clic en "EJECUTAR SCRAPING"
   - Espera a que se complete el proceso

5. **Exploración de resultados**

   - Usa los filtros para refinar los resultados:
     - Filtrar por tipo de etiqueta
     - Buscar texto específico
   - Explora los datos en formato tabular

6. **Análisis con IA**

   - Selecciona la pestaña "IA" y luego:
     - "Preguntar" para hacer consultas generales
     - "Analizar" para interpretar los datos extraídos
   - Selecciona el modelo de IA que deseas utilizar

7. **Exportación y guardado**
   - Exporta los datos en formato CSV o JSON
   - Guarda el proyecto para uso futuro

## 🧩 Plantillas predefinidas

Smart Scraper IA incluye plantillas predefinidas para tipos comunes de sitios web:

- **🛒 Productos de E-commerce**: Extrae nombres, precios e imágenes de productos
- **📰 Artículos y Noticias**: Extrae titulares, fechas y contenido de artículos
- **📊 Tablas de Datos**: Optimizada para extraer datos tabulares
- **📋 Listas de Elementos**: Para extracción eficiente de listas

### Personalización de plantillas

Puedes crear tus propias plantillas:

1. Configura los elementos que deseas extraer
2. Ve a la sección "Plantillas" en el menú lateral
3. Haz clic en "Guardar plantilla actual"
4. Asigna un nombre y descripción a tu plantilla

Las plantillas personalizadas se guardarán para uso futuro.

## 🧠 Modelos de IA disponibles

### OpenAI (ChatGPT)

- GPT-3.5 Turbo (recomendado para uso general)
- GPT-4o (más potente, mejor comprensión)
- GPT-4 Turbo (alto rendimiento)

### Groq

- Llama 3.3 70B Versatile (recomendado, gran capacidad)
- Llama 3.1 8B Instant (rápido)
- Gemma 2 9B (buen equilibrio)
- Mixtral 8x7B (alta capacidad)

### Google (Gemini)

- Gemini 2.0 Flash (recomendado)
- Gemini 1.5 Pro (alta capacidad)
- Gemini Pro (estable)

Cada modelo tiene diferentes capacidades y límites de tokens. La aplicación selecciona automáticamente los parámetros óptimos según el modelo elegido.

## 📱 Compatibilidad móvil

Smart Scraper IA está diseñado para funcionar en dispositivos móviles:

- **Modo Compacto**: Optimizado para pantallas pequeñas, con controles adaptados para uso táctil
- **Modo Expandido**: Aprovecha pantallas más grandes con vista detallada
- **Diseño responsivo**: Se adapta automáticamente a diferentes tamaños de pantalla

Para alternar entre modos, usa el selector "Modo de visualización" en la barra lateral.

## 🎯 Ejemplos de uso práctico

### Monitoreo de precios

```
URL: https://www.tienda-ejemplo.com/productos
Elementos: div.product, span.price
Resultado: Lista de precios para seguimiento
```

### Extracción de noticias

```
URL: https://www.portal-noticias.com
Elementos: article, h2.title, p.summary, span.date
Resultado: Feed personalizado de noticias
```

### Investigación de mercado

```
URL: https://www.comparador-productos.com
Elementos: table, tr, td.spec, span.rating
Resultado: Tabla comparativa de productos y calificaciones
```

### Extracción de información de contacto

```
URL: https://www.directorio-empresas.com
Elementos: div.company-card, span.phone, a.email
Resultado: Base de datos de contactos empresariales
```

### Seguimiento de estadísticas

```
URL: https://www.datos-deportes.com/estadisticas
Elementos: table.stats, tr, th, td
Resultado: Datos estadísticos para análisis
```

## ❓ Solución de problemas

### Problemas comunes y soluciones

| Problema                              | Solución                                                                   |
| ------------------------------------- | -------------------------------------------------------------------------- |
| **No se detecta el navegador**        | Instala Chrome, Edge, Brave u otro navegador compatible con Chromium       |
| **Error con Selenium**                | Aumenta el tiempo de espera en la configuración avanzada                   |
| **No se extraen elementos dinámicos** | Activa la opción "Usar Selenium" en configuración avanzada                 |
| **Error de API key inválida**         | Verifica que la clave API esté activa y correctamente escrita              |
| **Datos incompletos**                 | Refina los selectores CSS para ser más específicos                         |
| **Límite de tokens excedido**         | Reduce la cantidad de datos a analizar o usa un modelo con mayor capacidad |
| **La aplicación es lenta**            | Desactiva Selenium si no es necesario para contenido estático              |

Para problemas no listados, considera revisar la [documentación de Streamlit](https://docs.streamlit.io/) o [crear un issue](https://github.com/OmarReales/smart-scraper/issues).

## 🔜 Próximas mejoras

Características planeadas para futuras versiones:

- [ ] **🔄 Extracción programada**: Configuración de scrapers que se ejecuten automáticamente
- [ ] **📊 Visualización avanzada**: Gráficos y dashboards para analizar datos extraídos
- [ ] **🔗 Navegación por paginación**: Soporte para extraer datos de múltiples páginas
- [ ] **🔐 Manejo de autenticación**: Soporte para scraping de sitios que requieren login
- [ ] **🌐 Proxy rotativo**: Mayor robustez para scraping a gran escala
- [ ] **📲 Aplicación nativa**: Versiones para dispositivos móviles
- [ ] **🧪 Entorno de pruebas**: Para probar y depurar selectores antes del scraping
- [ ] **🔄 Sincronización en la nube**: Guardar proyectos y resultados en servicios de almacenamiento

## 📄 Licencia

Este proyecto está licenciado bajo la licencia MIT. Ver el archivo LICENSE para más detalles.

## 👥 Contribuciones

Las contribuciones son bienvenidas. Para contribuir:

1. Haz un fork del repositorio
2. Crea una nueva rama (`git checkout -b feature/amazing-feature`)
3. Realiza tus cambios
4. Haz commit de tus cambios (`git commit -m 'Add some amazing feature'`)
5. Sube tus cambios (`git push origin feature/amazing-feature`)
6. Abre un Pull Request

### Áreas de contribución

- Mejoras en la detección automática
- Optimización del manejo de tokens en los modelos de IA
- Mejoras en la interfaz de usuario
- Documentación y ejemplos
- Soporte para más navegadores

---

Desarrollado con ❤️ usando Python y Streamlit.

¿Tienes preguntas o comentarios? Abre un issue o contáctame.
