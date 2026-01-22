from flask import jsonify, request, Blueprint
from ..database import (
    carregar_livros_do_banco, 
    get_conn, 
    salvar_livro_no_banco, 
    excluir_livro_do_banco
)
import mysql.connector

# Criação do Blueprint da API. Todas as rotas aqui serão prefixadas com /api/ no app principal.
api_bp = Blueprint('api', __name__)

# -----------------------------------------------------------------------------------------
# ROTAS DA API REST (Retornam JSON)
# -----------------------------------------------------------------------------------------

@api_bp.route('/livros', methods=['GET'])
def obter_livros():
    """Retorna todos os livros em formato JSON para integrações externas."""
    livros = carregar_livros_do_banco()
    return jsonify(livros)

@api_bp.route('/livros/<int:id>', methods=['GET'])
def obter_livro_por_id(id):
    """Busca um único livro pelo ID e retorna JSON."""
    try:
        conn = get_conn()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT codg_livro_pk as id, titulo, autor FROM livros WHERE codg_livro_pk = %s", (id,))
        livro = cur.fetchone()
        cur.close()
        conn.close()
        
        if livro:
            return jsonify(livro)
        return jsonify({"erro": "Livro não encontrado"}), 404
    except mysql.connector.Error as err:
        return jsonify({"erro": f"Erro ao buscar livro: {err}"}), 500

@api_bp.route('/livros/<int:id>', methods=['PUT'])
def editar_livro_por_id(id):
    """Atualiza dados de um livro via requisição HTTP PUT."""
    livro_alterado = request.get_json()  # Captura o corpo JSON enviado
    livro_alterado["id"] = id
    
    try:
        salvar_livro_no_banco(livro_alterado)
        
        # Busca o livro novamente para confirmar como ficou no banco
        conn = get_conn()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT codg_livro_pk as id, titulo, autor FROM livros WHERE codg_livro_pk = %s", (id,))
        livro_atualizado = cur.fetchone()
        cur.close()
        conn.close()
        
        if livro_atualizado:
            return jsonify(livro_atualizado)
        return jsonify({"erro": "Livro não encontrado"}), 404
    except Exception as err:
        return jsonify({"erro": f"Erro ao atualizar livro: {err}"}), 500

@api_bp.route('/livros', methods=['POST'])
def incluir_novo_livro():
    """Cria um novo livro via API. Se o ID não for enviado, gera o próximo automaticamente."""
    novo_livro = request.get_json()
    
    if "id" not in novo_livro:
        try:
            conn = get_conn()
            cur = conn.cursor()
            # Lógica para pegar o maior ID atual e somar +1
            cur.execute("SELECT MAX(codg_livro_pk) as max_id FROM livros")
            result = cur.fetchone()
            novo_id = (result[0] + 1) if result[0] else 1
            novo_livro["id"] = novo_id
            cur.close()
            conn.close()
        except Exception as err:
            return jsonify({"erro": f"Erro ao gerar ID: {err}"}), 500
    
    try:
        salvar_livro_no_banco(novo_livro)
        return jsonify(novo_livro), 201  # Código 201 significa "Criado com sucesso"
    except Exception as err:
        return jsonify({"erro": f"Erro ao salvar livro: {err}"}), 500
