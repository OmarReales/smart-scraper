import logging
import pandas as pd
import openai
from groq import Groq
import google.generativeai as genai

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
    "llama-guard-3-8b": "Llama Guard 3 8B",
    "distil-whisper-large-v3-en": "Whisper Large V3 (Inglés)",
    "whisper-large-v3": "Whisper Large V3",
    "whisper-large-v3-turbo": "Whisper Large V3 Turbo"
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

def ask_chatgpt(prompt, api_key, model_name="gpt-3.5-turbo"):
    """Ask a question to ChatGPT API with selected model"""
    try:
        if not api_key:
            return "Por favor, ingresa tu ChatGPT API Key en la configuración."
        
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "Eres un experto en web scraping."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error en ChatGPT API con modelo {model_name}: {e}")
        return f"Error con la API de ChatGPT (modelo {model_name}): {str(e)}"

def ask_groq(prompt, api_key, model_name="llama-3.3-70b-versatile"):
    """Ask a question to Groq API with selected model"""
    try:
        if not api_key:
            return "Por favor, ingresa tu Groq API Key en la configuración."
        
        client = Groq(api_key=api_key)
        # Comprobar si el modelo es de tipo Whisper (para transcripción de audio)
        if "whisper" in model_name.lower():
            logger.info(f"Modelo de transcripción seleccionado: {model_name}")
            return f"Modelo {model_name} es para transcripción de audio, no para chat. Por favor selecciona un modelo LLM para preguntas de texto."
            
        # Usar el modelo seleccionado
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=model_name,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        logger.error(f"Error en Groq API con modelo {model_name}: {e}")
        return f"Error con la API de Groq (modelo {model_name}): {str(e)}"

def ask_gemini(prompt, api_key, model_name="gemini-2.0-flash"):
    """Ask a question to Gemini API using selected model"""
    try:
        if not api_key:
            return "Por favor, ingresa tu Gemini API Key en la configuración."
        
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
            logger.error(f"Error con el modelo {model_name}: {e}")
            
            # Intentar con modelo de respaldo
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
        
    except Exception as e:
        logger.error(f"Error general con Gemini API: {e}")
        return f"Error de conexión con Gemini: {str(e)}"

def analyze_scraped_data(data, api_key, model="groq", model_name="llama-3.3-70b-versatile"):
    """Analyze scraped data using AI with selected model"""
    if isinstance(data, pd.DataFrame) and data.empty:
        return "No hay datos para analizar."
    
    # Convertir los datos a un formato más legible
    data_str = ""
    try:
        # Limitar la cantidad de datos para evitar exceder límites de tokens
        sample_data = data.head(20) if len(data) > 20 else data
        data_str = sample_data.to_string()
    except:
        data_str = str(data)
    
    prompt = f"Analiza estos datos extraídos de una página web y proporciona un resumen útil e identifica patrones:\n\n{data_str}"
    
    # Asegurarse de que la solicitud no sea demasiado larga
    if len(prompt) > 8000:
        prompt = prompt[:8000] + "...[truncado]"
    
    if model == "chatgpt":
        return ask_chatgpt(prompt, api_key, model_name)
    elif model == "groq":
        return ask_groq(prompt, api_key, model_name)
    elif model == "gemini":
        return ask_gemini(prompt, api_key, model_name)
    else:
        return "Modelo de IA no reconocido."
