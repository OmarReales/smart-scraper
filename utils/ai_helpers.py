import logging
import pandas as pd
import openai
from groq import Groq
import google.generativeai as genai
import re
import time
from functools import lru_cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lista de modelos de Groq disponibles
GROQ_MODELS = {
    "llama-3.3-70b-versatile": "Llama 3.3 70B Versatile (Recomendado)",
    "llama-3.1-8b-instant": "Llama 3.1 8B Instant (Rápido)",
    "llama3-70b-8192": "Llama 3 70B",
    "llama3-8b-8192": "Llama 3 8B",
    "gemma2-9b-it": "Gemma 2 9B",
    "mixtral-8x7b-32768": "Mixtral 8x7B",
    "llama-guard-3-8b": "Llama Guard 3 8B"
}

# Lista de modelos de OpenAI disponibles
OPENAI_MODELS = {
    "gpt-3.5-turbo": "GPT-3.5 Turbo (Recomendado)",
    "gpt-4o": "GPT-4o (Más potente)",
    "gpt-4-turbo": "GPT-4 Turbo",
    "gpt-4": "GPT-4 (Original)",
    "gpt-3.5-turbo-instruct": "GPT-3.5 Turbo Instruct"
}

# Lista de modelos de Gemini disponibles
GEMINI_MODELS = {
    "gemini-2.0-flash": "Gemini 2.0 Flash (Recomendado)",
    "gemini-1.5-pro": "Gemini 1.5 Pro",
    "gemini-1.5-flash": "Gemini 1.5 Flash (Rápido)",
    "gemini-pro": "Gemini Pro (Estable)",
    "gemini-pro-vision": "Gemini Pro Vision"
}

# Diccionario con límites de tokens aproximados por modelo
TOKEN_LIMITS = {
    # OpenAI
    "gpt-3.5-turbo": 16000,
    "gpt-4o": 128000,
    "gpt-4-turbo": 128000,
    "gpt-4": 8000,
    "gpt-3.5-turbo-instruct": 4000,
    # Groq - Reduciendo límites para mayor seguridad
    "llama-3.3-70b-versatile": 25000,  # Más conservador que los 32K teóricos
    "llama-3.1-8b-instant": 7000,      # Más conservador que los 8K teóricos
    "llama3-70b-8192": 7000,
    "llama3-8b-8192": 7000,
    "gemma2-9b-it": 7000,
    "mixtral-8x7b-32768": 28000,       # Más conservador que los 32K teóricos
    "llama-guard-3-8b": 7000,
    # Gemini
    "gemini-2.0-flash": 32000,
    "gemini-1.5-pro": 100000,  
    "gemini-1.5-flash": 32000,
    "gemini-pro": 32000,
    "gemini-pro-vision": 16000
}

def estimate_tokens(text):
    """
    Estima aproximadamente la cantidad de tokens en un texto.
    Esta es una estimación aproximada basada en el número de caracteres.
    Se usa un factor de seguridad para evitar subestimaciones.
    """
    # Un token es aproximadamente 4 caracteres en inglés/español
    # Aplicamos un factor de seguridad de 1.2 para evitar subestimaciones
    return int(len(text) // 3.5)  # Más conservador que 4 caracteres por token

@lru_cache(maxsize=8)  # Caché para evitar múltiples verificaciones
def validate_api_key(api_type, api_key):
    """
    Valida si una API key es válida haciendo una solicitud mínima.
    Retorna (válido, mensaje)
    """
    if not api_key:
        return False, "No se proporcionó API key"
    
    try:
        if api_type == "openai":
            client = openai.OpenAI(api_key=api_key)
            # Usamos una solicitud pequeña para validar
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return True, "API key válida"
            
        elif api_type == "groq":
            client = Groq(api_key=api_key)
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": "test"}],
                model="llama-3.1-8b-instant",
                max_tokens=5
            )
            return True, "API key válida"
            
        elif api_type == "gemini":
            genai.configure(api_key=api_key)
            # Cambiar a gemini-2.0-flash que es el modelo recomendado
            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content("test", generation_config={"max_output_tokens": 5})
            return True, "API key válida"
            
    except Exception as e:
        error_msg = str(e).lower()
        
        # Detectar errores específicos de API key
        if "api key" in error_msg and ("invalid" in error_msg or "incorrect" in error_msg):
            return False, f"API key inválida: {e}"
        elif "auth" in error_msg or "authent" in error_msg:
            return False, f"Error de autenticación: {e}"
        # Añadir caso específico para modelo no encontrado de Gemini
        elif "not found" in error_msg and "model" in error_msg:
            return False, f"Error: modelo no encontrado o no compatible con tu API key. {str(e)}"
        else:
            return False, f"Error validando API key: {e}"
    
    return True, "API key válida"

def truncate_content(content, max_tokens):
    """
    Trunca el contenido para que esté dentro del límite de tokens.
    Preserva el principio y final del contenido.
    """
    estimated_tokens = estimate_tokens(content)
    
    # Si está dentro del límite, devolver tal cual
    if estimated_tokens <= max_tokens:
        return content
    
    # Reservar tokens para el mensaje de truncado
    truncation_msg = "\n[...CONTENIDO TRUNCADO...]\n"
    truncation_tokens = estimate_tokens(truncation_msg)
    
    # Calcular cuánto texto conservar del principio y del final
    available_tokens = max_tokens - truncation_tokens
    start_tokens = available_tokens * 2 // 3  # 2/3 del contenido al principio
    end_tokens = available_tokens - start_tokens  # 1/3 del contenido al final
    
    # Convertir tokens a caracteres aproximados
    start_chars = start_tokens * 4
    end_chars = end_tokens * 4
    
    # Truncar preservando inicio y fin
    truncated = content[:start_chars] + truncation_msg + content[-end_chars:]
    
    return truncated

def ask_chatgpt(prompt, api_key, model_name="gpt-3.5-turbo", retries=1):
    """Ask a question to ChatGPT API with selected model"""
    if not api_key:
        return "Por favor, ingresa tu ChatGPT API Key en la configuración."
    
    # Validar API key primero
    is_valid, message = validate_api_key("openai", api_key)
    if not is_valid:
        return f"Error de API: {message}"
    
    try:
        # Verificar límite de tokens y truncar si es necesario
        max_tokens = TOKEN_LIMITS.get(model_name, 4000)
        estimated_tokens = estimate_tokens(prompt)
        
        if estimated_tokens > max_tokens * 0.9:  # Usar 90% como límite seguro
            logger.warning(f"Prompt demasiado largo: ~{estimated_tokens} tokens. Truncando...")
            prompt = truncate_content(prompt, int(max_tokens * 0.9))
            logger.info(f"Prompt truncado a ~{estimate_tokens(prompt)} tokens")
        
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "Eres un experto en web scraping."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
        
    except openai.BadRequestError as e:
        error_msg = str(e).lower()
        
        # Error de token limit
        if "token" in error_msg and ("exceed" in error_msg or "limit" in error_msg):
            if retries > 0:
                logger.warning(f"Error de límite de tokens: {e}. Reintentando con un prompt más pequeño...")
                # Reducir aún más el tamaño del prompt
                shortened_prompt = truncate_content(prompt, int(max_tokens * 0.7))
                return ask_chatgpt(shortened_prompt, api_key, model_name, retries-1)
            else:
                return f"Error: El contenido es demasiado largo para el modelo {model_name}. Por favor, reduce la cantidad de datos o usa un modelo con mayor capacidad."
        
        # Otros errores de solicitud
        return f"Error con la API de ChatGPT: {e}"
        
    except Exception as e:
        logger.error(f"Error en ChatGPT API con modelo {model_name}: {e}")
        return f"Error con la API de ChatGPT (modelo {model_name}): {str(e)}"

def ask_groq(prompt, api_key, model_name="llama-3.3-70b-versatile", retries=1):
    """Ask a question to Groq API with selected model"""
    if not api_key:
        return "Por favor, ingresa tu Groq API Key en la configuración."
    
    # Validar API key primero
    is_valid, message = validate_api_key("groq", api_key)
    if not is_valid:
        return f"Error de API: {message}"
    
    try:
        # Verificar límite de tokens y truncar si es necesario
        max_tokens = TOKEN_LIMITS.get(model_name, 8000)
        estimated_tokens = estimate_tokens(prompt)
        
        logger.info(f"Estimación de tokens para solicitud a Groq ({model_name}): {estimated_tokens} tokens (límite: {max_tokens})")
        
        # Factor de seguridad especial para llama-3.3-70b-versatile
        safety_factor = 0.65 if model_name == "llama-3.3-70b-versatile" else 0.85
        
        if estimated_tokens > max_tokens * safety_factor:
            logger.warning(f"Prompt demasiado largo: ~{estimated_tokens} tokens. Truncando para {model_name}...")
            prompt = truncate_content(prompt, int(max_tokens * safety_factor))
            new_estimate = estimate_tokens(prompt)
            logger.info(f"Prompt truncado a ~{new_estimate} tokens")
            
        # Usar el modelo seleccionado
        client = Groq(api_key=api_key)
        
        # Para llama-3.3-70b-versatile, intentemos limitar explícitamente los tokens de salida
        if model_name == "llama-3.3-70b-versatile":
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=model_name,
                max_tokens=4000  # Limitar explícitamente la respuesta
            )
        else:
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=model_name,
            )
            
        return chat_completion.choices[0].message.content
        
    except Exception as e:
        error_msg = str(e).lower()
        logger.error(f"Error en Groq API con modelo {model_name}: {e}")
        
        # Si es un error de límite de tokens y podemos reintentar
        if ("token" in error_msg and ("exceed" in error_msg or "limit" in error_msg)) and retries > 0:
            logger.warning(f"Error de límite de tokens: {e}. Reintentando con un prompt más pequeño...")
            
            # Reducción más agresiva específicamente para llama-3.3-70b-versatile
            reduction_factor = 0.5 if model_name == "llama-3.3-70b-versatile" else 0.7
            max_tokens = TOKEN_LIMITS.get(model_name, 8000)
            shortened_prompt = truncate_content(prompt, int(max_tokens * reduction_factor))
            
            logger.info(f"Intentando nuevamente con prompt reducido al {int(reduction_factor*100)}% del límite")
            return ask_groq(shortened_prompt, api_key, model_name, retries-1)
        
        # Mensajes de error más específicos
        if "token" in error_msg and ("exceed" in error_msg or "limit" in error_msg):
            # Mensaje de error específico con recomendación de otro modelo
            if model_name == "llama-3.3-70b-versatile":
                return f"Error: El modelo {model_name} está rechazando el contenido por su longitud. Prueba estas alternativas: 1) Reduce aún más los datos seleccionados para el análisis, o 2) Usa el modelo 'llama-3.1-8b-instant' que aunque tiene menor capacidad, puede procesar tus datos con mayor facilidad."
            else:
                return f"Error: El contenido es demasiado largo para el modelo {model_name}. Prueba reduciendo los datos o seleccionando otro modelo."
        elif "api key" in error_msg:
            return f"Error: API key de Groq inválida o expirada. Por favor verifica tu API key."
        elif "rate limit" in error_msg:
            return f"Error: Has alcanzado el límite de solicitudes de Groq. Espera unos minutos antes de intentar nuevamente."
        else:
            return f"Error con la API de Groq (modelo {model_name}): {str(e)}"

def ask_gemini(prompt, api_key, model_name="gemini-2.0-flash", retries=1):
    """Ask a question to Gemini API using selected model"""
    if not api_key:
        return "Por favor, ingresa tu Gemini API Key en la configuración."
    
    # Validar API key primero
    is_valid, message = validate_api_key("gemini", api_key)
    if not is_valid:
        return f"Error de API: {message}"
    
    try:
        # Verificar límite de tokens y truncar si es necesario
        max_tokens = TOKEN_LIMITS.get(model_name, 32000)
        estimated_tokens = estimate_tokens(prompt)
        
        if estimated_tokens > max_tokens * 0.9:  # Usar 90% como límite seguro
            logger.warning(f"Prompt demasiado largo: ~{estimated_tokens} tokens. Truncando...")
            prompt = truncate_content(prompt, int(max_tokens * 0.9))
            logger.info(f"Prompt truncado a ~{estimate_tokens(prompt)} tokens")
        
        # Configuración básica de Gemini
        genai.configure(api_key=api_key)
        
        try:
            logger.info(f"Usando modelo Gemini: {model_name}")
            model = genai.GenerativeModel(model_name)
            
            # Usar configuración básica
            response = model.generate_content(prompt)
            
            if response and hasattr(response, 'text'):
                return response.text
            else:
                return "No se obtuvo respuesta del modelo. Intenta con otro modelo."
                
        except Exception as e:
            error_msg = str(e).lower()
            
            # Si es un error de límite de tokens y podemos reintentar
            if ("token" in error_msg or "content too long" in error_msg) and retries > 0:
                logger.warning(f"Error de Gemini - Contenido demasiado largo: {e}. Reintentando...")
                # Reducir el tamaño del prompt
                shortened_prompt = truncate_content(prompt, int(max_tokens * 0.7))
                return ask_gemini(shortened_prompt, api_key, model_name, retries-1)
            
            logger.error(f"Error con el modelo {model_name}: {e}")
            
            # Intentar con modelo de respaldo
            if retries > 0:
                try:
                    logger.info("Intentando con modelo de respaldo gemini-pro")
                    model = genai.GenerativeModel("gemini-pro")
                    response = model.generate_content(prompt)
                    
                    if response and hasattr(response, 'text'):
                        return "⚠️ Modelo solicitado no disponible. Respuesta generada con el modelo de respaldo gemini-pro:\n\n" + response.text
                    else:
                        return "No se pudo obtener respuesta de ningún modelo de Gemini."
                except Exception as backup_error:
                    return f"Error con todos los modelos de Gemini. Error: {str(e)}. Error de respaldo: {str(backup_error)}"
            else:
                if "token" in error_msg:
                    return f"Error: El contenido es demasiado largo para el modelo {model_name}. Por favor, reduce la cantidad de datos o usa un modelo con mayor capacidad como gemini-1.5-pro."
                else:
                    return f"Error con el modelo {model_name}: {str(e)}"
        
    except Exception as e:
        logger.error(f"Error general con Gemini API: {e}")
        return f"Error de conexión con Gemini: {str(e)}"

def analyze_scraped_data(data, api_key, model="groq", model_name="llama-3.3-70b-versatile"):
    """Analyze scraped data using AI with selected model"""
    if isinstance(data, pd.DataFrame) and data.empty:
        return "No hay datos para analizar."
    
    # Para modelo llama-3.3-70b-versatile, limitar aún más las filas
    row_limit = 10 if (model == "groq" and model_name == "llama-3.3-70b-versatile") else 15
    
    # Convertir los datos a un formato más legible
    data_str = ""
    try:
        # Limitar la cantidad de datos para evitar exceder límites de tokens
        sample_data = data.head(row_limit) if len(data) > row_limit else data
        data_str = sample_data.to_string()
        
        # Registrar el tamaño estimado para diagnóstico
        estimated_tokens = estimate_tokens(data_str)
        logger.info(f"Tamaño estimado de los datos a analizar: ~{estimated_tokens} tokens")
        
    except:
        data_str = str(data)
    
    # Instrucciones más claras y concisas para modelos grandes
    if model == "groq" and model_name == "llama-3.3-70b-versatile":
        prompt = f"Analiza brevemente estos datos extraídos de una página web:\n\n{data_str}"
    else:
        prompt = f"Analiza estos datos extraídos de una página web y proporciona un resumen útil e identifica patrones:\n\n{data_str}"
    
    # Verificar longitud del prompt y estimar tokens
    estimated_tokens = estimate_tokens(prompt)
    max_tokens = 0
    
    if model == "chatgpt":
        max_tokens = TOKEN_LIMITS.get(model_name, 4000)
    elif model == "groq":
        max_tokens = TOKEN_LIMITS.get(model_name, 8000)
    elif model == "gemini":
        max_tokens = TOKEN_LIMITS.get(model_name, 32000)
    
    # Factor de seguridad especial para llama-3.3-70b-versatile
    safety_factor = 0.65 if (model == "groq" and model_name == "llama-3.3-70b-versatile") else 0.85
    
    # Advertir si el prompt es muy largo
    if estimated_tokens > max_tokens * safety_factor:
        logger.warning(f"Datos para analizar demasiado grandes: ~{estimated_tokens} tokens. " +
                      f"Truncando para el modelo {model_name} (límite ~{max_tokens})...")
        
        prompt = truncate_content(prompt, int(max_tokens * safety_factor))
        new_estimate = estimate_tokens(prompt)
        logger.info(f"Prompt truncado a ~{new_estimate} tokens")
        
    # Realizar el análisis con el modelo seleccionado
    if model == "chatgpt":
        return ask_chatgpt(prompt, api_key, model_name)
    elif model == "groq":
        return ask_groq(prompt, api_key, model_name)
    elif model == "gemini":
        return ask_gemini(prompt, api_key, model_name)
    else:
        return "Modelo de IA no reconocido."
