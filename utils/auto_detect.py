import requests
from bs4 import BeautifulSoup
from collections import Counter
import re

def detect_page_type(soup):
    """
    Detecta el tipo de página basado en su estructura HTML
    """
    # Detección de e-commerce
    ecommerce_indicators = [
        'cart', 'basket', 'shop', 'product', 'price', 'checkout', 'add-to-cart',
        'buy', 'purchase', 'shopping', 'store', 'order', 'payment'
    ]
    
    # Detección de blog/noticias
    news_indicators = [
        'article', 'blog', 'news', 'post', 'author', 'date', 'published',
        'editorial', 'journalist', 'reporter', 'story', 'opinion'
    ]
    
    # Detección de páginas con tablas de datos
    table_indicators = ['table', 'data', 'statistics', 'chart', 'dataset']
    
    # Contadores de indicadores
    ecommerce_count = 0
    news_count = 0
    table_count = 0
    
    # Buscar en clases, IDs y texto
    page_text = soup.text.lower()
    all_attributes = []
    
    for tag in soup.find_all():
        if tag.attrs:
            for attr, val in tag.attrs.items():
                if isinstance(val, str):
                    all_attributes.append(val.lower())
                elif isinstance(val, list):
                    all_attributes.extend([v.lower() for v in val if isinstance(v, str)])
    
    # Combinar todo el texto y atributos para análisis
    all_text = " ".join(all_attributes) + " " + page_text
    
    # Contar indicadores
    for indicator in ecommerce_indicators:
        ecommerce_count += all_text.count(indicator)
    
    for indicator in news_indicators:
        news_count += all_text.count(indicator)
        
    for indicator in table_indicators:
        table_count += all_text.count(indicator)
        
    # Contar etiquetas específicas
    table_tags = len(soup.find_all('table'))
    article_tags = len(soup.find_all('article'))
    product_elements = len(soup.find_all(class_=re.compile(r'product|item')))
    
    # Ajustar contadores con factores de peso
    table_count += table_tags * 5
    news_count += article_tags * 5
    ecommerce_count += product_elements * 5
    
    # Determinar tipo de página
    if ecommerce_count > news_count and ecommerce_count > table_count:
        return "ecommerce"
    elif news_count > ecommerce_count and news_count > table_count:
        return "news"
    elif table_count > news_count and table_count > ecommerce_count:
        return "data"
    else:
        return "general"

def suggest_selectors(soup, page_type="general"):
    """
    Sugiere selectores CSS basados en el tipo de página
    """
    suggested_tags = {}
    
    # Análisis de clases más comunes
    class_counter = Counter()
    for tag in soup.find_all(True):
        if 'class' in tag.attrs:
            for cls in tag.attrs['class']:
                class_counter[f"{tag.name}.{cls}"] += 1
    
    # Obtener las 10 clases más comunes
    common_classes = [cls for cls, _ in class_counter.most_common(10)]
    
    # Sugerencias específicas según tipo de página
    if page_type == "ecommerce":
        # Buscar elementos que probablemente sean productos
        product_selectors = []
        price_selectors = []
        
        # Buscar elementos de producto
        for tag in soup.find_all(class_=re.compile(r'product|item|card')):
            if tag.name == 'div' or tag.name == 'article' or tag.name == 'li':
                try:
                    class_names = " ".join(tag.attrs.get('class', []))
                    product_selectors.append(f"{tag.name}.{class_names.replace(' ', '.')}")
                except Exception:
                    continue
        
        # Buscar elementos de precio
        price_elements = soup.find_all(class_=re.compile(r'price|cost|amount'))
        for tag in price_elements:
            try:
                class_names = " ".join(tag.attrs.get('class', []))
                selector = f"{tag.name}.{class_names.replace(' ', '.')}"
                price_selectors.append(selector)
            except Exception:
                continue
                
        # Limitar a los 5 más probables
        product_selectors = product_selectors[:5]
        price_selectors = price_selectors[:3]
        
        # Agregar sugerencias específicas para e-commerce
        suggested_tags["div"] = {
            "class": "product", 
            "id": "", 
            "selector": ", ".join(product_selectors) if product_selectors else ".product, .product-item, .item"
        }
        suggested_tags["span"] = {
            "class": "price", 
            "id": "", 
            "selector": ", ".join(price_selectors) if price_selectors else ".price, .product-price"
        }
        suggested_tags["img"] = {
            "class": "", 
            "id": "", 
            "selector": "img.product-image, .product img"
        }
        suggested_tags["a"] = {
            "class": "", 
            "id": "", 
            "selector": "a.product-link, .product a"
        }
    
    elif page_type == "news":
        # Sugerir selectores para artículos de noticias
        suggested_tags["article"] = {"class": "", "id": "", "selector": "article"}
        suggested_tags["h1"] = {"class": "", "id": "", "selector": "h1.title, h1.entry-title"}
        suggested_tags["p"] = {"class": "", "id": "", "selector": "p.entry-content, article p"}
        suggested_tags["time"] = {"class": "", "id": "", "selector": "time, .date, .published"}
    
    elif page_type == "data":
        # Sugerir selectores para tablas de datos
        suggested_tags["table"] = {"class": "", "id": "", "selector": "table"}
        suggested_tags["tr"] = {"class": "", "id": "", "selector": "tr"}
        suggested_tags["th"] = {"class": "", "id": "", "selector": "th"}
        suggested_tags["td"] = {"class": "", "id": "", "selector": "td"}
    
    else:
        # Para páginas generales, usar las etiquetas más comunes
        header_tags = soup.find_all(['h1', 'h2', 'h3'])
        if header_tags:
            suggested_tags["h1"] = {"class": "", "id": "", "selector": "h1"}
        
        paragraphs = soup.find_all('p')
        if paragraphs:
            suggested_tags["p"] = {"class": "", "id": "", "selector": "p"}
            
        links = soup.find_all('a')
        if links:
            suggested_tags["a"] = {"class": "", "id": "", "selector": "a"}
    
    # Agregar algunos selectores comunes basados en análisis de frecuencia
    for selector in common_classes[:3]:
        tag_name = selector.split('.')[0]
        if tag_name not in suggested_tags:
            suggested_tags[tag_name] = {"class": "", "id": "", "selector": selector}
    
    return suggested_tags

def auto_detect_elements(url):
    """
    Función principal para detectar automáticamente elementos relevantes
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Detectar tipo de página
        page_type = detect_page_type(soup)
        
        # Sugerir selectores según el tipo
        suggested_selectors = suggest_selectors(soup, page_type)
        
        return {
            "page_type": page_type,
            "suggested_selectors": suggested_selectors
        }
        
    except Exception as e:
        return {
            "page_type": "unknown",
            "suggested_selectors": {},
            "error": str(e)
        }
