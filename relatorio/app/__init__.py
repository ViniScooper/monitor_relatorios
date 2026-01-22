import os
from flask import Flask
from .routes import api_bp, web_bp

def create_app():
    """Fábrica de aplicativos Flask."""
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    app = Flask(__name__, template_folder=template_dir)
    
    # Configurações
    app.secret_key = os.urandom(24)
    
    # Registro de Blueprints
    # O prefixo '' para web_bp significa que as rotas começam na raiz /
    # O prefixo poderia ser '/api' para api_bp se quiséssemos separar totalmente
    app.register_blueprint(web_bp, url_prefix='/')
    app.register_blueprint(api_bp, url_prefix='/api') # Adicionado prefixo /api para melhor organização

    return app
