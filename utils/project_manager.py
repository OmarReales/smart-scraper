import json
import os
from datetime import datetime
from pathlib import Path
import pandas as pd

# Directorio para guardar proyectos
PROJECTS_DIR = Path(__file__).parent.parent / "projects"

# Asegurar que existe el directorio de proyectos
if not PROJECTS_DIR.exists():
    PROJECTS_DIR.mkdir(exist_ok=True)

def sanitize_filename(name):
    """Convierte un nombre en un nombre de archivo seguro"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    return name

def save_project(project_data):
    """
    Guarda un proyecto de scraping
    
    project_data debe contener:
    - name: Nombre del proyecto
    - url: URL objetivo
    - tags_info: Información de etiquetas para el scraping
    - use_selenium: Booleano indicando si usar Selenium
    - wait_time: Tiempo de espera para Selenium
    - results: Resultados del scraping (opcional)
    """
    try:
        # Validar datos mínimos
        if not project_data.get("name") or not project_data.get("url"):
            return False, "El proyecto debe tener nombre y URL"
        
        # Crear ID único basado en nombre y fecha
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = sanitize_filename(project_data["name"])
        project_id = f"{safe_name}_{timestamp}"
        
        # Ruta del proyecto
        project_dir = PROJECTS_DIR / project_id
        project_dir.mkdir(exist_ok=True)
        
        # Guardar configuración
        config = {
            "name": project_data["name"],
            "url": project_data["url"],
            "tags_info": project_data["tags_info"],
            "use_selenium": project_data.get("use_selenium", False),
            "wait_time": project_data.get("wait_time", 3),
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        
        with open(project_dir / "config.json", "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        # Guardar resultados si existen
        if "results" in project_data and isinstance(project_data["results"], pd.DataFrame) and not project_data["results"].empty:
            # Guardar en múltiples formatos
            project_data["results"].to_csv(project_dir / "results.csv", index=False)
            project_data["results"].to_excel(project_dir / "results.xlsx", index=False)
            project_data["results"].to_json(project_dir / "results.json", orient="records")
        
        return True, project_id
    
    except Exception as e:
        return False, f"Error al guardar el proyecto: {str(e)}"

def load_project(project_id):
    """
    Carga un proyecto guardado
    """
    try:
        project_dir = PROJECTS_DIR / project_id
        
        if not project_dir.exists():
            return None, f"Proyecto no encontrado: {project_id}"
        
        # Cargar configuración
        with open(project_dir / "config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        
        # Cargar resultados si existen
        results = None
        results_path = project_dir / "results.csv"
        if results_path.exists():
            results = pd.read_csv(results_path)
        
        # Combinar todo en un diccionario
        project_data = {**config, "results": results, "project_id": project_id}
        return project_data, None
    
    except Exception as e:
        return None, f"Error al cargar el proyecto: {str(e)}"

def list_projects():
    """
    Lista todos los proyectos guardados
    """
    projects = []
    
    try:
        for project_dir in PROJECTS_DIR.iterdir():
            if project_dir.is_dir() and (project_dir / "config.json").exists():
                try:
                    with open(project_dir / "config.json", "r", encoding="utf-8") as f:
                        config = json.load(f)
                    
                    has_results = (project_dir / "results.csv").exists()
                    
                    project_info = {
                        "id": project_dir.name,
                        "name": config.get("name", "Sin nombre"),
                        "url": config.get("url", ""),
                        "created_at": config.get("created_at", ""),
                        "last_updated": config.get("last_updated", ""),
                        "has_results": has_results
                    }
                    projects.append(project_info)
                except Exception as e:
                    print(f"Error loading project {project_dir.name}: {e}")
    except Exception as e:
        print(f"Error accessing projects directory: {e}")
    
    # Ordenar por fecha de actualización (más recientes primero)
    projects.sort(key=lambda x: x.get("last_updated", ""), reverse=True)
    
    return projects

def delete_project(project_id):
    """
    Elimina un proyecto guardado
    """
    try:
        project_dir = PROJECTS_DIR / project_id
        
        if not project_dir.exists():
            return False, f"Proyecto no encontrado: {project_id}"
        
        # Eliminar archivos del proyecto
        for file in project_dir.iterdir():
            file.unlink()
        
        # Eliminar directorio
        project_dir.rmdir()
        
        return True, f"Proyecto {project_id} eliminado correctamente"
    
    except Exception as e:
        return False, f"Error al eliminar el proyecto: {str(e)}"

def update_project(project_id, project_data):
    """
    Actualiza un proyecto existente
    """
    try:
        project_dir = PROJECTS_DIR / project_id
        
        if not project_dir.exists():
            return False, f"Proyecto no encontrado: {project_id}"
        
        # Cargar configuración existente
        with open(project_dir / "config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        
        # Actualizar campos permitidos
        for field in ["name", "url", "tags_info", "use_selenium", "wait_time"]:
            if field in project_data:
                config[field] = project_data[field]
        
        # Actualizar timestamp
        config["last_updated"] = datetime.now().isoformat()
        
        # Guardar configuración actualizada
        with open(project_dir / "config.json", "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        # Actualizar resultados si se proporcionan
        if "results" in project_data and isinstance(project_data["results"], pd.DataFrame) and not project_data["results"].empty:
            project_data["results"].to_csv(project_dir / "results.csv", index=False)
            project_data["results"].to_excel(project_dir / "results.xlsx", index=False)
            project_data["results"].to_json(project_dir / "results.json", orient="records")
        
        return True, f"Proyecto {project_id} actualizado correctamente"
    
    except Exception as e:
        return False, f"Error al actualizar el proyecto: {str(e)}"
