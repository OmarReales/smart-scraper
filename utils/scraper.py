import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time as wait_module  # Renombramos la importación para evitar problemas
import os
import platform
import logging

# Configurar el logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ruta para navegadores basados en Chromium
def find_chromium_based_browsers():
    """Busca navegadores basados en Chromium instalados en el sistema"""
    system = platform.system()
    browsers = {}
    
    if system == "Windows":
        # Ubicaciones comunes en Windows para diferentes navegadores
        browser_paths = {
            "Chrome": [
                os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
                os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
                os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
            ],
            "Edge": [
                os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
                os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
            ],
            "Brave": [
                os.path.expandvars(r"%ProgramFiles%\BraveSoftware\Brave-Browser\Application\brave.exe"),
                os.path.expandvars(r"%LocalAppData%\BraveSoftware\Brave-Browser\Application\brave.exe"),
            ],
            "Opera": [
                os.path.expandvars(r"%ProgramFiles%\Opera\launcher.exe"),
                os.path.expandvars(r"%ProgramFiles(x86)%\Opera\launcher.exe"),
                os.path.expandvars(r"%LocalAppData%\Programs\Opera\launcher.exe"),
            ],
            "Vivaldi": [
                os.path.expandvars(r"%ProgramFiles%\Vivaldi\Application\vivaldi.exe"),
                os.path.expandvars(r"%LocalAppData%\Vivaldi\Application\vivaldi.exe"),
            ]
        }
    
    elif system == "Darwin":  # macOS
        browser_paths = {
            "Chrome": ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"],
            "Edge": ["/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"],
            "Brave": ["/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"],
            "Opera": ["/Applications/Opera.app/Contents/MacOS/Opera"],
            "Vivaldi": ["/Applications/Vivaldi.app/Contents/MacOS/Vivaldi"]
        }
    
    elif system == "Linux":
        # En Linux intentamos usar 'which' para encontrar los navegadores
        browser_cmds = {
            "Chrome": ["google-chrome", "google-chrome-stable"],
            "Chromium": ["chromium", "chromium-browser"],
            "Edge": ["microsoft-edge"],
            "Brave": ["brave-browser"],
            "Opera": ["opera"],
            "Vivaldi": ["vivaldi"]
        }
        
        import subprocess
        for browser_name, commands in browser_cmds.items():
            for cmd in commands:
                try:
                    path = subprocess.check_output(["which", cmd], stderr=subprocess.DEVNULL).decode("utf-8").strip()
                    if path:
                        browsers[browser_name] = path
                        break
                except:
                    pass
        
        return browsers

    # Para Windows y macOS, verificar cada ruta
    for browser_name, paths in browser_paths.items():
        for path in paths:
            if os.path.exists(path):
                browsers[browser_name] = path
                break
    
    return browsers

def extract_element_data(elem, tag):
    """Extrae datos específicos basados en el tipo de etiqueta"""
    data = {
        "Contenido": elem.get_text(strip=True),
        "HTML": str(elem)
    }
    
    # Extraer atributos específicos según el tipo de etiqueta
    if tag == 'a':
        data["href"] = elem.get('href', '')
        data["texto_enlace"] = elem.get_text(strip=True)
    
    elif tag == 'img':
        data["src"] = elem.get('src', '')
        data["alt"] = elem.get('alt', '')
        
    elif tag in ['input', 'button', 'select']:
        data["name"] = elem.get('name', '')
        data["value"] = elem.get('value', '')
        data["type"] = elem.get('type', '')
        
    elif tag == 'meta':
        data["name"] = elem.get('name', '')
        data["content"] = elem.get('content', '')
        
    elif tag in ['tr', 'th', 'td']:
        # Para elementos de tabla, intentar obtener la fila/columna
        parent = elem.find_parent('table')
        if parent:
            if tag == 'tr':
                data["fila_num"] = len(elem.find_previous_siblings('tr')) + 1
            else:
                data["columna_num"] = len(elem.find_previous_siblings()) + 1
    
    return data

def scrape_website_static(url, tags_info):
    """Scrape website using requests and BeautifulSoup (for static content)"""
    try:
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")
        
        data = []
        for tag, attrs in tags_info.items():
            try:
                if attrs['selector']:
                    elements = soup.select(attrs['selector'])
                else:
                    elements = soup.find_all(tag, class_=attrs['class'] or None, id=attrs['id'] or None)
                
                for elem in elements:
                    elem_data = extract_element_data(elem, tag)
                    elem_data["Etiqueta"] = tag
                    data.append(elem_data)
                    
            except Exception as e:
                print(f"Error processing tag '{tag}': {e}")
        
        df = pd.DataFrame(data) if data else pd.DataFrame(columns=["Etiqueta", "Contenido", "HTML"])
        
        # Reorganizar columnas para poner Etiqueta y Contenido primero
        if not df.empty:
            cols = df.columns.tolist()
            cols = ['Etiqueta', 'Contenido'] + [c for c in cols if c not in ['Etiqueta', 'Contenido']]
            df = df[cols]
            
        return df
    except requests.exceptions.RequestException as e:
        return f"Error de conexión: {e}"
    except Exception as e:
        return f"Error inesperado: {e}"

def scrape_website_dynamic(url, tags_info, wait_time=3):
    """Scrape website using Selenium with any available Chromium-based browser"""
    try:
        # Opciones estándar para navegadores Chromium
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        # Encontrar navegadores disponibles
        browsers = find_chromium_based_browsers()
        if browsers:
            browser_names = list(browsers.keys())
            logger.info(f"Navegadores encontrados: {browser_names}")
            
            # Usar el primer navegador encontrado
            first_browser = browser_names[0]
            browser_path = browsers[first_browser]
            logger.info(f"Usando navegador: {first_browser} en {browser_path}")
            
            # Establecer la ubicación del binario
            chrome_options.binary_location = browser_path
        else:
            logger.warning("No se encontraron navegadores Chromium instalados. Usando configuración predeterminada.")
        
        # Intentar iniciar el WebDriver con diferentes enfoques
        driver = None
        error_messages = []

        # Intentar con Chrome
        try:
            logger.info("Intentando con ChromeDriver...")
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("ChromeDriver iniciado correctamente")
        except Exception as e:
            error_messages.append(f"Error con ChromeDriver: {e}")
            
            # Intentar con Edge si falló Chrome y está disponible
            if "Edge" in browsers:
                try:
                    logger.info("Intentando con EdgeDriver...")
                    from selenium.webdriver.edge.service import Service as EdgeService
                    from webdriver_manager.microsoft import EdgeChromiumDriverManager
                    
                    edge_service = EdgeService(EdgeChromiumDriverManager().install())
                    driver = webdriver.Edge(service=edge_service, options=chrome_options)
                    logger.info("EdgeDriver iniciado correctamente")
                except Exception as edge_e:
                    error_messages.append(f"Error con EdgeDriver: {edge_e}")
        
        # Si no se pudo inicializar el driver
        if not driver:
            browsers_str = ", ".join(browsers.keys()) if browsers else "ninguno"
            error_msg = f"No se pudo iniciar ningún navegador. Navegadores disponibles: {browsers_str}.\n"
            error_msg += "Errores:\n" + "\n".join(error_messages)
            error_msg += "\n\nSoluciones posibles:\n"
            error_msg += "1. Instalar Google Chrome, Microsoft Edge u otro navegador basado en Chromium\n"
            error_msg += "2. Usar el modo estático (sin usar Selenium)\n"
            error_msg += "3. Verificar la instalación de los controladores WebDriver"
            
            logger.error(error_msg)
            return error_msg
        
        # Continuar con el scraping si tenemos un driver
        try:
            logger.info(f"Navegando a URL: {url}")
            driver.get(url)
            
            # Esperar explícitamente para que cargue la página
            logger.info(f"Esperando {wait_time} segundos para que la página cargue...")
            wait_module.sleep(wait_time)
            
            # Obtener el código HTML y parsearlo con BeautifulSoup
            soup = BeautifulSoup(driver.page_source, "lxml")
            
            data = []
            for tag, attrs in tags_info.items():
                try:
                    if attrs['selector']:
                        elements = soup.select(attrs['selector'])
                    else:
                        elements = soup.find_all(tag, class_=attrs['class'] or None, id=attrs['id'] or None)
                    
                    for elem in elements:
                        elem_data = extract_element_data(elem, tag)
                        elem_data["Etiqueta"] = tag
                        data.append(elem_data)
                        
                except Exception as e:
                    logger.error(f"Error procesando etiqueta '{tag}': {e}")
            
            # Cerrar el navegador
            driver.quit()
            
            df = pd.DataFrame(data) if data else pd.DataFrame(columns=["Etiqueta", "Contenido", "HTML"])
            
            # Reorganizar columnas para poner Etiqueta y Contenido primero
            if not df.empty:
                cols = df.columns.tolist()
                cols = ['Etiqueta', 'Contenido'] + [c for c in cols if c not in ['Etiqueta', 'Contenido']]
                df = df[cols]
                
            return df
        
        except Exception as e:
            # Asegurarse de cerrar el driver si ocurre un error
            try:
                driver.quit()
            except:
                pass
            logger.error(f"Error durante el scraping: {e}")
            return f"Error durante el scraping: {e}"
            
    except Exception as e:
        logger.error(f"Error general: {e}")
        return f"Error general: {e}"
