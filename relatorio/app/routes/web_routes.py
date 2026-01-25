import csv
import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_from_directory
from io import TextIOWrapper
from ..database import (
    carregar_livros_do_banco, 
    get_conn, 
    importar_linha_csv,
    excluir_livro_do_banco,
    contar_total_livros
)

# Blueprint para a interface Web principal
web_bp = Blueprint('web', __name__, template_folder='../../templates')

# -----------------------------------------------------------------------------------------
# ROTAS WEB (Renderizam HTML)
# -----------------------------------------------------------------------------------------

@web_bp.route("/", methods=["GET"])
async def pagina_inicial():
    """
    Página inicial. Carrega os 10 primeiros registros (ou busca inicial).
    Utiliza as mesmas funções centralizadas que a API.
    """
    nome_busca = request.args.get("busca", "").strip()
    
    # Carrega a 'Página 1' inicial (índice 0)
    livros = carregar_livros_do_banco(limite=10, pagina=0, busca=nome_busca)
    # Total serve para o cálculo do contador de páginas inicial
    total_registros = contar_total_livros(nome_busca)
    
    return render_template("index.html", 
                         livros=livros, 
                         busca=nome_busca, 
                         total=total_registros)

# -----------------------------------------------------------------------------------------
# PROCESSAMENTO DE CSV
# -----------------------------------------------------------------------------------------

@web_bp.route("/upload_csv", methods=["POST"])
def upload_csv():
    file = request.files.get("arquivo")
    if not file or file.filename == "":
        flash("Selecione um arquivo CSV", "error")
        return redirect(url_for("web.pagina_inicial"))
    
    try:
        reader = csv.DictReader(TextIOWrapper(file, encoding="utf-8-sig"))
        conn = get_conn()
        cursor = conn.cursor()
        
        autores_vistos = set()
        livros_vistos = set()
        linhas_processadas = 0
        
        for row in reader:
            try:
                # Função refatorada para usar Store Procedure
                importar_linha_csv(cursor, row, autores_vistos, livros_vistos)
                linhas_processadas += 1
            except:
                continue
        
        conn.commit()
        cursor.close()
        conn.close()
        flash(f"{linhas_processadas} registros processados!", "success")
    except Exception as err:
        flash(f"Erro no processamento: {err}", "error")
    
    return redirect(url_for("web.pagina_inicial"))

@web_bp.route("/livros/<int:id>/excluir", methods=["POST"])
def excluir_livro_web(id):
    if excluir_livro_do_banco(id):
        flash("Excluído!", "success")
    else:
        flash("Não encontrado", "error")
    return redirect(url_for("web.pagina_inicial"))

@web_bp.route("/static/<path:filename>")
def static_files(filename):
    templates_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "templates"))
    return send_from_directory(templates_dir, filename)
