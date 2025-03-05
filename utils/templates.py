import json
import os
from pathlib import Path

# Directorio para guardar plantillas personalizadas
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

# Asegurar que existe el directorio de plantillas
if not TEMPLATES_DIR.exists():
    TEMPLATES_DIR.mkdir(exist_ok=True)

# Plantillas predefinidas para casos de uso comunes
DEFAULT_TEMPLATES = {
    "productos_ecommerce": {
        "name": "Productos E-commerce",
        "description": "Extrae información de productos (nombre, precio, imagen) de tiendas online",
        "tags": {
            "div": {"class": "product", "id": "", "selector": ".product, .product-item, .item, .product-card"},
            "h1": {"class": "", "id": "", "selector": "h1.product-title, h1.name"},
            "h2": {"class": "", "id": "", "selector": "h2.product-name"},
            "span": {"class": "price", "id": "", "selector": ".price, .product-price, span.price"},
            "img": {"class": "", "id": "", "selector": "img.product-image"},
            "a": {"class": "", "id": "", "selector": "a.product-link"}
        },
        "use_selenium": True,
        "wait_time": 3
    },
    "articulos_noticias": {
        "name": "Artículos y Noticias",
        "description": "Extrae titulares, contenido y metadatos de noticias y blogs",
        "tags": {
            "article": {"class": "", "id": "", "selector": "article"},
            "h1": {"class": "", "id": "", "selector": "h1.entry-title, h1.title"},
            "h2": {"class": "", "id": "", "selector": "h2.entry-title, h2.subtitle"},
            "p": {"class": "", "id": "", "selector": "p.entry-content, .article-body p"},
            "time": {"class": "", "id": "", "selector": "time, .date, .published"},
            "img": {"class": "", "id": "", "selector": "img.featured-image"},
            "a": {"class": "", "id": "", "selector": "a.author-link"}
        },
        "use_selenium": False,
        "wait_time": 2
    },
    "tablas_datos": {
        "name": "Tablas de Datos",
        "description": "Extrae información estructurada de tablas HTML",
        "tags": {
            "table": {"class": "", "id": "", "selector": "table"},
            "tr": {"class": "", "id": "", "selector": "tr"},
            "th": {"class": "", "id": "", "selector": "th"},
            "td": {"class": "", "id": "", "selector": "td"}
        },
        "use_selenium": False,
        "wait_time": 2
    },
    "listas_elementos": {
        "name": "Listas de Elementos",
        "description": "Extrae elementos de listas ordenadas y no ordenadas",
        "tags": {
            "ul": {"class": "", "id": "", "selector": "ul"},
            "ol": {"class": "", "id": "", "selector": "ol"},
            "li": {"class": "", "id": "", "selector": "li"}
        },
        "use_selenium": False,
        "wait_time": 2
    }
}

def get_default_templates():
    """Obtiene las plantillas predefinidas"""
    return DEFAULT_TEMPLATES

def get_custom_templates():
    """Carga plantillas personalizadas guardadas por el usuario"""
    custom_templates = {}
    
    try:
        for template_file in TEMPLATES_DIR.glob("*.json"):
            try:
                with open(template_file, "r", encoding="utf-8") as f:
                    template_data = json.load(f)
                    template_id = template_file.stem
                    custom_templates[template_id] = template_data
            except Exception as e:
                print(f"Error loading template {template_file}: {e}")
    except Exception as e:
        print(f"Error accessing templates directory: {e}")
        
    return custom_templates

def save_custom_template(template_id, template_data):
    """Guarda una plantilla personalizada"""
    try:
        # Asegurar que existe el directorio
        TEMPLATES_DIR.mkdir(exist_ok=True)
        
        # Guardar la plantilla como JSON
        template_path = TEMPLATES_DIR / f"{template_id}.json"
        with open(template_path, "w", encoding="utf-8") as f:
            json.dump(template_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving template: {e}")
        return False

def delete_custom_template(template_id):
    """Elimina una plantilla personalizada"""
    try:
        template_path = TEMPLATES_DIR / f"{template_id}.json"
        if template_path.exists():
            template_path.unlink()
            return True
        return False
    except Exception as e:
        print(f"Error deleting template: {e}")
        return False

def get_all_templates():
    """Combina las plantillas predefinidas y personalizadas"""
    templates = get_default_templates()
    custom = get_custom_templates()
    
    # Evitar sobrescribir plantillas predefinidas
    for template_id, template_data in custom.items():
        if template_id not in templates:
            templates[template_id] = template_data
            
    return templates
