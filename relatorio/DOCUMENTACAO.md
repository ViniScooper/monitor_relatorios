# 📊 Sistema de Monitoramento de Relatórios - Livros, Autores e Vendas

Este projeto é um sistema de monitoramento de relatórios desenvolvido em **Python** com **Flask** e **MySQL**. Ele agora suporta uma estrutura relacional completa, permitindo o acompanhamento de livros, seus respectivos autores e dados de vendas por cidade.

## 📂 Estrutura do Projeto

O sistema utiliza o padrão **Application Factory** e **Blueprints**, garantindo modularidade:

```text
monitor_relatorios/
├── relatorio/              # Pasta raiz da aplicação
│   ├── app/                # Lógica central (Python)
│   │   ├── routes/         # Divisão de rotas
│   │   │   ├── api_routes.py  # Endpoints JSON (API REST)
│   │   │   └── web_routes.py  # Interface Web (HTML)
│   │   ├── database.py      # Queries SQL e Lógica de Importação
│   │   └── __init__.py      # Fábrica do Aplicativo
│   ├── templates/          # Interface Visual (HTML/CSS)
│   │   └── index.html      # Dashboard Premium
│   └── run.py              # Script para iniciar o servidor
├── env                     # Configurações do Banco de Dados
└── book.csv                # Arquivo de dados para importação
```

---

## 🛠️ Arquitetura de Banco de Dados

O sistema utiliza três tabelas relacionadas para gerenciar os dados:

1.  **AUTOR**: Dados dos escritores (`NOME`, `DATA_NASCIMENTO`, `CIDADE`).
2.  **LIVRO**: Dados das obras (`TITULO`, `GENERO`, `SINOSPE`) vinculadas a um autor.
3.  **VENDAS**: Registros de vendas por cidade vinculados a um livro.

---

## 🚀 Funcionalidades Principais

### 1. Importação Inteligente (CSV)
O sistema processa relatórios brutos em CSV. Ao importar:
*   **Normalização**: Divide os dados entre as tabelas de Autores, Livros e Vendas.
*   **Upsert (ON DUPLICATE KEY)**: Atualiza registros existentes em vez de criar duplicatas.
*   **Integridade**: Garante que o autor exista antes de criar o livro, e o livro antes da venda.

### 2. Dashboard Premium
Uma interface moderna e responsiva que exibe:
*   Cards detalhados para cada livro.
*   Informações do autor e cidade de origem.
*   Cálculo automático do **Total de Vendas** agregando dados da tabela de vendas.
*   Busca em tempo real por título.

### 3. API REST
Endpoints para integração com outros sistemas:
*   `GET /api/livros`: Lista completa de livros com estatísticas.
*   `GET /api/livros/<id>`: Detalhes de um livro específico.
*   `DELETE /api/livros/<id>`: Remoção de registros.
*   `POST /api/livros/`: ADICIONAR LIVROS.

---

## 📋 Como Utilizar

### Requisitos
*   Python 3.x e MySQL.
*   Instalar dependências: `flask`, `mysql-connector-python`, `python-dotenv`.

### Execução
1.  Configure suas credenciais no arquivo `env`.
2.  Inicie o servidor:
    ```powershell
    python relatorio/run.py
    ```
3.  Acesse `http://localhost:5000` no navegador.
4.  Use o botão de **Importar CSV** para carregar o arquivo `book.csv`.

---
*Documentação atualizada em 2026-01-22 refletindo a nova estrutura relacional.*
