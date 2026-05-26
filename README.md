# 🎮 Professor Simulator Clicker

> Um jogo incremental (clicker) temático com Pokémon, desenvolvido em **FastAPI** + **PostgreSQL** + **HTML/CSS/JS**

![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)
![Python](https://img.shields.io/badge/python-3.9+-blue)
![FastAPI](https://img.shields.io/badge/fastapi-0.104.1-green)
![License](https://img.shields.io/badge/license-MIT-purple)

## 🌟 Sobre o Projeto

**Professor Simulator Clicker** é um jogo incremental divertido onde você simula a vida de um professor de Pokémon! Clique, compre melhorias, construa seu inventário e colecione Pokémon enquanto gerencia seus recursos.

### ✨ Funcionalidades

* **Sistema de Cliques** - Ganhe moedas a cada clique
* **Loja de Upgrades** - Compre melhorias para aumentar sua renda
* **Inventário** - Gerencie seus itens e recursos
* **Pokedex** - Colecione e acompanhe seus Pokémon
* **Sistema de Usuários** - Crie sua conta e progresso persistente
* **Torneio Pokémon** - Inscreva seu time em torneios de 2, 4 ou 8 participantes e enfrente bots de outros treinadores para ganhar prêmios baseados nos status (BST) dos Pokémon
* **API RESTful** - Backend robusto com FastAPI
* **Banco de Dados** - Dados persistidos com PostgreSQL

---

## 🚀 Quick Start (Como Executar o Projeto)

#### Pré-requisitos
* Python 3.9+ instalado
* Docker e Docker Compose instalados
* VS Code com a extensão "Live Server" (ou similar)

#### Passos

**1. Clonar o repositório:**
```bash
git clone [https://github.com/jjvaldezzzzz/professor-simulator-clicker.git](https://github.com/jjvaldezzzzz/professor-simulator-clicker.git)
cd professor-simulator-clicker
```

**2. Iniciar o Banco de Dados (PostgreSQL via Docker):**
Levante o container do banco de dados (os scripts `.sql` serão rodados automaticamente).
```bash
docker-compose up -d
```

**3. Configurar e Iniciar o Backend (FastAPI):**
Crie um ambiente virtual, instale as dependências e inicie o servidor:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Instalar as dependências
pip install -r requirements.txt

# Iniciar o servidor backend localmente
uvicorn app.main:app --reload
```
*A API estará disponível em: http://localhost:8000*
*Documentação (Swagger): http://localhost:8000/docs*

**4. Iniciar o Frontend (Interface do Jogo):**
* Abra a pasta do projeto no VS Code.
* Navegue até a pasta `front-end` e abra o arquivo `index.html`.
* Clique com o botão direito na aba do arquivo ou no próprio código e selecione **"Open with Live Server"**.
* O jogo abrirá no seu navegador padrão (geralmente em `http://127.0.0.1:5500/front-end/index.html`).

---

## 📁 Estrutura do Projeto

```
professor-simulator-clicker/
├── app/                          # Backend FastAPI
│   ├── main.py                  # Configuração principal e inicialização do CORS
│   ├── database.py              # Conexão com PostgreSQL
│   ├── models.py                # Modelos do banco de dados
│   ├── schemas.py               # Esquemas Pydantic
│   └── routers/                 # Endpoints da API
│       ├── users.py             # 👤 Gerenciamento de usuários
│       ├── shop.py              # 🛒 Sistema de loja
│       ├── game.py              # 🎮 Lógica do jogo
│       ├── inventory.py         # 🎒 Gerenciamento de inventário
│       ├── pokemon.py           # 🐕 Sistema de Pokémon
│       └── tournament.py        # 🏆 Lógica e gerenciamento de Torneios
├── front-end/                    # Frontend HTML/CSS/JS
│   ├── index.html               # Página principal
│   ├── game.html                # Tela do jogo
│   ├── inventory.html           # Tela do inventário
│   ├── pokemon.html             # Tela de Pokémon
│   ├── shop.html                # Tela da loja
│   ├── tournament.html          # Tela de Torneios
│   ├── css/                     # Estilos
│   └── js/                      # Scripts do cliente
├── scripts/                      # Scripts SQL (Mapeados na inicialização do DB)
│   ├── init.sql                 # Criação de tabelas
│   └── seed.sql                 # Dados iniciais
├── tests/                        # Testes automatizados
│   └── TEST_CASES.md            # Acompanhamento de cenários de teste da Sprint 2
├── docker-compose.yml           # Configuração Docker
├── requirements.txt             # Dependências Python
└── README.md                    # Este arquivo
```

---

## 🛠️ Tecnologias Utilizadas

| Componente | Tecnologia |
|-----------|-----------|
| **Backend** | [FastAPI](https://fastapi.tiangolo.com/) 0.104.1 |
| **Servidor ASGI** | [Uvicorn](https://www.uvicorn.org/) 0.24.0 |
| **Banco de Dados** | PostgreSQL 15 |
| **ORM** | [SQLAlchemy](https://www.sqlalchemy.org/) 2.0.23 |
| **Validação** | [Pydantic](https://docs.pydantic.dev/) 2.4.2 |
| **HTTP Client** | [HTTPX](https://www.python-httpx.org/) 0.25.1 |
| **Testes** | [Pytest](https://pytest.org/) 7.4.3 |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Containerização** | Docker & Docker Compose |

---

## 📚 API Endpoints

### 👤 Usuários
```
POST   /users/register           # Registrar novo usuário
POST   /users/login              # Fazer login
GET    /users/{user_id}          # Obter dados do usuário
PUT    /users/{user_id}          # Atualizar dados do usuário
```

### 🎮 Jogo
```
POST   /game/click               # Registrar um clique
GET    /game/stats/{user_id}     # Obter estatísticas
GET    /game/leaderboard         # Ranking de jogadores
```

### 🛒 Loja
```
GET    /shop/items               # Listar itens disponíveis
POST   /shop/buy/{item_id}       # Comprar um item
GET    /shop/{user_id}/purchases # Histórico de compras
```

### 🎒 Inventário
```
GET    /inventory/{user_id}      # Listar inventário
POST   /inventory/add/{item_id}  # Adicionar item
DELETE /inventory/{item_id}      # Remover item
```

### 🐕 Pokémon
```
GET    /pokemon/available        # Pokémon disponíveis
POST   /pokemon/catch/{pokemon_id} # Capturar Pokémon
GET    /pokemon/{user_id}/pokedex # Pokedex do usuário
```

### 🏆 Torneios
```
POST   /torneio/{jogador_id}                                 # Criar novo torneio (2, 4 ou 8 participantes)
GET    /torneio/{jogador_id}                                 # Listar todos os torneios do jogador
GET    /torneio/{jogador_id}/{torneio_id}                    # Obter informações detalhadas de um torneio
POST   /torneio/{torneio_id}/partidas/{partida_id}/resolver  # Resolver o resultado de uma partida no torneio
DELETE /torneio/{torneio_id}                                 # Deletar um torneio (apenas se estiver finalizado)
```

**Documentação interativa:** http://localhost:8000/docs

---

## 🧪 Testes

O acompanhamento detalhado dos testes unitários, de integração e fluxo de dados (Sprint 2) pode ser visualizado no arquivo `tests/TEST_CASES.md`.

Execute os testes automatizados:

```bash
# Rodar todos os testes
pytest

# Rodar com cobertura
pytest --cov=app

# Rodar um teste específico
pytest tests/test_users.py -v

# Modo verboso
pytest -v
```

---

## SonarQube (Qualidade de Codigo)

O projeto ja vem configurado com SonarQube via `sonar-project.properties` e pelo workflow do GitHub Actions.

### Rodar localmente
1. Suba o SonarQube:
```bash
docker-compose -f docker-compose.sonarqube.yml up -d
```
2. Acesse http://localhost:9000 e crie um token em **My Account > Security**.
3. Gere os relatorios locais:
```bash
./run-tests.sh
```
4. Rode o scanner:
```bash
sonar-scanner -Dsonar.host.url=http://localhost:9000 -Dsonar.login=SEU_TOKEN
```

### CI (GitHub Actions)
- Configure os secrets `SONAR_HOST_URL` e `SONAR_TOKEN` no repositorio.

---

## 📝 Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Banco de Dados
DATABASE_URL=postgresql://postgres:suasenha@localhost:5432/isaac_db

# API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# Segurança
SECRET_KEY=sua_chave_secreta_super_segura
JWT_ALGORITHM=HS256
```

---

## 🐛 Troubleshooting

### Erro de conexão com PostgreSQL
```bash
# Verifique se o PostgreSQL está rodando
# Docker: docker-compose ps
# Local: psql -U postgres -d isaac_db

# Reinicie os serviços
docker-compose restart
```

### Porta 5433 já está em uso
```bash
# Mude a porta no docker-compose.yml
# Ou libere a porta:
# Windows: netstat -ano | findstr :5433
# Linux: lsof -i :5433
```

### CORS bloqueando requisições
* O acesso do Frontend já é liberado nativamente pelo sistema através do `CORSMiddleware` (com `allow_origins=["*"]`) configurado em `app.add_middleware()`. Se enfrentar problemas, revise a URL no seu arquivo de frontend local ou certifique-se de usar o Live Server.

### Inicialização do Banco de Dados pelo Docker
* Todos os arquivos com a extensão `.sql` localizados na pasta `./scripts` são automaticamente lidos e executados pela instância do Postgres durante o *build* inicial (volume mapeado em `/docker-entrypoint-initdb.d`), garantindo a correta montagem das tabelas.

---

## 📖 Documentação Adicional

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Pydantic](https://docs.pydantic.dev/)
- [PostgreSQL](https://www.postgresql.org/docs/)

---

## 👨‍💻 Contribuindo

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

<div align="center">

**⭐ Se este projeto foi útil, dê uma estrela!**

Made with 🎮 and ☕ by developers who love Pokemon

</div>