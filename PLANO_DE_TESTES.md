# Plano de Testes — Professor Simulator Clicker

## Visão Geral

Este documento descreve a estratégia de testes em **3 níveis** para o Professor Simulator Clicker:

1. **Testes Unitários (UT)**: Validam funções, métodos e componentes isolados.
2. **Testes de Integração (IT)**: Verificam comunicação entre camadas, banco de dados e APIs externas.
3. **Testes End-to-End (E2E)**: Simulam fluxos reais do usuário no navegador.

Cada caso de uso (UC) possui casos de teste documentados com:
- **ID**: Identificador único
- **Objetivo**: O que será testado
- **Pré-condições**: Estado do sistema antes do teste
- **Dados de Entrada**: Inputs do teste
- **Passos de Execução**: Como executar
- **Resultado Esperado**: Output desejado
- **Resultado Obtido**: Output real (preenchido após execução)
- **Status**: Aprovado/Reprovado

---

## Ferramentas Utilizadas

- **Framework de Testes**: PyTest (Python backend)
- **Testes Unitários**: PyTest + coverage
- **Testes de Integração**: PyTest + TestClient (FastAPI)
- **Testes E2E**: Playwright (navegador real)
- **Análise Estática**: SonarQube (complexidade, duplicação, code smells, vulnerabilidades)
- **Cobertura de Código**: pytest-cov (meta: 70–100%)

---

## Matriz de Testes por Caso de Uso

### **PERFIL DO USUÁRIO (UC01–UC04)**

#### UC01 — Cadastrar Jogador

| Aspecto | Detalhes |
|---------|----------|
| **Testes Unitários** | UT-UC01-001, UT-UC01-002, UT-UC01-003 |
| **Testes de Integração** | IT-UC01-001, IT-UC01-002, IT-UC01-003 |
| **Testes E2E** | E2E-UC01-001 |
| **Cobertura Esperada** | 90%+ |

**UT-UC01-001**: Validação de email obrigatório
- Objetivo: Garantir que `JogadorCreate` rejeita email vazio
- Pré-condições: Nenhuma
- Dados de entrada: `{"nome": "João", "email": "", "senha": "123"}`
- Passos: Criar instância de `JogadorCreate` com email vazio
- Resultado esperado: `ValidationError` lançado
- Resultado obtido: *(a preencher após execução)*
- Status: *(a preencher após execução)*

**UT-UC01-002**: Validação de nome obrigatório
- Objetivo: Garantir que `JogadorCreate` rejeita nome vazio
- Pré-condições: Nenhuma
- Dados de entrada: `{"nome": "", "email": "teste@example.com", "senha": "123"}`
- Passos: Criar instância de `JogadorCreate` com nome vazio
- Resultado esperado: `ValidationError` lançado
- Resultado obtido: *(a preencher após execução)*
- Status: *(a preencher após execução)*

**UT-UC01-003**: Validação de formato de email
- Objetivo: Garantir que `JogadorCreate` aceita email válido
- Pré-condições: Nenhuma
- Dados de entrada: `{"nome": "João", "email": "joao@example.com", "senha": "123"}`
- Passos: Criar instância de `JogadorCreate`
- Resultado esperado: Instância criada com sucesso
- Resultado obtido: *(a preencher após execução)*
- Status: *(a preencher após execução)*

**IT-UC01-001**: Cadastro com sucesso (HTTP 201)
- Objetivo: Validar que jogador é criado e persistido
- Pré-condições: Banco de dados vazio; servidor rodando
- Dados de entrada: `POST /jogadores/` com `{"nome": "Ana", "email": "ana@test.com", "senha": "senha123"}`
- Passos:
  1. Enviar POST request
  2. Verificar status 201
  3. Consultar BD para validar persistência
- Resultado esperado: Jogador criado, `nome_exibicao` default = "Treinador Iniciante", `saldo` = 0
- Resultado obtido: *(a preencher após execução)*
- Status: *(a preencher após execução)*

**IT-UC01-002**: Rejeitar email duplicado (HTTP 400)
- Objetivo: Garantir que emails únicos
- Pré-condições: Jogador com email "dup@test.com" já existe
- Dados de entrada: `POST /jogadores/` com `{"nome": "Outro", "email": "dup@test.com", "senha": "123"}`
- Passos:
  1. Enviar POST request
  2. Verificar status 400
  3. Verificar mensagem de erro
- Resultado esperado: HTTP 400 com "Email já cadastrado"
- Resultado obtido: *(a preencher após execução)*
- Status: *(a preencher após execução)*

**IT-UC01-003**: Validação de email mal formado (HTTP 422)
- Objetivo: Garantir validação de formato
- Pré-condições: Nenhuma
- Dados de entrada: `POST /jogadores/` com `{"nome": "João", "email": "invalido", "senha": "123"}`
- Passos:
  1. Enviar POST request
  2. Verificar status 422
- Resultado esperado: HTTP 422 (Validation Error)
- Resultado obtido: *(a preencher após execução)*
- Status: *(a preencher após execução)*

**E2E-UC01-001**: Fluxo completo de cadastro via navegador
- Objetivo: Validar cadastro do usuário final
- Pré-condições: Navegador aberto; app rodando; homepage visível
- Dados de entrada: Nome="Maria", Email="maria@test.com", Senha="senha123"
- Passos:
  1. Clicar no botão "Registrar"
  2. Preencher formulário
  3. Clicar "Enviar"
  4. Validar redirecionamento para login
- Resultado esperado: Conta criada; redirecionamento para login
- Resultado obtido: *(a preencher após execução)*
- Status: *(a preencher após execução)*

---

#### UC02 — Autenticar Jogador

| Aspecto | Detalhes |
|---------|----------|
| **Testes Unitários** | UT-UC02-001 |
| **Testes de Integração** | IT-UC02-001, IT-UC02-002, IT-UC02-003 |
| **Testes E2E** | E2E-UC02-001 |

**UT-UC02-001**: Validação de schema de login
- Objetivo: Garantir que `JogadorLogin` valida email e senha
- Pré-condições: Nenhuma
- Dados de entrada: `{"email": "test@example.com", "senha": "123"}`
- Passos: Criar instância de `JogadorLogin`
- Resultado esperado: Instância criada com sucesso
- Resultado obtido: *(a preencher)*
- Status: *(a preencher)*

**IT-UC02-001**: Login com credenciais válidas (HTTP 200)
- Objetivo: Autenticar jogador e retornar token
- Pré-condições: Jogador "user@test.com" com senha "senha123" existe
- Dados de entrada: `POST /jogadores/login` com `{"email": "user@test.com", "senha": "senha123"}`
- Passos:
  1. Enviar POST request
  2. Verificar status 200
  3. Validar presença de `jogador_id`, `token`, `is_admin`
- Resultado esperado: HTTP 200 com token e `is_admin` correto
- Resultado obtido: *(a preencher)*
- Status: *(a preencher)*

**IT-UC02-002**: Login com senha incorreta (HTTP 401)
- Objetivo: Rejeitar credenciais inválidas
- Pré-condições: Jogador "user@test.com" com senha "correta" existe
- Dados de entrada: `POST /jogadores/login` com `{"email": "user@test.com", "senha": "incorreta"}`
- Passos:
  1. Enviar POST request
  2. Verificar status 401
- Resultado esperado: HTTP 401 com "Credenciais inválidas"
- Resultado obtido: *(a preencher)*
- Status: *(a preencher)*

**IT-UC02-003**: Login com email inexistente (HTTP 401)
- Objetivo: Rejeitar login de usuário não existente
- Pré-condições: Email "inexistente@test.com" não existe
- Dados de entrada: `POST /jogadores/login` com `{"email": "inexistente@test.com", "senha": "123"}`
- Passos:
  1. Enviar POST request
  2. Verificar status 401
- Resultado esperado: HTTP 401 com "Credenciais inválidas"
- Resultado obtido: *(a preencher)*
- Status: *(a preencher)*

**E2E-UC02-001**: Login completo via navegador
- Objetivo: Validar fluxo de autenticação
- Pré-condições: Jogador com email "e2e@test.com" e senha "senha123" existe; página de login visível
- Dados de entrada: Email="e2e@test.com", Senha="senha123"
- Passos:
  1. Digitar email no campo de email
  2. Digitar senha no campo de senha
  3. Clicar "Entrar"
  4. Validar redirecionamento para dashboard
- Resultado esperado: Redirecionamento para dashboard; token armazenado em localStorage
- Resultado obtido: *(a preencher)*
- Status: *(a preencher)*

---

#### UC03 — Atualizar Perfil (Nome de Exibição)

| Aspecto | Detalhes |
|---------|----------|
| **Testes Unitários** | UT-UC03-001, UT-UC03-002 |
| **Testes de Integração** | IT-UC03-001, IT-UC03-002, IT-UC03-003 |
| **Testes E2E** | E2E-UC03-001 |

**UT-UC03-001**: Validação de `JogadorUpdate` com nome válido
- Objetivo: Garantir que schema aceita nome válido
- Pré-condições: Nenhuma
- Dados de entrada: `{"nome_exibicao": "Mestre Pokémon"}`
- Passos: Criar instância de `JogadorUpdate`
- Resultado esperado: Instância criada com sucesso
- Resultado obtido: *(a preencher)*
- Status: *(a preencher)*

**UT-UC03-002**: Validação de caracteres proibidos
- Objetivo: Garantir que regex rejeita caracteres especiais
- Pré-condições: Nenhuma
- Dados de entrada: Nome com caracteres como `@`, `#`, `!`
- Passos: Executar validação de regex
- Resultado esperado: Rejeição do nome
- Resultado obtido: *(a preencher)*
- Status: *(a preencher)*

**IT-UC03-001**: Atualizar nome com sucesso (HTTP 200)
- Objetivo: Validar persistência do novo nome
- Pré-condições: Jogador com `id=1` existe
- Dados de entrada: `PUT /jogadores/1/perfil` com `{"nome_exibicao": "Novo Nome"}`
- Passos:
  1. Enviar PUT request
  2. Verificar status 200
  3. Consultar BD para validar mudança
- Resultado esperado: HTTP 200; `nome_exibicao` atualizado no BD
- Resultado obtido: *(a preencher)*
- Status: *(a preencher)*

**IT-UC03-002**: Rejeitar nome com caracteres inválidos (HTTP 400)
- Objetivo: Garantir validação de formato
- Pré-condições: Jogador com `id=1` existe
- Dados de entrada: `PUT /jogadores/1/perfil` com `{"nome_exibicao": "Nome@Inválido"}`
- Passos:
  1. Enviar PUT request
  2. Verificar status 400
- Resultado esperado: HTTP 400 com "caracteres invalidos"
- Resultado obtido: *(a preencher)*
- Status: *(a preencher)*

**IT-UC03-003**: Rejeitar nome vazio (HTTP 400)
- Objetivo: Garantir que nome não pode ser vazio
- Pré-condições: Jogador com `id=1` existe
- Dados de entrada: `PUT /jogadores/1/perfil` com `{"nome_exibicao": ""}`
- Passos:
  1. Enviar PUT request
  2. Verificar status 400
- Resultado esperado: HTTP 400 com "Nome de exibicao e obrigatorio"
- Resultado obtido: *(a preencher)*
- Status: *(a preencher)*

**E2E-UC03-001**: Atualizar perfil via UI
- Objetivo: Validar fluxo de edição de perfil
- Pré-condições: Usuário autenticado; página de perfil aberta
- Dados de entrada: Novo nome = "Campeão"
- Passos:
  1. Clicar no campo de nome
  2. Limpar valor anterior
  3. Digitar "Campeão"
  4. Clicar "Salvar"
  5. Validar atualização na tela
- Resultado esperado: Nome atualizado em tempo real na interface
- Resultado obtido: *(a preencher)*
- Status: *(a preencher)*

---

#### UC04 — Deletar Conta

| Aspecto | Detalhes |
|---------|----------|
| **Testes Unitários** | UT-UC04-001 |
| **Testes de Integração** | IT-UC04-001, IT-UC04-002 |
| **Testes E2E** | E2E-UC04-001 |

**UT-UC04-001**: Validação de privilégio (não admin)
- Objetivo: Garantir que apenas não-admins podem ser deletados
- Pré-condições: Função de verificação implementada
- Dados de entrada: `is_admin=False`
- Passos: Executar função de validação
- Resultado esperado: Deleção permitida
- Resultado obtido: *(a preencher)*
- Status: *(a preencher)*

**IT-UC04-001**: Deletar conta com sucesso (HTTP 200)
- Objetivo: Remover jogador do BD
- Pré-condições: Jogador não-admin com `id=2` existe
- Dados de entrada: `DELETE /jogadores/2`
- Passos:
  1. Enviar DELETE request
  2. Verificar status 200
  3. Consultar BD; verificar que jogador não existe
- Resultado esperado: HTTP 200; registro deletado
- Resultado obtido: *(a preencher)*
- Status: *(a preencher)*

**IT-UC04-002**: Rejeitar deleção de admin (HTTP 403)
- Objetivo: Proteger conta admin
- Pré-condições: Admin com `id=1` e `is_admin=1` existe
- Dados de entrada: `DELETE /jogadores/1`
- Passos:
  1. Enviar DELETE request
  2. Verificar status 403
- Resultado esperado: HTTP 403 com "Conta admin nao pode ser deletada"
- Resultado obtido: *(a preencher)*
- Status: *(a preencher)*

**E2E-UC04-001**: Deletar conta via UI com confirmação
- Objetivo: Validar fluxo de deleção
- Pré-condições: Usuário não-admin autenticado; página de configurações visível
- Dados de entrada: Confirmação = "Sim"
- Passos:
  1. Clicar "Deletar Conta"
  2. Confirmar na modal
  3. Validar redirecionamento para homepage
- Resultado esperado: Redirecionamento para homepage; conta removida
- Resultado obtido: *(a preencher)*
- Status: *(a preencher)*

---

### **LOJA E INVENTÁRIO (UC05–UC11)**

#### UC05 — Cadastrar Novo Item (Admin)

| Aspecto | Detalhes |
|---------|----------|
| **Testes Unitários** | UT-UC05-001, UT-UC05-002 |
| **Testes de Integração** | IT-UC05-001, IT-UC05-002, IT-UC05-003 |
| **Testes E2E** | E2E-UC05-001 |

**UT-UC05-001**: Validação de schema `ItemCreate`
- Objetivo: Garantir que item válido é aceito
- Pré-condições: Nenhuma
- Dados de entrada: `{"nome": "Café", "preco": 50.0, "multiplicador": 1.5, "tipo": "bebida", "raridade": "comum"}`
- Passos: Criar instância de `ItemCreate`
- Resultado esperado: Instância criada com sucesso
- Resultado obtido: *(a preencher)*
- Status: *(a preencher)*

**UT-UC05-002**: Validação de preço positivo
- Objetivo: Rejeitar preço <= 0
- Pré-condições: Nenhuma
- Dados de entrada: `{"nome": "Item", "preco": -10.0, ...}`
- Passos: Validar schema
- Resultado esperado: Validação falha ou app rejeita
- Resultado obtido: *(a preencher)*
- Status: *(a preencher)*

**IT-UC05-001**: Criar item com admin válido (HTTP 201)
- Objetivo: Persistir novo item na loja
- Pré-condições: Admin com `id=1` e `is_admin=1` existe
- Dados de entrada: `POST /loja/itens` com item válido e `jogador_id=1`
- Passos:
  1. Enviar POST request
  2. Verificar status 201
  3. Validar que item está no BD
- Resultado esperado: HTTP 201; item criado e ativo
- Resultado obtido: *(a preencher)*
- Status: *(a preencher)*

**IT-UC05-002**: Rejeitar criação sem privilégio admin (HTTP 403)
- Objetivo: Validar controle de acesso
- Pré-condições: Jogador não-admin com `id=2` existe
- Dados de entrada: `POST /loja/itens` com item válido e `jogador_id=2`
- Passos:
  1. Enviar POST request
  2. Verificar status 403
- Resultado esperado: HTTP 403 com "Acesso negado"
- Resultado obtido: *(a preencher)*
- Status: *(a preencher)*

**IT-UC05-003**: Registrar transação administrativa
- Objetivo: Validar log de ação admin
- Pré-condições: Admin com `id=1` existe
- Dados de entrada: Criar item "Notebook" (preco=5000)
- Passos:
  1. Enviar POST request
  2. Consultar tabela `transacao` filtrada por `jogador_id=1`
  3. Verificar se transação com tipo="admin_criar_item" foi criada
- Resultado esperado: Transação registrada com descrição do item
- Resultado obtido: *(a preencher)*
- Status: *(a preencher)*

**E2E-UC05-001**: Criar item via admin dashboard
- Objetivo: Validar UI de cadastro
- Pré-condições: Admin autenticado; admin panel visível
- Dados de entrada: Nome="Livro", Preço="100", Tipo="material"
- Passos:
  1. Navegar para "Gerenciar Loja"
  2. Clicar "Novo Item"
  3. Preencher formulário
  4. Clicar "Criar"
  5. Validar item em catálogo
- Resultado esperado: Item aparece no catálogo com preço correto
- Resultado obtido: *(a preencher)*
- Status: *(a preencher)*

---

#### UC06 — Visualizar Catálogo da Loja

| Aspecto | Detalhes |
|---------|----------|
| **Testes Unitários** | UT-UC06-001 |
| **Testes de Integração** | IT-UC06-001, IT-UC06-002 |
| **Testes E2E** | E2E-UC06-001 |

**UT-UC06-001**: Ordenação por preço (query)
- Objetivo: Validar que items são ordenados corretamente
- Pré-condições: 3 itens com preços diferentes
- Dados de entrada: Items: (nome="A", preco=100), (nome="B", preco=50), (nome="C", preco=75)
- Passos: Simular query `ORDER BY preco ASC`
- Resultado esperado: [B:50, C:75, A:100]
- Resultado obtido: *(a preencher)*
- Status: *(a preencher)*

**IT-UC06-001**: Listar itens da loja (HTTP 200)
- Objetivo: Retornar catálogo completo
- Pré-condições: 5 itens ativos existem no BD
- Dados de entrada: `GET /loja/itens`
- Passos:
  1. Enviar GET request
  2. Verificar status 200
  3. Contar items na resposta
  4. Validar ordenação por preço
- Resultado esperado: HTTP 200 com 5 items ordenados por preço
- Resultado obtido: *(a preencher)*
- Status: *(a preencher)*

**IT-UC06-002**: Listar com catálogo vazio
- Objetivo: Validar resposta quando sem itens
- Pré-condições: Nenhum item ativo no BD
- Dados de entrada: `GET /loja/itens`
- Passos:
  1. Enviar GET request
  2. Verificar status 200
  3. Contar items na resposta
- Resultado esperado: HTTP 200 com lista vazia `[]`
- Resultado obtido: *(a preencher)*
- Status: *(a preencher)*

**E2E-UC06-001**: Visualizar catálogo no navegador
- Objetivo: Validar renderização da loja
- Pré-condições: 3 items em catálogo; homepage aberta
- Dados de entrada: Nenhuma
- Passos:
  1. Clicar em "Loja"
  2. Aguardar carregamento
  3. Validar que items aparecem
  4. Validar ordenação visual
- Resultado esperado: Items aparecem em ordem de preço; preços visíveis
- Resultado obtido: *(a preencher)*
- Status: *(a preencher)*

---

#### UC07–UC11 (Itens, Inventário)

*[Seguir o mesmo padrão de documentação para os casos UC07, UC08, UC09, UC10, UC11]*

---

### **TIMES POKÉMON (UC12–UC18)**

#### UC12 — Sortear Pokémon (Gacha)

| Aspecto | Detalhes |
|---------|----------|
| **Testes Unitários** | UT-UC12-001, UT-UC12-002 |
| **Testes de Integração** | IT-UC12-001, IT-UC12-002, IT-UC12-003 |
| **Testes E2E** | E2E-UC12-001 |

**UT-UC12-001**: Custo do gacha >= saldo
- Objetivo: Validar cálculo de saldo insuficiente
- Pré-condições: `CUSTO_GACHA = 100.0`
- Dados de entrada: `saldo = 50.0, custo = 100.0`
- Passos: Executar `saldo < custo`
- Resultado esperado: Resultado = `True` (saldo insuficiente)
- Resultado obtido: *(a preencher)*
- Status: *(a preencher)*

**UT-UC12-002**: Dedução de saldo após sorteio
- Objetivo: Validar cálculo de novo saldo
- Pré-condições: Nenhuma
- Dados de entrada: `saldo_anterior = 500.0, custo = 100.0`
- Passos: Calcular `novo_saldo = saldo_anterior - custo`
- Resultado esperado: `novo_saldo = 400.0`
- Resultado obtido: *(a preencher)*
- Status: *(a preencher)*

**IT-UC12-001**: Sortear com saldo suficiente (HTTP 200)
- Objetivo: Validar sorteio e persistência
- Pré-condições: Jogador com `id=1, saldo=500` existe; PokeAPI está online
- Dados de entrada: `POST /pokemon/gacha/1`
- Passos:
  1. Enviar POST request
  2. Verificar status 200
  3. Validar que `pokemon_api_id` está no response
  4. Consultar BD: verificar novo saldo = 400
  5. Verificar novo registro em `pokemon_time`
- Resultado esperado: HTTP 200; saldo deduzido; pokémon criado
- Resultado obtido: *(a preencher)*
- Status: *(a preencher)*

**IT-UC12-002**: Rejeitar sorteio com saldo insuficiente (HTTP 400)
- Objetivo: Validar validação de saldo
- Pré-condições: Jogador com `id=2, saldo=50` existe
- Dados de entrada: `POST /pokemon/gacha/2`
- Passos:
  1. Enviar POST request
  2. Verificar status 400
- Resultado esperado: HTTP 400 com "Saldo insuficiente"
- Resultado obtido: *(a preencher)*
- Status: *(a preencher)*

**IT-UC12-003**: Falha na PokeAPI (HTTP 503)
- Objetivo: Validar tratamento de erro externo
- Pré-condições: Jogador com `id=1, saldo=500` existe; PokeAPI offline (simulado)
- Dados de entrada: `POST /pokemon/gacha/1` (com PokeAPI mockada para retornar 500)
- Passos:
  1. Enviar POST request
  2. Verificar status 503
- Resultado esperado: HTTP 503 com "Falha de comunicacao com a PokeAPI"
- Resultado obtido: *(a preencher)*
- Status: *(a preencher)*

**E2E-UC12-001**: Sortear pokémon via UI
- Objetivo: Validar fluxo de gacha no navegador
- Pré-condições: Jogador autenticado com saldo 500; página de gacha aberta
- Dados de entrada: Nenhuma
- Passos:
  1. Clicar "Sortear Pokémon"
  2. Aguardar resposta da API
  3. Validar que pokémon sorteado aparece
  4. Validar que saldo foi deduzido
- Resultado esperado: Pokémon sorteado exibido; saldo atualizado
- Resultado obtido: *(a preencher)*
- Status: *(a preencher)*

---

#### UC13–UC18 (Pokémons, Times)

*[Seguir o mesmo padrão para UC13, UC14, UC15, UC16, UC17, UC18]*

---

### **TORNEIO POKÉMON (UC19–UC23)**

#### UC19 — Criar Torneio e Inscrever Time

| Aspecto | Detalhes |
|---------|----------|
| **Testes Unitários** | UT-UC19-001, UT-UC19-002 |
| **Testes de Integração** | IT-UC19-001, IT-UC19-002, IT-UC19-003 |
| **Testes E2E** | E2E-UC19-001 |

**UT-UC19-001**: Validação de tamanho de torneio
- Objetivo: Garantir que tamanho é válido (2, 4 ou 8)
- Pré-condições: Nenhuma
- Dados de entrada: `tamanho = 3` (inválido)
- Passos: Executar validação
- Resultado esperado: Erro ou rejeição
- Resultado obtido: *(a preencher)*
- Status: *(a preencher)*

**UT-UC19-002**: Cálculo de custo por tamanho
- Objetivo: Validar mapeamento de custo
- Pré-condições: `CUSTO_POR_TAMANHO = {2: 500, 4: 700, 8: 1000}`
- Dados de entrada: `tamanho = 4`
- Passos: Buscar custo em dicionário
- Resultado esperado: `custo = 700`
- Resultado obtido: *(a preencher)*
- Status: *(a preencher)*

**IT-UC19-001**: Criar torneio com time válido (HTTP 200)
- Objetivo: Persistir torneio com participantes e partidas
- Pré-condições: Jogador com `id=1, saldo=1000` existe; time com 6 pokémons existe
- Dados de entrada: `POST /torneio/1` com `{"time_id": 1, "tamanho": 4}`
- Passos:
  1. Enviar POST request
  2. Verificar status 200
  3. Validar que torneio foi criado no BD
  4. Validar que saldo = 300 (1000 - 700)
  5. Validar que bots foram criados
  6. Validar que partidas foram criadas (4 na rodada 1, 2 na rodada 2)
- Resultado esperado: Torneio criado; 5 participantes (1 jogador + 3 bots); 6 partidas
- Resultado obtido: *(a preencher)*
- Status: *(a preencher)*

**IT-UC19-002**: Rejeitar se time sem 6 pokémons (HTTP 400)
- Objetivo: Validar requisito de 6 pokémons
- Pré-condições: Jogador com `id=1` existe; time com 3 pokémons
- Dados de entrada: `POST /torneio/1` com `{"time_id": 1, "tamanho": 4}`
- Passos:
  1. Enviar POST request
  2. Verificar status 400
- Resultado esperado: HTTP 400 com "O time precisa ter exatamente 6 Pokemon"
- Resultado obtido: *(a preencher)*
- Status: *(a preencher)*

**IT-UC19-003**: Rejeitar com saldo insuficiente (HTTP 400)
- Objetivo: Validar validação de saldo
- Pré-condições: Jogador com `id=1, saldo=200` existe; time válido com 6 pokémons
- Dados de entrada: `POST /torneio/1` com `{"time_id": 1, "tamanho": 4}` (custo=700)
- Passos:
  1. Enviar POST request
  2. Verificar status 400
- Resultado esperado: HTTP 400 com "Saldo insuficiente para entrar no torneio"
- Resultado obtido: *(a preencher)*
- Status: *(a preencher)*

**E2E-UC19-001**: Criar torneio via UI
- Objetivo: Validar fluxo completo de criação
- Pré-condições: Jogador autenticado; time com 6 pokémons; página de torneio aberta
- Dados de entrada: Tamanho=4
- Passos:
  1. Clicar "Novo Torneio"
  2. Selecionar tamanho
  3. Clicar "Inscrever"
  4. Validar que tela de torneio abre com participantes
- Resultado esperado: Torneio criado; lista de participantes exibida
- Resultado obtido: *(a preencher)*
- Status: *(a preencher)*

---

#### UC20–UC23 (Listar, Obter, Resolver, Deletar Torneios)

*[Seguir o mesmo padrão para UC20, UC21, UC22, UC23]*

---

### **SISTEMA DE AMIGOS (UC24–UC28)**

#### UC24 — Adicionar Amigo (Bilateral)

| Aspecto | Detalhes |
|---------|----------|
| **Testes Unitários** | UT-UC24-001 |
| **Testes de Integração** | IT-UC24-001, IT-UC24-002, IT-UC24-003 |
| **Testes E2E** | E2E-UC24-001 |

**UT-UC24-001**: Validação de amigos diferentes
- Objetivo: Garantir que `jogador_id != amigo_id`
- Pré-condições: Nenhuma
- Dados de entrada: `jogador_id = 1, amigo_id = 1`
- Passos: Executar validação
- Resultado esperado: Erro ou rejeição
- Resultado obtido: *(a preencher)*
- Status: *(a preencher)*

**IT-UC24-001**: Adicionar amigo com sucesso (HTTP 200)
- Objetivo: Criar amizade bilateral
- Pré-condições: Jogadores com `id=1` e `id=2` existem; não são amigos
- Dados de entrada: `POST /amigos/adicionar` com `{"jogador_id": 1, "amigo_id": 2}`
- Passos:
  1. Enviar POST request
  2. Verificar status 200
  3. Consultar BD: verificar 2 entradas em `amizade` (1->2 e 2->1)
- Resultado esperado: HTTP 200; 2 entradas criadas (bilateral)
- Resultado obtido: *(a preencher)*
- Status: *(a preencher)*

**IT-UC24-002**: Rejeitar amigos duplicados (HTTP 400)
- Objetivo: Validar que amigos já existentes não podem ser re-adicionados
- Pré-condições: Amizade 1->2 e 2->1 já existe
- Dados de entrada: `POST /amigos/adicionar` com `{"jogador_id": 1, "amigo_id": 2}`
- Passos:
  1. Enviar POST request
  2. Verificar status 400
- Resultado esperado: HTTP 400 com "Você já é amigo deste jogador"
- Resultado obtido: *(a preencher)*
- Status: *(a preencher)*

**IT-UC24-003**: Rejeitar auto-amizade (HTTP 400)
- Objetivo: Validar que jogador não pode ser amigo de si mesmo
- Pré-condições: Jogador com `id=1` existe
- Dados de entrada: `POST /amigos/adicionar` com `{"jogador_id": 1, "amigo_id": 1}`
- Passos:
  1. Enviar POST request
  2. Verificar status 400
- Resultado esperado: HTTP 400 com "Você não pode se adicionar como amigo"
- Resultado obtido: *(a preencher)*
- Status: *(a preencher)*

**E2E-UC24-001**: Adicionar amigo via UI
- Objetivo: Validar fluxo de adição de amigos
- Pré-condições: Jogador autenticado; página de amigos aberta
- Dados de entrada: Email do amigo = "friend@test.com"
- Passos:
  1. Clicar "Adicionar Amigo"
  2. Digitar email
  3. Clicar "Buscar"
  4. Clicar "Adicionar"
  5. Validar que amigo aparece na lista
- Resultado esperado: Amigo adicionado; aparece em "Meus Amigos"
- Resultado obtido: *(a preencher)*
- Status: *(a preencher)*

---

#### UC25–UC28 (Listar, Favoritar, Remover, Buscar)

*[Seguir o mesmo padrão para UC25, UC26, UC27, UC28]*

---

## Resumo de Cobertura por Nível

### Testes Unitários
- **Total de casos**: ~60+
- **Meta de cobertura**: 80–100%
- **Ferramentas**: PyTest + pytest-cov
- **Locais**: `tests/unit/`

### Testes de Integração
- **Total de casos**: ~70+
- **Meta de cobertura**: 70–90%
- **Ferramentas**: PyTest + TestClient
- **Locais**: `tests/integration/`

### Testes End-to-End
- **Total de casos**: ~28+ (1 por UC)
- **Meta de cobertura**: Fluxos críticos
- **Ferramentas**: Playwright
- **Locais**: `tests/e2e/`

---

## Configuração de SonarQube

### sonar-project.properties

```properties
sonar.projectKey=professor-simulator-clicker
sonar.projectName=Professor Simulator Clicker
sonar.projectVersion=1.0

sonar.sources=app
sonar.tests=tests
sonar.python.coverage.reportPaths=coverage.xml
sonar.python.flake8.reportPath=flake8-report.txt

# Coverage thresholds
sonar.coverage.exclusions=app/main.py,app/database.py
sonar.coverage.lines=70
sonar.coverage.branches=70

# Code quality rules
sonar.python.pylint.reportPath=pylint-report.txt
sonar.python.bandit.reportPath=bandit-report.json
```

### Executar SonarQube

```bash
# 1. Executar testes com coverage
pytest tests/ --cov=app --cov-report=xml --cov-report=html

# 2. Executar análise estática
pylint app --exit-zero > pylint-report.txt 2>&1
flake8 app --format=json > flake8-report.txt 2>&1
bandit -r app -f json > bandit-report.json 2>&1

# 3. Enviar para SonarQube
sonar-scanner
```

---

## Exemplo de Teste Documentado (Código)

### Test Case: IT-UC01-001 (Cadastro com sucesso)

```python
# tests/integration/test_users_it.py
import pytest
from fastapi.testclient import TestClient

@pytest.mark.integration
def test_cadastrar_jogador_sucesso(client: TestClient, db_session):
    """
    IT-UC01-001: Cadastro com sucesso (HTTP 201)
    
    Objetivo: Validar que jogador é criado e persistido
    Pré-condições: Banco de dados vazio; servidor rodando
    Dados de entrada: POST /jogadores/ com dados válidos
    
    Resultado esperado:
    - HTTP 201
    - jogador criado com nome_exibicao default
    - saldo inicial = 0
    - ativo = True
    """
    # Setup
    payload = {
        "nome": "Ana",
        "email": "ana@test.com",
        "senha": "senha123"
    }
    
    # Execução
    response = client.post("/jogadores/", json=payload)
    
    # Validações
    assert response.status_code == 201
    data = response.json()
    assert data["nome"] == "Ana"
    assert data["email"] == "ana@test.com"
    assert data["nome_exibicao"] == "Treinador Iniciante"
    assert data["saldo"] == 0
    
    # Verificar persistência no BD
    jogador = db_session.execute(
        text("SELECT * FROM jogador WHERE email = :email"),
        {"email": "ana@test.com"}
    ).fetchone()
    assert jogador is not None
    assert jogador.nome == "Ana"
```

---

## Cronograma de Implementação

| Semana | Tarefa | Status |
|--------|--------|--------|
| 1 | Implementar testes unitários (UT-UC01 até UT-UC05) | *Pendente* |
| 2 | Implementar testes de integração (IT-UC01 até IT-UC10) | *Pendente* |
| 3 | Implementar testes E2E (E2E-UC01 até E2E-UC10) | *Pendente* |
| 4 | Expandir testes para UC11-UC20 | *Pendente* |
| 5 | Expandir testes para UC21-UC28 | *Pendente* |
| 6 | Configurar SonarQube; gerar relatórios finais | *Pendente* |

---

## Meta Final

✅ **28 Casos de Uso** × **3 Testes em média** = **84+ Casos de Teste**
✅ **Cobertura**: 70–100% de código
✅ **SonarQube**: Sem bloqueadores; máximo 10 code smells

