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
    """Scrape website using Selenium (for dynamic content)"""
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        driver.get(url)
        
        # Esperar explícitamente para que cargue la página
        print(f"Esperando {wait_time} segundos para que la página cargue...")
        wait_module.sleep(wait_time)  # Usamos el módulo renombrado
        
        # Get the page source and parse with BeautifulSoup
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
                print(f"Error processing tag '{tag}': {e}")
        
        driver.quit()
        
        df = pd.DataFrame(data) if data else pd.DataFrame(columns=["Etiqueta", "Contenido", "HTML"])
        
        # Reorganizar columnas para poner Etiqueta y Contenido primero
        if not df.empty:
            cols = df.columns.tolist()
            cols = ['Etiqueta', 'Contenido'] + [c for c in cols if c not in ['Etiqueta', 'Contenido']]
            df = df[cols]
            
        return df
    except Exception as e:
        return f"Error: {e}"
