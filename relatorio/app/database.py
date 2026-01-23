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
















# -----------------------------------------------------------------------------------------
# FUNÇÕES PARA MANIPULAÇÃO DE LIVROS
# -----------------------------------------------------------------------------------------
def carregar_livros_do_banco():
    """
    Executa um comando SELECT para trazer todos os livros cadastrados.
    Retorna uma lista de dicionários para fácil manipulação no Flask/HTML.
    """
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
            GROUP BY l.CODG_LIVRO_PK, l.TITULO, l.GENERO, l.SINOSPE, a.NOME, a.CIDADE
            ORDER BY total_vendas DESC
        """)

        livros = cur.fetchall()
        cur.close()
        conn.close()
        return livros
    except mysql.connector.Error as err:
        print(f"Erro ao carregar livros do banco: {err}")
        return []













# -----------------------------------------------------------------------------------------
# FUNÇÕES PARA MANIPULAÇÃO DE LIVROS
# -----------------------------------------------------------------------------------------

def importar_linha_csv(cursor, row, autores_vistos, livros_vistos):
    """
    Insere os dados de uma linha do CSV nas tabelas correspondentes.
    Usa ON DUPLICATE KEY UPDATE para evitar erros de duplicidade.
    """
    # -------------------------------
    # Inserir AUTOR
    codg_autor = int(row["CODG_AUTOR_PK"])
    if codg_autor not in autores_vistos:
        cursor.execute(
            "INSERT INTO autor (CODG_AUTOR_PK, NOME, DATA_NASCIMENTO, CIDADE) "
            "VALUES (%s, %s, %s, %s) "
            "ON DUPLICATE KEY UPDATE NOME=VALUES(NOME), DATA_NASCIMENTO=VALUES(DATA_NASCIMENTO), CIDADE=VALUES(CIDADE)",
            (codg_autor, row["NOME"], row["DATA_NASCIMENTO"], row["CIDADE"])
        )
        autores_vistos.add(codg_autor)



    # -------------------------------
    # Inserir LIVRO
    codg_livro = int(row["CODG_LIVRO_PK"])
    if codg_livro not in livros_vistos:
        # Nota: Usamos SINOSPE para a coluna do banco, mas SINOPSE para ler do CSV
        cursor.execute(
            "INSERT INTO livro (CODG_LIVRO_PK, TITULO, GENERO, SINOSPE, CODG_AUTOR_FK) "
            "VALUES (%s, %s, %s, %s, %s) "
            "ON DUPLICATE KEY UPDATE TITULO=VALUES(TITULO), GENERO=VALUES(GENERO), SINOSPE=VALUES(SINOSPE), CODG_AUTOR_FK=VALUES(CODG_AUTOR_FK)",
            (codg_livro, row["TITULO"], row["GENERO"], row["SINOPSE"], codg_autor)
        )
        livros_vistos.add(codg_livro)






    # -------------------------------
    # Inserir VENDAS
    codg_venda = int(row["CODG_VENDA_PK"])
    # Nota: A tabela vendas no banco do usuário usa a coluna CIDADE, no snippet estava LOCAL
    cursor.execute(
        "INSERT INTO vendas (CODG_VENDA_PK, CIDADE, QUANTIDADE, CODG_LIVRO_FK) "
        "VALUES (%s, %s, %s, %s) "
        "ON DUPLICATE KEY UPDATE CIDADE=VALUES(CIDADE), QUANTIDADE=VALUES(QUANTIDADE), CODG_LIVRO_FK=VALUES(CODG_LIVRO_FK)",
        (codg_venda, row["LOCAL"], int(row["QUANTIDADE"]), codg_livro)
    )







def excluir_livro_do_banco(id: int):
    """
    Remove permanentemente um livro baseado no seu ID (Chave Primária).
    """
    try:
        conn = get_conn()
        cur = conn.cursor()
        # Deletar vendas primeiro devido a FK (opcional se houver ON DELETE CASCADE)
        cur.execute("DELETE FROM vendas WHERE CODG_LIVRO_FK = %s", (id,))
        cur.execute("DELETE FROM livro WHERE CODG_LIVRO_PK = %s", (id,))
       #cur.execute("DELETE FROM autor WHERE CODG_AUTOR_PK = %s", (id,))
        conn.commit()
        rows_affected = cur.rowcount
        cur.close()
        conn.close()
        return rows_affected > 0
    except mysql.connector.Error as err:
        print(f"Erro ao excluir livro do banco: {err}")
        raise
