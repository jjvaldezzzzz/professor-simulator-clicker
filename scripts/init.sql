-- Tabela de Jogadores (UC01, UC02, UC03)
CREATE TABLE IF NOT EXISTS jogador (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    nome_exibicao VARCHAR(50) DEFAULT 'Treinador Iniciante',
    saldo DECIMAL(10,2) DEFAULT 0.00 CHECK (saldo >= 0),
    tentativas_login INTEGER DEFAULT 0,
    bloqueado_ate TIMESTAMP,
    token_sessao VARCHAR(500),
    is_admin BOOLEAN DEFAULT FALSE, -- ⬅️ NOVA COLUNA PARA O ADMIN
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_login TIMESTAMP,
    ativo BOOLEAN DEFAULT TRUE
);

-- Índice para busca por email (login)
CREATE INDEX idx_jogador_email ON jogador(email);
CREATE INDEX idx_jogador_token ON jogador(token_sessao);

-- Tabela de Itens da Loja (UC07, UC08, UC09)
CREATE TABLE item (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    preco DECIMAL(10,2) NOT NULL CHECK (preco > 0),
    multiplicador DECIMAL(5,2) NOT NULL DEFAULT 1.00,
    tipo VARCHAR(50) NOT NULL, -- 'cafe', 'placa_video', 'cadeira', etc.
    raridade VARCHAR(20) DEFAULT 'comum', -- 'comum', 'raro', 'mitico'
    vendivel BOOLEAN DEFAULT TRUE,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ativo BOOLEAN DEFAULT TRUE
);

-- Índice para listagem da loja
CREATE INDEX idx_item_ativo ON item(ativo);

-- Tabela de Inventário (UC10, UC11, UC12)
CREATE TABLE inventario (
    id SERIAL PRIMARY KEY,
    jogador_id INTEGER NOT NULL REFERENCES jogador(id) ON DELETE CASCADE,
    item_id INTEGER NOT NULL REFERENCES item(id) ON DELETE RESTRICT,
    data_compra TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ativo BOOLEAN DEFAULT TRUE,
    UNIQUE(jogador_id, item_id) -- Evita duplicatas do mesmo item
);

-- Índices para consultas do inventário
CREATE INDEX idx_inventario_jogador ON inventario(jogador_id);
CREATE INDEX idx_inventario_item ON inventario(item_id);

-- Tabela de Times de Pokemon
CREATE TABLE time_pokemon (
    id SERIAL PRIMARY KEY,
    jogador_id INTEGER NOT NULL REFERENCES jogador(id) ON DELETE CASCADE,
    nome VARCHAR(50) NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ativo BOOLEAN DEFAULT TRUE
);

-- Índice para consulta dos times
CREATE INDEX idx_time_pokemon_jogador ON time_pokemon(jogador_id);

-- Tabela de Pokemon do Jogador (UC13, UC14, UC15)
CREATE TABLE pokemon_time (
    id SERIAL PRIMARY KEY,
    jogador_id INTEGER NOT NULL REFERENCES jogador(id) ON DELETE CASCADE,
    time_id INTEGER REFERENCES time_pokemon(id) ON DELETE SET NULL,
    pokemon_api_id INTEGER NOT NULL CHECK (pokemon_api_id BETWEEN 1 AND 1025),
    nome_pokemon VARCHAR(100) NOT NULL,
    sprite_url VARCHAR(500),
    apelido VARCHAR(50),
    data_obtido TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ativo BOOLEAN DEFAULT TRUE
);

-- Índice para consulta do time
CREATE INDEX idx_pokemon_jogador ON pokemon_time(jogador_id);
CREATE INDEX idx_pokemon_time_id ON pokemon_time(time_id);

-- Tabela de Transações/Histórico (UC04, UC05, UC06, UC10, UC12)
CREATE TABLE transacao (
    id SERIAL PRIMARY KEY,
    jogador_id INTEGER NOT NULL REFERENCES jogador(id) ON DELETE CASCADE,
    tipo VARCHAR(30) NOT NULL, -- 'ganho_aula', 'compra_item', 'venda_item', 'sorteio_pokemon', 'reset'
    valor DECIMAL(10,2) NOT NULL,
    descricao TEXT,
    data_transacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índice para histórico
CREATE INDEX idx_transacao_jogador ON transacao(jogador_id);
CREATE INDEX idx_transacao_data ON transacao(data_transacao);

-- Tabela de Configurações do Jogo (UC06)
CREATE TABLE config_game (
    id SERIAL PRIMARY KEY,
    jogador_id INTEGER NOT NULL REFERENCES jogador(id) ON DELETE CASCADE,
    config_key VARCHAR(50) NOT NULL,
    config_value TEXT,
    UNIQUE(jogador_id, config_key)
);

-- Tabela de Log de Autenticação (UC02 - segurança)
CREATE TABLE log_autenticacao (
    id SERIAL PRIMARY KEY,
    jogador_id INTEGER REFERENCES jogador(id) ON DELETE SET NULL,
    email_tentativa VARCHAR(255),
    ip_address VARCHAR(45),
    sucesso BOOLEAN NOT NULL,
    data_tentativa TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);