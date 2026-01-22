# ============================================================================================================
# SISTEMA DE MONITORAMENTO DE RELATÓRIOS - GERENCIAMENTO DE LIVROS
# ============================================================================================================
# Este arquivo contém a aplicação Flask principal que gerencia livros em um banco de dados MySQL.
# Funcionalidades:
# - API REST para gerenciar livros (CRUD completo)
# - Interface web para visualizar e gerenciar livros
# - Importação de livros via CSV
# - Busca de livros por nome/título
# ============================================================================================================

# ------------------------------------------------------------------------------------------------------------
# IMPORTAÇÃO DE BIBLIOTECAS NECESSÁRIAS
# ------------------------------------------------------------------------------------------------------------
from flask import Flask, jsonify, request, render_template, redirect, url_for, flash, send_from_directory
# Flask: Framework web principal
# jsonify: Converte dados Python para formato JSON (usado nas APIs)
# request: Acessa dados das requisições HTTP (formulários, parâmetros, etc)
# render_template: Renderiza templates HTML com dados do Python
# redirect: Redireciona para outra página
# url_for: Gera URLs para rotas nomeadas
# flash: Envia mensagens temporárias (sucesso/erro) para o usuário
# send_from_directory: Serve arquivos estáticos (CSS, JS, imagens)

import csv  # Para trabalhar com arquivos CSV (leitura e escrita)
import os  # Para acessar variáveis de ambiente e caminhos de arquivos
from io import TextIOWrapper  # Para converter streams de arquivos binários em texto
import mysql.connector  # Biblioteca para conectar e trabalhar com banco de dados MySQL
from dotenv import load_dotenv  # Carrega variáveis de ambiente de um arquivo .env

# ------------------------------------------------------------------------------------------------------------
# INICIALIZAÇÃO DA APLICAÇÃO FLASK
# ------------------------------------------------------------------------------------------------------------
app = Flask(__name__)  # Cria a instância principal do Flask
# __name__ é usado para que o Flask saiba onde encontrar templates e arquivos estáticos

app.secret_key = os.urandom(24)  # Gera uma chave secreta aleatória para flash messages
# A chave secreta é necessária para que o Flask possa criptografar as mensagens flash
# e garantir que não sejam alteradas pelo usuário

# ------------------------------------------------------------------------------------------------------------
# CONFIGURAÇÃO DO BANCO DE DADOS
# ------------------------------------------------------------------------------------------------------------
# Carrega as variáveis de ambiente do arquivo "env" que está na raiz do projeto
# O arquivo env contém informações sensíveis como senha do banco (não deve ser commitado no git)
env_path = os.path.join(os.path.dirname(__file__), "..", "env")
# os.path.dirname(__file__) = pasta onde está este arquivo (relatorio/)
# ".." = sobe um nível (raiz do projeto)
# "env" = nome do arquivo com as variáveis de ambiente
load_dotenv(env_path)  # Carrega as variáveis do arquivo env

def get_conn():
    """
    Função para estabelecer conexão com o banco de dados MySQL.
    
    Esta função:
    - Lê as configurações do banco de dados do arquivo env
    - Cria uma conexão com o MySQL
    - Retorna a conexão para ser usada em outras funções
    
    Retorna:
        mysql.connector.connection: Objeto de conexão com o banco de dados
    
    Levanta:
        mysql.connector.Error: Se houver erro ao conectar
    """
    try:
        # Cria a conexão usando as variáveis de ambiente
        return mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),  # Endereço do servidor MySQL (padrão: localhost)
            port=int(os.getenv("DB_PORT", "3306")),  # Porta do MySQL (padrão: 3306)
            user=os.getenv("DB_USER", "root"),  # Usuário do banco (padrão: root)
            password=os.getenv("DB_PASSWORD", ""),  # Senha do banco (padrão: vazio)
            database=os.getenv("DB_NAME", "monitor_relatorio"),  # Nome do banco de dados
            use_unicode=True,  # Permite usar caracteres especiais (acentos, etc)
            charset='utf8mb4',  # Codificação de caracteres (suporta emojis e caracteres especiais)
            autocommit=False  # Não faz commit automático (precisamos fazer manualmente)
        )
    except mysql.connector.Error as err:
        # Se houver erro, imprime e relança a exceção
        print(f"Erro ao conectar ao MySQL: {err}")
        raise

# ------------------------------------------------------------------------------------------------------------
# FUNÇÕES AUXILIARES PARA MANIPULAÇÃO DE LIVROS NO BANCO DE DADOS
# ------------------------------------------------------------------------------------------------------------

def carregar_livros_do_banco():
    """
    Carrega todos os livros do banco de dados MySQL.
    
    Esta função:
    - Conecta ao banco de dados
    - Executa uma query SELECT para buscar todos os livros
    - Retorna uma lista de dicionários, onde cada dicionário representa um livro
    
    Retorna:
        list: Lista de dicionários com os livros. Cada dicionário tem:
            - id: ID do livro (codg_livro_pk)
            - titulo: Título do livro
            - autor: Nome do autor
        Retorna lista vazia [] se houver erro
    
    Exemplo de retorno:
        [
            {"id": 1, "titulo": "Dom Casmurro", "autor": "Machado de Assis"},
            {"id": 2, "titulo": "1984", "autor": "George Orwell"}
        ]
    """
    try:
        conn = get_conn()  # Obtém conexão com o banco
        # dictionary=True faz com que os resultados sejam retornados como dicionários
        # ao invés de tuplas, facilitando o acesso aos dados
        cur = conn.cursor(dictionary=True)
        
        # Executa a query SQL para buscar todos os livros
        # codg_livro_pk é o nome da coluna no banco, mas usamos "as id" para renomear
        # ORDER BY ordena os resultados pelo ID (do menor para o maior)
        cur.execute("SELECT codg_livro_pk as id, titulo, autor FROM livros ORDER BY codg_livro_pk")
        livros = cur.fetchall()  # Busca todos os resultados da query
        
        # Fecha o cursor e a conexão (importante para liberar recursos)
        cur.close()
        conn.close()
        return livros
    except mysql.connector.Error as err:
        # Se houver erro, imprime e retorna lista vazia
        print(f"Erro ao carregar livros do banco: {err}")
        return []  # Retorna lista vazia em caso de erro

def salvar_livro_no_banco(livro: dict):
    """
    Salva um livro no banco de dados MySQL.
    
    Esta função faz um UPSERT (INSERT ou UPDATE):
    - Se o ID do livro não existir no banco, insere um novo registro
    - Se o ID já existir, atualiza os dados do livro existente
    
    Parâmetros:
        livro (dict): Dicionário com os dados do livro. Deve conter:
            - id: ID do livro (obrigatório)
            - titulo: Título do livro (opcional, padrão: "")
            - autor: Nome do autor (opcional, padrão: "")
    
    Levanta:
        mysql.connector.Error: Se houver erro ao salvar no banco
    
    Exemplo de uso:
        livro = {"id": 1, "titulo": "Dom Casmurro", "autor": "Machado de Assis"}
        salvar_livro_no_banco(livro)
    """
    try:
        conn = get_conn()  # Obtém conexão com o banco
        cur = conn.cursor()  # Cria cursor para executar comandos SQL
        
        # Comando SQL que faz INSERT ou UPDATE
        # INSERT INTO: tenta inserir um novo registro
        # ON DUPLICATE KEY UPDATE: se o ID já existir (chave primária duplicada),
        # atualiza os campos titulo e autor com os novos valores
        # VALUES(...) retorna os valores que foram inseridos/atualizados
        cur.execute(
            "INSERT INTO livros (codg_livro_pk, titulo, autor) VALUES (%s, %s, %s) "
            "ON DUPLICATE KEY UPDATE titulo=VALUES(titulo), autor=VALUES(autor)",
            (livro["id"], livro.get("titulo", ""), livro.get("autor", "")),
        )
        # %s são placeholders que serão substituídos pelos valores da tupla
        # livro.get("titulo", "") retorna o título se existir, senão retorna ""
        
        conn.commit()  # Confirma as alterações no banco (importante!)
        # Sem commit, as alterações não são salvas permanentemente
        
        cur.close()    # Fecha o cursor
        conn.close()   # Fecha a conexão
        print(f"Livro {livro['id']} salvo no banco com sucesso!")
    except mysql.connector.Error as err:
        print(f"Erro ao salvar livro no banco: {err}")
        raise  # Relança a exceção para que quem chamou a função saiba que houve erro

def excluir_livro_do_banco(id: int):
    """
    Exclui um livro do banco de dados MySQL pelo ID.
    
    Parâmetros:
        id (int): ID do livro a ser excluído
    
    Retorna:
        bool: True se o livro foi excluído com sucesso, False se não foi encontrado
    
    Levanta:
        mysql.connector.Error: Se houver erro ao excluir
    
    Exemplo de uso:
        excluir_livro_do_banco(1)  # Exclui o livro com ID 1
    """
    try:
        conn = get_conn()
        cur = conn.cursor()
        
        # Executa o comando DELETE para remover o livro com o ID especificado
        cur.execute("DELETE FROM livros WHERE codg_livro_pk = %s", (id,))
        # A vírgula após id é importante: (id,) cria uma tupla com um elemento
        # Sem a vírgula, seria apenas (id) que não é uma tupla válida
        
        conn.commit()  # Confirma a exclusão
        rows_affected = cur.rowcount  # Conta quantas linhas foram afetadas
        # Se rows_affected > 0, significa que um livro foi excluído
        # Se rows_affected == 0, significa que nenhum livro tinha esse ID
        
        cur.close()
        conn.close()
        
        if rows_affected > 0:
            print(f"Livro {id} excluído do banco com sucesso!")
            return True
        else:
            print(f"Livro {id} não encontrado no banco")
            return False
    except mysql.connector.Error as err:
        print(f"Erro ao excluir livro do banco: {err}")
        raise

# ============================================================================================================
# DEFINIÇÃO DAS ROTAS DA API REST
# ============================================================================================================
# As rotas abaixo implementam uma API REST completa para gerenciar livros.
# REST = Representational State Transfer (padrão de arquitetura para APIs web)
# ============================================================================================================

# ------------------------------------------------------------------------------------------------------------
# ROTA 1: OBTER TODOS OS LIVROS (GET /livros)
# ------------------------------------------------------------------------------------------------------------
@app.route('/livros', methods=['GET'])
def obter_livros():
    """
    Retorna todos os livros em formato JSON.
    
    Esta é uma rota de API REST que retorna dados em formato JSON.
    Útil para integração com outras aplicações ou frontend JavaScript.
    
    Método HTTP: GET
    URL: /livros
    Resposta: JSON com lista de livros
    
    Exemplo de resposta:
        [
            {"id": 1, "titulo": "Dom Casmurro", "autor": "Machado de Assis"},
            {"id": 2, "titulo": "1984", "autor": "George Orwell"}
        ]
    """
    livros = carregar_livros_do_banco()  # Carrega todos os livros do banco
    return jsonify(livros)  # Converte a lista Python para JSON e retorna

# ------------------------------------------------------------------------------------------------------------
# ROTA 2: OBTER UM LIVRO ESPECÍFICO POR ID (GET /livros/<id>)
# ------------------------------------------------------------------------------------------------------------
@app.route('/livros/<int:id>', methods=['GET'])
def obter_livro_por_id(id):
    """
    Busca um livro específico pelo seu ID.
    
    Método HTTP: GET
    URL: /livros/<id>
    Parâmetros de URL:
        id (int): ID do livro a ser buscado
    
    Resposta:
        - 200 OK: JSON com os dados do livro
        - 404 Not Found: JSON com mensagem de erro se não encontrar
        - 500 Internal Server Error: JSON com mensagem de erro se houver problema no servidor
    
    Exemplo de uso:
        GET /livros/1
        Resposta: {"id": 1, "titulo": "Dom Casmurro", "autor": "Machado de Assis"}
    """
    try:
        conn = get_conn()
        cur = conn.cursor(dictionary=True)  # Retorna dicionários ao invés de tuplas
        
        # Busca o livro com o ID especificado
        cur.execute("SELECT codg_livro_pk as id, titulo, autor FROM livros WHERE codg_livro_pk = %s", (id,))
        livro = cur.fetchone()  # Busca apenas um resultado (o primeiro)
        
        cur.close()
        conn.close()
        
        if livro:
            # Se encontrou o livro, retorna em JSON
            return jsonify(livro)
        else:
            # Se não encontrou, retorna erro 404 (Not Found)
            return jsonify({"erro": "Livro não encontrado"}), 404
    except mysql.connector.Error as err:
        # Se houver erro no banco, retorna erro 500 (Internal Server Error)
        return jsonify({"erro": f"Erro ao buscar livro: {err}"}), 500

# ------------------------------------------------------------------------------------------------------------
# ROTA 3: EDITAR UM LIVRO EXISTENTE (PUT /livros/<id>)
# ------------------------------------------------------------------------------------------------------------
@app.route('/livros/<int:id>', methods=['PUT'])
def editar_livro_por_id(id):
    """
    Atualiza os dados de um livro existente.
    
    Método HTTP: PUT (usado para atualizar recursos existentes)
    URL: /livros/<id>
    Body: JSON com os novos dados do livro
    Parâmetros de URL:
        id (int): ID do livro a ser atualizado
    
    Exemplo de requisição:
        PUT /livros/1
        Body: {"titulo": "Dom Casmurro - Edição Especial", "autor": "Machado de Assis"}
    
    Resposta:
        - 200 OK: JSON com os dados atualizados do livro
        - 404 Not Found: Se o livro não existir
        - 500 Internal Server Error: Se houver erro ao atualizar
    """
    livro_alterado = request.get_json()  # Obtém os dados JSON do corpo da requisição
    # request.get_json() converte o JSON enviado pelo cliente em um dicionário Python
    
    # Garante que o ID no dicionário seja o mesmo da URL
    livro_alterado["id"] = id
    
    # Salva no banco (a função salvar_livro_no_banco faz UPSERT, então atualiza se existir)
    try:
        salvar_livro_no_banco(livro_alterado)
        
        # Busca o livro atualizado para retornar os dados finais
        conn = get_conn()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT codg_livro_pk as id, titulo, autor FROM livros WHERE codg_livro_pk = %s", (id,))
        livro_atualizado = cur.fetchone()
        cur.close()
        conn.close()
        
        if livro_atualizado:
            return jsonify(livro_atualizado)  # Retorna os dados atualizados
        else:
            return jsonify({"erro": "Livro não encontrado"}), 404
    except Exception as err:
        return jsonify({"erro": f"Erro ao atualizar livro: {err}"}), 500

# ------------------------------------------------------------------------------------------------------------
# ROTA 4: ADICIONAR UM NOVO LIVRO (POST /livros)
# ------------------------------------------------------------------------------------------------------------
@app.route('/livros', methods=['POST'])
def incluir_novo_livro():
    """
    Adiciona um novo livro à lista.
    
    Método HTTP: POST (usado para criar novos recursos)
    URL: /livros
    Body: JSON com dados do livro
    
    Exemplo de requisição:
        POST /livros
        Body: {"titulo": "1984", "autor": "George Orwell"}
        (O ID será gerado automaticamente se não for fornecido)
    
    Resposta:
        - 201 Created: JSON com os dados do livro criado (incluindo o ID gerado)
        - 500 Internal Server Error: Se houver erro ao criar
    """
    novo_livro = request.get_json()  # Obtém dados do novo livro do corpo da requisição
    
    # Se o livro não tiver ID, busca o próximo ID disponível no banco
    if "id" not in novo_livro:
        try:
            conn = get_conn()
            cur = conn.cursor()
            # Busca o maior ID existente no banco
            cur.execute("SELECT MAX(codg_livro_pk) as max_id FROM livros")
            result = cur.fetchone()  # Retorna uma tupla, ex: (5,)
            # Se result[0] for None (banco vazio), usa 1, senão soma 1 ao maior ID
            novo_id = (result[0] + 1) if result[0] else 1
            novo_livro["id"] = novo_id
            cur.close()
            conn.close()
        except Exception as err:
            return jsonify({"erro": f"Erro ao gerar ID: {err}"}), 500
    
    # Salva o novo livro no banco
    try:
        salvar_livro_no_banco(novo_livro)
        return jsonify(novo_livro), 201  # Retorna o livro criado com status 201 (Created)
    except Exception as err:
        return jsonify({"erro": f"Erro ao salvar livro: {err}"}), 500

# ------------------------------------------------------------------------------------------------------------
# ROTA 5: REMOVER UM LIVRO (DELETE /livros/<id>)
# ------------------------------------------------------------------------------------------------------------
@app.route('/livros/<int:id>', methods=['DELETE'])
def excluir_livro(id):
    """
    Remove um livro do banco de dados.
    
    Método HTTP: DELETE (usado para remover recursos)
    URL: /livros/<id>
    Parâmetros de URL:
        id (int): ID do livro a ser excluído
    
    Exemplo de uso:
        DELETE /livros/1
    
    Resposta:
        - 200 OK: JSON com mensagem de sucesso
        - 404 Not Found: Se o livro não existir
        - 500 Internal Server Error: Se houver erro ao excluir
    """
    try:
        if excluir_livro_do_banco(id):
            return jsonify({"mensagem": "Livro removido com sucesso"})
        else:
            return jsonify({"erro": "Livro não encontrado"}), 404
    except Exception as err:
        return jsonify({"erro": f"Erro ao excluir livro: {err}"}), 500

# ------------------------------------------------------------------------------------------------------------
# ROTA 6: IMPORTAR LIVRO VIA JSON (POST /livros/importar)
# ------------------------------------------------------------------------------------------------------------
@app.route("/livros/importar", methods=["POST"])
def importar_livro():
    """
    Importa um livro via JSON e salva no banco de dados.
    
    Similar à rota POST /livros, mas com uma mensagem de resposta diferente.
    Útil para distinguir entre criação normal e importação.
    
    Método HTTP: POST
    URL: /livros/importar
    Body: JSON com dados do livro
    
    Exemplo de requisição:
        POST /livros/importar
        Body: {"titulo": "Dom Casmurro", "autor": "Machado de Assis"}
    
    Resposta:
        - 200 OK: JSON com mensagem de sucesso e ID do livro
        - 400 Bad Request: Se o JSON for inválido
        - 500 Internal Server Error: Se houver erro ao importar
    """
    novo_livro = request.get_json()  # Obtém dados JSON da requisição
    
    # Verifica se recebeu JSON válido
    if not novo_livro:
        return jsonify({"erro": "JSON inválido"}), 400  # Bad Request
    
    # Se o livro não tiver ID, busca o próximo ID disponível no banco
    if "id" not in novo_livro:
        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("SELECT MAX(codg_livro_pk) as max_id FROM livros")
            result = cur.fetchone()
            novo_livro["id"] = (result[0] + 1) if result[0] else 1
            cur.close()
            conn.close()
        except Exception as err:
            return jsonify({"erro": f"Erro ao gerar ID: {err}"}), 500
    
    # Salva no banco de dados MySQL
    try:
        salvar_livro_no_banco(novo_livro)
        return jsonify({
            "mensagem": "Livro importado com sucesso", 
            "id": novo_livro["id"]
        })
    except Exception as err:
        return jsonify({"erro": f"Erro ao importar livro: {err}"}), 500

# ------------------------------------------------------------------------------------------------------------
# ROTA 7: IMPORTAR VÁRIOS LIVROS VIA CSV (POST /upload_csv)
# ------------------------------------------------------------------------------------------------------------
@app.route("/upload_csv", methods=["POST"])
def upload_csv():
    """
    Importa múltiplos livros de um arquivo CSV.
    
    Esta rota recebe um arquivo CSV via formulário HTML e importa todos os livros
    contidos no arquivo para o banco de dados.
    
    Método HTTP: POST
    URL: /upload_csv
    Form-Data:
        arquivo: Arquivo CSV com os livros
    
    Formato esperado do CSV:
        id,titulo,autor
        1,Dom Casmurro,Machado de Assis
        2,1984,George Orwell
    
    Comportamento:
        - Se o livro já existir (mesmo ID), atualiza os dados (UPSERT)
        - Se o livro não tiver ID no CSV, gera um ID automaticamente
        - Continua processando mesmo se houver erro em algum livro
        - Retorna mensagem flash com quantidade de livros importados
    
    Redireciona para a página inicial após o processamento.
    """
    # Verifica se um arquivo foi enviado no formulário
    file = request.files.get("arquivo")
    # request.files.get("arquivo") busca o arquivo enviado com o nome "arquivo"
    
    if not file or file.filename == "":
        # Se não houver arquivo, mostra mensagem de erro e redireciona
        flash("Nenhum arquivo selecionado", "error")
        return redirect(url_for("pagina_inicial"))
    
    try:
        # Converte o arquivo binário para texto e lê como CSV
        # TextIOWrapper converte o stream binário em texto com encoding UTF-8
        reader = csv.DictReader(TextIOWrapper(file, encoding="utf-8"))
        # csv.DictReader lê o CSV e retorna cada linha como um dicionário
        # A primeira linha do CSV é usada como chaves do dicionário
        
        livros_importados = 0  # Contador de livros importados com sucesso
        
        # Processa cada linha do CSV
        for row in reader:
            # Cria dicionário com os dados do livro
            livro = {
                "id": int(row.get("id", 0)) if row.get("id") else None,
                # Tenta converter o ID para inteiro, se não existir ou for vazio, usa None
                "titulo": row.get("titulo", ""),  # Título (vazio se não existir)
                "autor": row.get("autor", "")      # Autor (vazio se não existir)
            }
            
            # Se não tiver ID, busca o próximo disponível
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
                    return redirect(url_for("pagina_inicial"))
            
            # Salva no banco de dados (a função já faz UPSERT, então não duplica)
            try:
                salvar_livro_no_banco(livro)
                livros_importados += 1  # Incrementa o contador
            except Exception as err:
                # Se houver erro ao salvar um livro, imprime o erro mas continua com os próximos
                print(f"Erro ao salvar livro {livro['id']}: {err}")
                continue  # Continua com o próximo livro
        
        # Mostra mensagem de sucesso com a quantidade de livros importados
        flash(f"{livros_importados} livro(s) importado(s) com sucesso!", "success")
    except Exception as err:
        # Se houver erro ao processar o arquivo CSV
        flash(f"Erro ao processar arquivo CSV: {err}", "error")
    
    # REDIRECIONA para GET (POST-Redirect-GET pattern)
    # Isso evita que ao atualizar a página, o formulário seja reenviado
    return redirect(url_for("pagina_inicial"))





    

# ------------------------------------------------------------------------------------------------------------
# ROTA 8: BUSCAR LIVRO POR ID VIA WEB (GET /livros/<id>/buscar)
# ------------------------------------------------------------------------------------------------------------
@app.route("/livros/<int:id>/buscar", methods=["GET"])
def buscar_livro_web(id):
    """
    Busca um livro específico por ID e exibe em uma página de detalhes.
    
    Esta rota é usada pela interface web (não é uma API JSON).
    Busca o livro no banco e renderiza uma página HTML com os detalhes.
    
    Método HTTP: GET
    URL: /livros/<id>/buscar
    Parâmetros de URL:
        id (int): ID do livro a ser buscado
    
    Comportamento:
        - Se encontrar o livro, renderiza a página livro_detalhe.html
        - Se não encontrar, mostra mensagem de erro e redireciona para página inicial
    
    Nota: Esta rota renderiza HTML, não retorna JSON.
    """
    try:
        conn = get_conn()
        cur = conn.cursor(dictionary=True)
        # Busca o livro com o ID especificado
        cur.execute("SELECT codg_livro_pk as id, titulo, autor FROM livros WHERE codg_livro_pk = %s", (id,))
        livro = cur.fetchone()
        cur.close()
        conn.close()
        
        if not livro:
            # Se não encontrou, mostra mensagem de erro e redireciona
            flash("Livro não encontrado", "error")
            return redirect(url_for("pagina_inicial"))
        
        # Se encontrou, renderiza a página de detalhes com os dados do livro
        return render_template("livro_detalhe.html", livro=livro)
    except mysql.connector.Error as err:
        # Se houver erro no banco, mostra mensagem e redireciona
        flash(f"Erro ao buscar livro: {err}", "error")
        return redirect(url_for("pagina_inicial"))

# ------------------------------------------------------------------------------------------------------------
# ROTA 9: SERVER ARQUIVOS ESTÁTICOS (GET /static/<filename>)
# ------------------------------------------------------------------------------------------------------------
@app.route("/static/<path:filename>")
def static_files(filename):
    """
    Serve arquivos estáticos (CSS, JavaScript, imagens, etc).
    
    Esta rota permite que o Flask sirva arquivos estáticos da pasta templates.
    Útil para arquivos CSS e JavaScript que não são templates HTML.
    
    Método HTTP: GET
    URL: /static/<filename>
    Parâmetros de URL:
        filename: Nome do arquivo a ser servido (ex: style.css)
    
    Exemplo de uso:
        GET /static/style.css
        Retorna o conteúdo do arquivo style.css
    """
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    # Cria o caminho completo para a pasta templates
    return send_from_directory(templates_dir, filename)
    # send_from_directory serve o arquivo de forma segura

# ------------------------------------------------------------------------------------------------------------
# ROTA 10: PÁGINA INICIAL (INTERFACE WEB) (GET /)
# ------------------------------------------------------------------------------------------------------------
@app.route("/", methods=["GET"])
def pagina_inicial():
    """
    Página inicial da aplicação (interface web).
    
    Esta é a rota principal que renderiza a página HTML com a lista de livros.
    Também implementa a funcionalidade de BUSCA por nome/título do livro.
    
    Método HTTP: GET
    URL: /
    Parâmetros de Query (opcionais):
        busca: Nome ou parte do nome do livro para buscar
    
    Funcionalidades:
        1. Se houver parâmetro "busca" na URL, filtra os livros pelo título
        2. Se não houver busca, mostra todos os livros
        3. Renderiza o template index.html com os livros encontrados
    
    Exemplo de uso:
        GET /                    -> Mostra todos os livros
        GET /?busca=dom          -> Mostra apenas livros com "dom" no título
        GET /?busca=1984         -> Mostra apenas livros com "1984" no título
    
    Como funciona a busca:
        - A busca é feita usando LIKE no SQL, que permite busca parcial
        - Exemplo: buscar "dom" encontra "Dom Casmurro"
        - A busca não diferencia maiúsculas/minúsculas (depende da configuração do MySQL)
        - O caractere % no SQL significa "qualquer sequência de caracteres"
    """
    # Obtém o parâmetro "busca" da URL (query string)
    # request.args.get("busca", "") busca o parâmetro "busca" na URL
    # Se não existir, retorna "" (string vazia)
    # .strip() remove espaços em branco no início e fim
    nome_busca = request.args.get("busca", "").strip()
    
    if nome_busca:
        # Se o usuário digitou algo para buscar, filtra os livros
        try:
            conn = get_conn()
            cur = conn.cursor(dictionary=True)
            
            # Executa query SQL com LIKE para busca parcial
            # %{nome_busca}% significa: qualquer texto antes + nome_busca + qualquer texto depois
            # Exemplo: se buscar "dom", encontra "Dom Casmurro", "Dom Quixote", etc.
            cur.execute(
                "SELECT codg_livro_pk as id, titulo, autor FROM livros WHERE titulo LIKE %s ORDER BY codg_livro_pk",
                (f"%{nome_busca}%",)  # Adiciona % antes e depois do termo de busca
            )
            livros = cur.fetchall()  # Busca todos os resultados
            cur.close()
            conn.close()
        except mysql.connector.Error as err:
            # Se houver erro, imprime e retorna lista vazia
            print(f"Erro ao buscar livros: {err}")
            livros = []
    else:
        # Se não houver busca, carrega todos os livros
        livros = carregar_livros_do_banco()
    
    # Renderiza o template HTML passando os livros e o termo de busca
    # O template pode usar a variável "busca" para manter o campo de busca preenchido
    return render_template("index.html", livros=livros, busca=nome_busca)

# ------------------------------------------------------------------------------------------------------------
# ROTA 11: EXCLUIR LIVRO VIA INTERFACE WEB (POST /livros/<id>/excluir)
# ------------------------------------------------------------------------------------------------------------
@app.route("/livros/<int:id>/excluir", methods=["POST"])
def excluir_livro_web(id):
    """
    Exclui um livro via interface web.
    
    Esta rota é chamada quando o usuário clica no botão "Excluir" na página web.
    Diferente da rota DELETE /livros/<id> que é uma API JSON, esta rota:
    - Mostra mensagens flash (sucesso/erro) para o usuário
    - Redireciona para a página inicial após excluir
    
    Método HTTP: POST
    URL: /livros/<id>/excluir
    Parâmetros de URL:
        id (int): ID do livro a ser excluído
    
    Comportamento:
        - Tenta excluir o livro do banco
        - Se conseguir, mostra mensagem de sucesso
        - Se não encontrar, mostra mensagem de erro
        - Sempre redireciona para a página inicial
    """
    try:
        if excluir_livro_do_banco(id):
            # Se excluiu com sucesso, mostra mensagem de sucesso
            flash("Livro excluído com sucesso!", "success")
        else:
            # Se não encontrou o livro, mostra mensagem de erro
            flash("Livro não encontrado", "error")
    except Exception as err:
        # Se houver erro, mostra mensagem com detalhes
        flash(f"Erro ao excluir livro: {err}", "error")
    
    # REDIRECIONA para GET (POST-Redirect-GET pattern)
    # Isso evita que ao atualizar a página, a exclusão seja repetida
    return redirect(url_for("pagina_inicial"))

# ============================================================================================================
# INICIALIZAÇÃO DO SERVIDOR
# ============================================================================================================
if __name__ == "__main__":
    """
    Este bloco só é executado quando o arquivo é rodado diretamente
    (não quando é importado como módulo).
    
    Inicia o servidor Flask na porta 5000.
    """
    # Inicia o servidor Flask
    app.run(
        port=5000,          # Porta onde o servidor vai rodar
        host='localhost',   # Endereço do servidor (localhost = apenas na máquina local)
        debug=True          # Modo debug ativado (mostra erros detalhados e recarrega automaticamente)
    )
    # Para acessar a aplicação, abra o navegador em: http://localhost:5000

# ============================================================================================================
# FIM DO ARQUIVO
# ============================================================================================================
