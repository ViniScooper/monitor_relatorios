import csv
import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_from_directory
from io import TextIOWrapper
from ..database import (
    carregar_livros_do_banco, 
    get_conn, 
    importar_linha_csv,
    excluir_livro_do_banco
)
import mysql.connector

# Blueprint para a interface Web. 
web_bp = Blueprint('web', __name__, template_folder='../../templates')










# -----------------------------------------------------------------------------------------
# ROTAS WEB (Renderizam HTML e gerenciam interface)
# -----------------------------------------------------------------------------------------

@web_bp.route("/", methods=["GET"])
def pagina_inicial():
    """Página principal que exibe a lista de livros e a barra de busca."""
    nome_busca = request.args.get("busca", "").strip()
    
    if nome_busca:
        try:
            conn = get_conn()
            cur = conn.cursor(dictionary=True)
            cur.execute("""
             
                            
                SELECT * FROM view_relatorio_livros 
                    WHERE TITULO LIKE %s 
                    ORDER BY total_vendas DESC







            """
                        

                        
                        , (f"%{nome_busca}%",))
            livros = cur.fetchall()
            cur.close()
            conn.close()
        except mysql.connector.Error as err:
            print(f"Erro ao buscar livros: {err}")
            livros = []
    else:
        livros = carregar_livros_do_banco()
    
    return render_template("index.html", livros=livros, busca=nome_busca)










# -----------------------------------------------------------------------------------------
# ROTA PARA UPLOAD DE ARQUIVO CSV
# -----------------------------------------------------------------------------------------

@web_bp.route("/upload_csv", methods=["POST"])
def upload_csv():
    """Recebe um arquivo CSV do formulário e processa cada linha salvando no banco."""
    file = request.files.get("arquivo")
    if not file or file.filename == "":
        flash("Nenhum arquivo selecionado", "error")
        return redirect(url_for("web.pagina_inicial"))
    
    try:
        # Wrapper para tratar o arquivo enviado como texto (CSV)
        # utf-8-sig lida com arquivos salvos com BOM (comum no Windows/Excel)
        reader = csv.DictReader(TextIOWrapper(file, encoding="utf-8-sig"))
        
        conn = get_conn()
        cursor = conn.cursor()
        
        autores_vistos = set()
        livros_vistos = set()
        linhas_processadas = 0
        
        for row in reader:
            try:
                importar_linha_csv(cursor, row, autores_vistos, livros_vistos)
                linhas_processadas += 1
            except Exception as e:
                print(f"Erro ao processar linha: {e}")
                continue
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash(f"{linhas_processadas} registros processados com sucesso!", "success")
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



# -----------------------------------------------------------------------------------------
# ROTA PARA SERVE ARQUIVOS ESTÁTICOS
# -----------------------------------------------------------------------------------------
 
@web_bp.route("/static/<path:filename>")
def static_files(filename):
    """Serve arquivos estáticos manualmente."""
    templates_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "templates"))
    return send_from_directory(templates_dir, filename)
