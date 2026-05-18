# 🎮 Professor Simulator Clicker

> Um jogo incremental (clicker) temático com Pokémon, desenvolvido em **FastAPI** + **PostgreSQL** + **HTML/CSS/JS**

![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)
![Python](https://img.shields.io/badge/python-3.9+-blue)
![FastAPI](https://img.shields.io/badge/fastapi-0.104.1-green)
![License](https://img.shields.io/badge/license-MIT-purple)

## 🌟 Sobre o Projeto

**Professor Simulator Clicker** é um jogo incremental divertido onde você simula a vida de um professor de Pokémon! Clique, compre melhorias, construa seu inventário e colecione Pokémon enquanto gerencia seus recursos.

### ✨ Funcionalidades

- 🎯 **Sistema de Cliques** - Ganhe moedas a cada clique
- 🛒 **Loja de Upgrades** - Compre melhorias para aumentar sua renda
- 🎒 **Inventário** - Gerencie seus itens e recursos
- 🐕 **Pokedex** - Colecione e acompanhe seus Pokémon
- 👤 **Sistema de Usuários** - Crie sua conta e progresso persistente
- 📊 **API RESTful** - Backend robusto com FastAPI
- 🗄️ **Banco de Dados** - Dados persistidos com PostgreSQL

---

## 🚀 Quick Start

#### Pré-requisitos
- Docker e Docker Compose instalados

#### Passos

**1. Clonar o repositório:**
```bash
git clone https://github.com/jjvaldezzzzz/professor-simulator-clicker.git
cd professor-simulator-clicker
```

**2. Crie um ambiente virtual:**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

**3. Instale as dependências:**
```bash
pip install -r requirements.txt
```


**4. Iniciar os serviços com Docker Compose:**
```bash
docker-compose up -d
```

**5. Pronto! Acesse:**
 - Interface: http://localhost:8000
 - API Docs: http://localhost:8000/docs
 - Postgres: localhost:5433 (user: postgres, pass: suasenha)


---

## 📁 Estrutura do Projeto

```
professor-simulator-clicker/
├── app/                          # Backend FastAPI
│   ├── main.py                  # Configuração principal
│   ├── database.py              # Conexão com PostgreSQL
│   ├── models.py                # Modelos do banco de dados
│   ├── schemas.py               # Esquemas Pydantic
│   └── routers/                 # Endpoints da API
│       ├── users.py             # 👤 Gerenciamento de usuários
│       ├── shop.py              # 🛒 Sistema de loja
│       ├── game.py              # 🎮 Lógica do jogo
│       ├── inventory.py         # 🎒 Gerenciamento de inventário
│       └── pokemon.py           # 🐕 Sistema de Pokémon
├── front-end/                    # Frontend HTML/CSS/JS
│   ├── index.html               # Página principal
│   ├── game.html                # Tela do jogo
│   ├── inventory.html           # Tela do inventário
│   ├── pokemon.html             # Tela de Pokémon
│   ├── shop.html                # Tela da loja
│   ├── css/                     # Estilos
│   └── js/                      # Scripts do cliente
├── scripts/                      # Scripts SQL
│   ├── init.sql                 # Criação de tabelas
│   └── seed.sql                 # Dados iniciais
├── tests/                        # Testes automatizados
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

**Documentação interativa:** http://localhost:8000/docs

---

## 🧪 Testes

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
- Verifique se a URL do frontend está configurada em `app.add_middleware()`
- Em desenvolvimento, `allow_origins=["*"]` permite qualquer origem

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
