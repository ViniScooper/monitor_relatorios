# Importa os Blueprints definidos nos arquivos de rotas
from .api_routes import api_bp
from .web_routes import web_bp

# Exporta para facilitar o acesso pelo app
__all__ = ['api_bp', 'web_bp']
