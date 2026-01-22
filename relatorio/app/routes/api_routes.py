from flask import jsonify, request, Blueprint
from ..database import (
    carregar_livros_do_banco, 
    get_conn, 
    excluir_livro_do_banco
)
import mysql.connector

# Criação do Blueprint da API.
api_bp = Blueprint('api', __name__)

# -----------------------------------------------------------------------------------------
# ROTAS DA API REST (Retornam JSON)
# -----------------------------------------------------------------------------------------

@api_bp.route('/livros', methods=['GET'])
def obter_livros():
    """Retorna todos os livros em formato JSON."""
    livros = carregar_livros_do_banco()
    return jsonify(livros)

@api_bp.route('/livros/<int:id>', methods=['GET'])
def obter_livro_por_id(id):
    """Busca um único livro pelo ID."""
    try:
        conn = get_conn()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT 
                l.CODG_LIVRO_PK as id,
                l.TITULO,
                l.GENERO, 
                l.SINOSPE as sinopse,
                a.NOME as nome_autor,
                a.CIDADE as cidade_autor,
                COALESCE(SUM(v.QUANTIDADE), 0) as total_vendas
            FROM livro l
            LEFT JOIN autor a ON l.CODG_AUTOR_FK = a.CODG_AUTOR_PK
            LEFT JOIN vendas v ON l.CODG_LIVRO_PK = v.CODG_LIVRO_FK
            WHERE l.CODG_LIVRO_PK = %s
            GROUP BY l.CODG_LIVRO_PK, l.TITULO, l.GENERO, l.SINOSPE, a.NOME, a.CIDADE
        """, (id,))
        livro = cur.fetchone()
        cur.close()
        conn.close()
        
        if livro:
            return jsonify(livro)
        return jsonify({"erro": "Livro não encontrado"}), 404
    except mysql.connector.Error as err:
        return jsonify({"erro": f"Erro ao buscar livro: {err}"}), 500

@api_bp.route('/livros/<int:id>', methods=['DELETE'])
def excluir_livro_api(id):
    """Exclui um livro via API."""
    try:
        if excluir_livro_do_banco(id):
            return jsonify({"mensagem": "Livro excluído com sucesso"}), 200
        return jsonify({"erro": "Livro não encontrado"}), 404
    except Exception as err:
        return jsonify({"erro": f"Erro ao excluir livro: {err}"}), 500
