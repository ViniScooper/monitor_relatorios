# 📊 Sistema de Monitoramento de Relatórios - Livros

Este projeto é um sistema de gerenciamento de livros desenvolvido em **Python** utilizando o framework **Flask** e banco de dados **MySQL**. Ele permite o gerenciamento completo (CRUD) de livros através de uma interface web amigável e uma API REST.

## 📂 Estrutura do Projeto

O sistema está organizado seguindo as melhores práticas de desenvolvimento Flask (**Application Factory** e **Blueprints**), separando responsabilidades para facilitar a manutenção:

```text
monitor_relatorios/
├── relatorio/              # Pasta raiz do código da aplicação
│   ├── app/                # Pacote principal da aplicação (Lógica Python)
│   │   ├── routes/         # Divisão das rotas do sistema
│   │   │   ├── __init__.py    # Registra e inicializa os Blueprints
│   │   │   ├── api_routes.py  # Rotas que retornam JSON (API REST)
│   │   │   └── web_routes.py  # Rotas HTML (Interface do Usuário)
│   │   ├── __init__.py     # Fábrica do Aplicativo (Configura o Flask)
│   │   └── database.py      # Módulo de Banco de Dados (Queries SQL)
│   ├── templates/          # Arquivos visuais (HTML/CSS)
│   │   └── index.html      # Página única do sistema
│   ├── run.py              # Script principal para iniciar o sistema
│   └── test_connection.py  # Script para testar a conexão com o banco
├── env                     # Variáveis de ambiente (Configuração do DB)
└── book.csv                # Exemplo de arquivo para importação
```

---

## 🛠️ Detalhamento das Pastas e Arquivos

### 1. `relatorio/app/`
É o "corpo" do sistema. Aqui reside toda a lógica de processamento.
*   **`database.py`**: Centraliza toda a comunicação com o MySQL. Contém funções como `salvar_livro_no_banco` e `carregar_livros_do_banco`. Se precisar mudar algo no banco, seu lugar é aqui.
*   **`__init__.py`**: Contém a função `create_app`. Ela configura o Flask, define as chaves de segurança e junta as peças (Blueprints e caminhos de templates).

### 2. `relatorio/app/routes/`
Separa como o sistema responde às requisições.
*   **`web_routes.py`**: Gerencia o que o usuário vê. Processa o envio de formulários, faz o upload do CSV e renderiza as páginas HTML.
*   **`api_routes.py`**: Transforma o sistema em uma API. Útil para conectar outros sistemas ou aplicativos que precisam ler ou escrever dados em formato JSON.

### 3. `relatorio/templates/`
Contém a interface visual. O Flask busca os arquivos aqui para "desenhar" a página no navegador do usuário.

### 4. `relatorio/run.py`
É o botão de "Ligar". Em vez de rodar arquivos internos, você sempre deve executar este arquivo para garantir que toda a estrutura de pastas seja carregada corretamente.

---

## 🚀 Como Funciona

### Fluxo de Dados:
1.  **Entrada**: O usuário interage com a página (`index.html`) ou faz uma chamada à API.
2.  **Roteamento**: O Flask recebe a chamada através das **Routes** (web ou api).
3.  **Processamento**: A rota chama uma função no arquivo **database.py**.
4.  **Banco de Dados**: O sistema executa os comandos SQL no MySQL usando as credenciais do arquivo **env**.
5.  **Resposta**: Os dados voltam do banco e são exibidos na tela para o usuário.

### Funcionalidades Principais:
*   **Busca em tempo real**: Filtra livros pelo título usando comandos SQL `LIKE`.
*   **Importação Massiva**: Lê arquivos CSV, gera IDs automaticamente se necessário e salva tudo no banco com um clique.
*   **Mensagens Flash**: Avisos visuais que confirmam o sucesso de uma operação ou explicam erros.

---

## 📋 Pré-requisitos
*   Python 3.x
*   MySQL Server
*   Bibliotecas: `flask`, `mysql-connector-python`, `python-dotenv`.

Para rodar o sistema:
```powershell
cd relatorio
python run.py
```
