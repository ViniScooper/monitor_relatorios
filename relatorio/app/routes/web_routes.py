import csv
import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_from_directory
from io import TextIOWrapper
from ..database import (
    carregar_livros_do_banco, 
    get_conn, 
    salvar_livro_no_banco, 
    excluir_livro_do_banco
)
import mysql.connector

# Blueprint para a interface Web. 
# Usamos template_folder para dizer onde estão os arquivos HTML deste módulo.
web_bp = Blueprint('web', __name__, template_folder='../../templates')

# -----------------------------------------------------------------------------------------
# ROTAS WEB (Renderizam HTML e gerenciam interface)
# -----------------------------------------------------------------------------------------

@web_bp.route("/", methods=["GET"])
def pagina_inicial():
    """Página principal que exibe a lista de livros e a barra de busca."""
    # .args.get pega parâmetros da URL (ex: ?busca=HP)
    nome_busca = request.args.get("busca", "").strip()
    
    if nome_busca:
        try:
            conn = get_conn()
            cur = conn.cursor(dictionary=True)
            # Busca parcial usando LIKE do SQL (%termo%)
            cur.execute(
                "SELECT codg_livro_pk as id, titulo, autor FROM livros WHERE titulo LIKE %s ORDER BY codg_livro_pk",
                (f"%{nome_busca}%",)
            )
            livros = cur.fetchall()
            cur.close()
            conn.close()
        except mysql.connector.Error as err:
            print(f"Erro ao buscar livros: {err}")
            livros = []
    else:
        # Se não houver busca, carrega tudo do banco
        livros = carregar_livros_do_banco()
    
    # render_template envia os dados para o arquivo HTML substituir as variáveis
    return render_template("index.html", livros=livros, busca=nome_busca)

@web_bp.route("/upload_csv", methods=["POST"])
def upload_csv():
    """Recebe um arquivo CSV do formulário e processa cada linha salvando no banco."""
    file = request.files.get("arquivo")
    if not file or file.filename == "":
        flash("Nenhum arquivo selecionado", "error") # Mensagem temporária na tela
        return redirect(url_for("web.pagina_inicial"))
    
    try:
        # Wrapper para tratar o arquivo enviado como texto (CSV)
        reader = csv.DictReader(TextIOWrapper(file, encoding="utf-8"))
        livros_importados = 0
        
        for row in reader:
            livro = {
                "id": int(row.get("id", 0)) if row.get("id") else None,
                "titulo": row.get("titulo", ""),
                "autor": row.get("autor", "")
            }
            
            # Se a linha no CSV não tiver ID, geramos no código
            if not livro["id"]:
                try:
                    conn = get_conn()
                    cur = conn.cursor()
                    cur.execute("SELECT MAX(codg_livro_pk) as max_id FROM livros")
                    result = cur.fetchone()
                    livro["id"] = (result[0] + 1) if result[0] else 1
                    cur.close()
                    conn.close()
                except Exception as err:
                    flash(f"Erro ao gerar ID: {err}", "error")
                    return redirect(url_for("web.pagina_inicial"))
            
            try:
                # Salva no banco (faz o update se o ID já existir)
                salvar_livro_no_banco(livro)
                livros_importados += 1
            except Exception as err:
                print(f"Erro ao salvar livro {livro['id']}: {err}")
                continue
        
        # Após o loop, avisa quantas linhas deram certo
        flash(f"{livros_importados} livro(s) importado(s) com sucesso!", "success")
    except Exception as err:
        flash(f"Erro ao processar arquivo CSV: {err}", "error")
    
    return redirect(url_for("web.pagina_inicial"))

@web_bp.route("/livros/<int:id>/excluir", methods=["POST"])
def excluir_livro_web(id):
    """Rota acionada pelo botão 'Excluir' na tabela HTML."""
    try:
        if excluir_livro_do_banco(id):
            flash("Livro excluído com sucesso!", "success")
        else:
            flash("Livro não encontrado", "error")
    except Exception as err:
        flash(f"Erro ao excluir livro: {err}", "error")
    
    return redirect(url_for("web.pagina_inicial"))

@web_bp.route("/static/<path:filename>")
def static_files(filename):
    """
    Serve arquivos estáticos (CSS, JS) manualmente, pois mudamos a pasta 
    padrão do Flask para uma estrutura personalizada.
    """
    templates_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "templates"))
    return send_from_directory(templates_dir, filename)
