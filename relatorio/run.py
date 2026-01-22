from app import create_app

# Cria a instância do aplicativo
app = create_app()

if __name__ == "__main__":
    """Ponto de entrada da aplicação."""
    print("Iniciando o Sistema de Monitoramento de Relatórios...")
    app.run(
        port=5000,
        host='localhost',
        debug=True
    )
