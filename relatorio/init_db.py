import os
import mysql.connector
from dotenv import load_dotenv

# Carrega variáveis de ambiente
env_path = os.path.join(os.path.dirname(__file__), "..", "env")
load_dotenv(env_path)

def init_db():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "monitor_relatorio")
        )
        cursor = conn.cursor()
        
        # Lê o esquema SQL
        schema_path = os.path.join(os.path.dirname(__file__), "..", "schema.sql")
        with open(schema_path, 'r', encoding='utf-8') as f:
            sql_commands = f.read().split(';')
            
        for command in sql_commands:
            if command.strip():
                cursor.execute(command)
                print(f"Executando: {command[:50]}...")
        
        conn.commit()
        print("\n[OK] Banco de dados inicializado com sucesso!")
        
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        print(f"[ERRO] Falha ao inicializar banco: {err}")

if __name__ == "__main__":
    init_db()
