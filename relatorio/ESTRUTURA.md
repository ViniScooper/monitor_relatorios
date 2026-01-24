# 📂 Estrutura de Pastas e Arquivos

Este documento explica como o projeto está organizado e o porquê de cada pasta e arquivo existir. O sistema segue o padrão **Application Factory** e utiliza **Blueprints** para manter o código limpo e escalável.

## 🌳 Árvore do Projeto

```text
monitor_relatorios/           # Raiz do projeto
├── relatorio/                # Pasta principal da aplicação Flask
│   ├── app/                  # Lógica central do sistema
│   │   ├── routes/           # Organização das rotas (URLs)
│   │   │   ├── api_routes.py # Endpoints que retornam JSON (API REST)
│   │   │   └── web_routes.py # Rotas que renderizam o site (HTML)
│   │   ├── database.py       # Toda a lógica de SQL e conexão com o banco
│   │   └── __init__.py       # Onde o Flask é configurado e inicializado
│   ├── templates/            # Arquivos HTML da interface visual
│   │   └── index.html        # Dashboard principal do sistema
│   ├── run.py                # O "controle remoto" que liga o servidor
│   ├── DOCUMENTACAO.md       # Guia geral de uso do sistema
│   ├── ESTRUTURA.md          # Este arquivo (guia de arquitetura)
│   └── init_db.py            # Script para criar as tabelas no banco pela primeira vez
├── env                       # Configurações sensíveis (usuário e senha do banco)
├── book.csv                  # Exemplo de arquivo para importação de dados
└── .venv/                    # Ambiente virtual do Python (bibliotecas instaladas)
```

---

## 🔍 Entendendo os Componentes

### 1. `relatorio/app/`
É o "cérebro" da aplicação.
- **`__init__.py`**: Transforma a pasta `app` em um pacote Python. Ele usa a função `create_app()` para configurar o Flask. Isso permite que você mude as configurações sem mexer no resto do código.
- **`database.py`**: Centraliza o acesso ao MySQL. Se você precisar mudar uma query SQL ou ajustar a lógica de importação do CSV, é aqui que deve mexer. Isso evita que o código de banco de dados fique espalhado por todo o projeto.

### 2. `relatorio/app/routes/`
Separa a interface do usuário da integração com outros sistemas.
- **`web_routes.py`**: Cuida do que o ser humano vê no navegador. Gerencia os formulários, as mensagens de sucesso/erro (flash) e o carregamento da página HTML.
- **`api_routes.py`**: Cuida do que máquinas e outros sistemas veem. Retorna apenas dados puros (JSON). É ideal se um dia você quiser criar um aplicativo de celular ou outro dashboard que consuma esses dados.

### 3. `relatorio/templates/`
Contém o visual. O Flask usa uma tecnologia chamada *Jinja2* para injetar os dados do Python dentro do HTML do arquivo `index.html`.

### 4. `relatorio/run.py`
É o ponto de entrada. Ao executar este arquivo, o sistema carrega todas as configurações da pasta `app` e coloca o servidor no ar.

---

## 💡 Por que essa estrutura?

1.  **Separação de Responsabilidades**: O código que lida com o banco de dados não sabe nada sobre HTML, e o código das rotas não precisa saber como o SQL foi escrito. Isso facilita achar e corrigir bugs.
2.  **Organização**: Se o projeto crescer (adicionar usuários, novos tipos de relatórios, etc.), basta criar novos arquivos dentro de `routes/` e registrá-los no `__init__.py`.
3.  **Segurança**: O arquivo `env` fica na raiz, fora da pasta de código, para garantir que as senhas do banco de dados não sejam incluídas acidentalmente em compartilhamentos de código.
