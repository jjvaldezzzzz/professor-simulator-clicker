-- ⬅️ INSERÇÃO DO ADMIN PADRÃO (O "DEUS" DO JOGO)
INSERT INTO jogador (nome, email, senha_hash, nome_exibicao, is_admin) 
VALUES ('Professor Isaac', 'isaac@ufpa.br', 'root', 'O Grande Mestre', TRUE)
ON CONFLICT (email) DO NOTHING;