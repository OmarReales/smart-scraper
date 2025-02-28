import validators
from urllib.parse import urlparse, unquote

def is_valid_url(url):
    """
    Validate if the input is a proper URL.
    Más permisivo con fragmentos (#) que contienen caracteres especiales.
    """
    try:
        # Primera verificación usando la biblioteca validators
        if validators.url(url):
            return True
        
        # Si falla, intentamos una validación más flexible
        parts = urlparse(url)
        
        # Verificamos si al menos tiene esquema (http/https) y netloc (dominio)
        if parts.scheme in ('http', 'https') and parts.netloc:
            return True
            
        return False
    except:
        return False
