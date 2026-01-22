"""Script de teste para verificar conexão com MySQL"""
import os
import mysql.connector
from dotenv import load_dotenv

# Carrega variáveis de ambiente
env_path = os.path.join(os.path.dirname(__file__), "..", "env")
load_dotenv(env_path)

print("Testando conexão com MySQL...")
print(f"Host: {os.getenv('DB_HOST')}")
print(f"Port: {os.getenv('DB_PORT')}")
print(f"Database: {os.getenv('DB_NAME')}")
print(f"User: {os.getenv('DB_USER')}")
print()

try:
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "monitor_relatorio"),
        use_unicode=True,
        charset='utf8mb4',
        autocommit=False
    )
    
    print("[OK] Conexao estabelecida com sucesso!")
    
    # Testa se a tabela existe
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES LIKE 'livro'")
    result = cursor.fetchone()
    
    if result:
        print("[OK] Tabela 'livro' encontrada!")
        
        # Verifica estrutura da tabela
        cursor.execute("DESCRIBE livro")
        columns = cursor.fetchall()
        print("\nEstrutura da tabela:")
        for col in columns:
            print(f"  - {col[0]} ({col[1]})")
    else:
        print("[ERRO] Tabela 'livro' nao encontrada!")
        print("   Verifique se rodou o script de criacao.")
    
    cursor.close()
    conn.close()
    
except mysql.connector.Error as err:
    print(f"[ERRO] Erro ao conectar: {err}")
    print("\nPossíveis causas:")
    print("  1. MySQL não está rodando")
    print("  2. Credenciais incorretas no arquivo env")
    print("  3. Banco de dados não existe")
    print("  4. Firewall bloqueando a conexão")
