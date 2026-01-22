import os  # Sistema operacional para manipular caminhos de arquivos
import mysql.connector  # Conector oficial do MySQL
from dotenv import load_dotenv  # Carrega variáveis do arquivo de configuração (env)

# -----------------------------------------------------------------------------------------
# CONFIGURAÇÃO DE AMBIENTE
# -----------------------------------------------------------------------------------------
# O código abaixo localiza o arquivo "env" que está dois níveis acima deste arquivo
# Caminho: relatorio/app/database.py -> relatorio/app -> relatorio -> raiz (onde está o env)
env_path = os.path.join(os.path.dirname(__file__), "..", "..", "env")
load_dotenv(env_path)

def get_conn():
    """
    Estabelece uma conexão ativa com o banco de dados MySQL.
    Busca as credenciais (host, user, password) no arquivo de configuração.
    """
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "monitor_relatorio"),
            use_unicode=True,
            charset='utf8mb4',
            autocommit=False  # Requer commit manual para salvar alterações
        )
    except mysql.connector.Error as err:
        print(f"Erro ao conectar ao MySQL: {err}")
        raise

def carregar_livros_do_banco():
    """
    Executa um comando SELECT para trazer todos os livros cadastrados.
    Retorna uma lista de dicionários para fácil manipulação no Flask/HTML.
    """
    try:
        conn = get_conn()
        # dictionary=True faz o banco devolver {'titulo': '...', 'autor': '...'} em vez de tupla
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT codg_livro_pk as id, titulo, autor FROM livros ORDER BY codg_livro_pk")
        livros = cur.fetchall()
        cur.close()
        conn.close()
        return livros
    except mysql.connector.Error as err:
        print(f"Erro ao carregar livros do banco: {err}")
        return []

def salvar_livro_no_banco(livro: dict):
    """
    Salva ou atualiza um livro (Lógica de UPSERT).
    Se o ID já existir, atualiza. Se não existir, insere um novo.
    """
    try:
        conn = get_conn()
        cur = conn.cursor()
        # ON DUPLICATE KEY UPDATE: Parte mágica do SQL que decide entre salvar novo ou atualizar velho
        cur.execute(
            "INSERT INTO livros (codg_livro_pk, titulo, autor) VALUES (%s, %s, %s) "
            "ON DUPLICATE KEY UPDATE titulo=VALUES(titulo), autor=VALUES(autor)",
            (livro["id"], livro.get("titulo", ""), livro.get("autor", "")),
        )
        conn.commit()  # ESSENCIAL: Sem isso, as mudanças não são gravadas no disco
        cur.close()
        conn.close()
    except mysql.connector.Error as err:
        print(f"Erro ao salvar livro no banco: {err}")
        raise

def excluir_livro_do_banco(id: int):
    """
    Remove permanentemente um livro baseado no seu ID (Chave Primária).
    """
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM livros WHERE codg_livro_pk = %s", (id,))
        conn.commit()
        rows_affected = cur.rowcount  # Verifica se alguma linha foi realmente apagada
        cur.close()
        conn.close()
        return rows_affected > 0
    except mysql.connector.Error as err:
        print(f"Erro ao excluir livro do banco: {err}")
        raise
