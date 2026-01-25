from flask import jsonify, request, Blueprint
from ..database import (
    carregar_livros_do_banco, 
    excluir_livro_do_banco,
    contar_total_livros
)

# Blueprint configurado com prefixo /api em app/__init__.py
api_bp = Blueprint('api', __name__)

# -----------------------------------------------------------------------------------------
# ROTAS DA API REST (Retornam JSON para o AJAX/Frontend)
# -----------------------------------------------------------------------------------------

@api_bp.route('/livros', methods=['GET'])
def obter_livros():
    """
    Retorna JSON com 'livros' (lista paginada) e 'total' (total de registros).
    O JavaScript no Frontend utiliza essa rota para navegar entre as páginas.
    """
    try:
        pagina = request.args.get('pagina', default=0, type=int)
        limite = request.args.get('limite', default=10, type=int)
        busca = request.args.get('busca', default='').strip()
        
        # Busca os dados no banco usando as funções centralizadas
        livros = carregar_livros_do_banco(limite=limite, pagina=pagina, busca=busca)
        total = contar_total_livros(busca)
        
        # Retorna a estrutura esperada pelo parser no index.html
        return jsonify({
            "livros": livros,
            "total": total,
            "pagina": pagina,
            "limite": limite
        })
    except Exception as err:
        return jsonify({"erro": f"Falha na API: {err}"}), 500

@api_bp.route('/livros/<int:id>', methods=['DELETE'])
def excluir_livro_api(id):
    """Exclui um livro via chamada de API."""
    try:
        if excluir_livro_do_banco(id):
            return jsonify({"mensagem": "Sucesso"}), 200
        return jsonify({"erro": "Não encontrado"}), 404
    except Exception as err:
        return jsonify({"erro": f"Erro: {err}"}), 500
