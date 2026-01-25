import os  # Sistema operacional para manipular caminhos de arquivos
import mysql.connector  # Conector oficial do MySQL
from dotenv import load_dotenv  # Carrega variáveis do arquivo de configuração (env)

# -----------------------------------------------------------------------------------------
# CONFIGURAÇÃO DE AMBIENTE
# -----------------------------------------------------------------------------------------
# O código abaixo localiza o arquivo "env" que está dois níveis acima deste arquivo
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
            autocommit=False
        )
    except mysql.connector.Error as err:
        print(f"Erro ao conectar ao MySQL: {err}")
        raise

# -----------------------------------------------------------------------------------------
# FUNÇÕES PARA MANIPULAÇÃO DE LIVROS
# -----------------------------------------------------------------------------------------

def carregar_livros_do_banco(limite=10, pagina=0, busca=""):
    """
    Busca livros da view vw_livros_vendas com paginação e busca centralizada.
    Garante que os aliases batam com o que o Frontend (JS/HTML) espera.
    """
    try:
        # OFFSET indica quantos registros pular (ex: Página 2 pula os 10 primeiros)
        offset = pagina * limite

        conn = get_conn()
        cur = conn.cursor(dictionary=True)

        # SQL com Aliases padronizados para o JS:
        # id, TITULO, GENERO, sinopse, nome_autor, cidade_autor, total_vendas
        sql = """
            SELECT 
                id, 
                TITULO, 
                GENERO, 
                SINOSPE AS sinopse, 
                nome_autor, 
                cidade_autor, 
                total_vendas
            FROM vw_livros_vendas
            WHERE TITULO LIKE %s
            ORDER BY total_vendas DESC
            LIMIT %s OFFSET %s
        """
        
        cur.execute(sql, (f"%{busca}%", limite, offset))
        livros = cur.fetchall()
        
        cur.close()
        conn.close()
        return livros

    except mysql.connector.Error as err:
        print(f"Erro ao carregar livros do banco: {err}")
        return []

def contar_total_livros(busca=""):
    """
    Retorna a quantidade total de livros disponíveis (ou filtrados pela busca).
    Essencial para o cálculo de total de páginas no frontend.
    """
    try:
        conn = get_conn()
        cur = conn.cursor()
        
        if busca:
            cur.execute("SELECT COUNT(*) FROM vw_livros_vendas WHERE TITULO LIKE %s", (f"%{busca}%",))
        else:
            cur.execute("SELECT COUNT(*) FROM vw_livros_vendas")
            
        total = cur.fetchone()[0]
        cur.close()
        conn.close()
        return total
    except mysql.connector.Error as err:
        print(f"Erro ao contar livros: {err}")
        return 0

# -----------------------------------------------------------------------------------------
# FUNÇÕES PARA IMPORTAÇÃO DE DADOS (STORED PROCEDURES)
# -----------------------------------------------------------------------------------------

def importar_linha_csv(cursor, row, autores_vistos, livros_vistos):
    """
    Insere os dados de uma linha do CSV chamando a Stored Procedure sp_importar_linha.
    Suporta as variações de grafia 'SINOPSE' e 'SINOSPE' vindas do CSV.
    """
    try:
        # Tenta capturar a sinopse independente da grafia (com ou sem erro) no CSV
        sinopse = row.get("SINOPSE") or row.get("SINOSPE") or ""
        
        params = (
            int(row["CODG_AUTOR_PK"]),     # p_codg_autor
            row["NOME"],                   # p_nome_autor
            row["DATA_NASCIMENTO"],        # p_data_nascimento
            row["CIDADE"],                 # p_cidade_autor
            int(row["CODG_LIVRO_PK"]),     # p_codg_livro
            row["TITULO"],                 # p_titulo
            row["GENERO"],                 # p_genero
            sinopse,                       # p_sinopse
            int(row["CODG_VENDA_PK"]),     # p_codg_venda
            row["LOCAL"],                  # p_cidade_venda
            int(row["QUANTIDADE"])         # p_quantidade
        )

        cursor.callproc('sp_importar_linha', params)
        
        # Mantém controle de IDs para evitar duplicidade de processamento no mesmo lote
        autores_vistos.add(int(row["CODG_AUTOR_PK"]))
        livros_vistos.add(int(row["CODG_LIVRO_PK"]))

    except Exception as e:
        print(f"[ERRO IMPORT] Venda ID {row.get('CODG_VENDA_PK')}: {e}")
        raise

def excluir_livro_do_banco(id: int):
    """
    Remove um livro e suas vendas associadas.
    """
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM vendas WHERE CODG_LIVRO_FK = %s", (id,))
        cur.execute("DELETE FROM livro WHERE CODG_LIVRO_PK = %s", (id,))
        conn.commit()
        rows_affected = cur.rowcount
        cur.close()
        conn.close()
        return rows_affected > 0
    except mysql.connector.Error as err:
        print(f"Erro ao excluir livro: {err}")
        raise
