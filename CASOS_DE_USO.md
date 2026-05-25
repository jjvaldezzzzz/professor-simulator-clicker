# Casos de Uso — Professor Simulator Clicker 
Este documento reúne os casos de uso principais do sistema. Cada caso de uso segue um padrão consistente: Ator, Pré-condições, Fluxo Principal, Fluxos Alternativos e Pós-condições.

## Sumário 

- Perfil do Usuário (UC01–UC04)
- Loja e Inventário (UC05–UC11)
- Times Pokémon (UC12–UC18)
- Torneio Pokémon (UC19–UC23)
- Sistema de Amigos (UC24–UC28)

---

## **UC01 — Cadastrar Jogador**
- **Ator**: Usuário (novo jogador)
- **Pré-condições**: Não existe conta com o mesmo email.
- **Fluxo principal**:
  1. Usuário envia `nome`, `email` e `senha` via `POST /jogadores/`.
  2. Sistema valida unicidade do email e campos obrigatórios.
  3. Sistema cria o registro e retorna dados do jogador.
- **Fluxos alternativos**:
  - A1: Email já cadastrado → retorna erro 400.
  - A2: Dados inválidos (nome vazio, email inválido) → retorna erro 400.
- **Pós-condições**: Conta criada; jogador ativo no sistema.

## **UC02 — Autenticar Jogador**
- **Ator**: Jogador
- **Pré-condições**: Conta existente e ativa.
- **Fluxo principal**:
  1. Jogador envia `email` e `senha` via `POST /jogadores/login`.
  2. Sistema valida credenciais e atualiza `ultimo_login`.
  3. Sistema retorna token simulado, `jogador_id` e `is_admin`.
- **Fluxos alternativos**:
  - A1: Credenciais inválidas → erro 401.
  - A2: Conta inativa → erro 404/401 conforme implementação.
- **Pós-condições**: Sessão autenticada; token para ações subsequentes.

## **UC03 — Atualizar Perfil (Nome de Exibição)**
- **Ator**: Jogador autenticado
- **Pré-condições**: Jogador existe e está ativo.
- **Fluxo principal**:
  1. Jogador envia novo `nome_exibicao` via `PUT /jogadores/{id}/perfil`.
  2. Sistema valida formato e tamanho (<=50, caracteres permitidos).
  3. Sistema atualiza e retorna confirmação.
- **Fluxos alternativos**:
  - A1: Nome inválido → erro 400.
  - A2: Jogador não encontrado → erro 404.
- **Pós-condições**: `nome_exibicao` atualizado.

## **UC04 — Deletar Conta**
- **Ator**: Jogador autenticado
- **Pré-condições**: Jogador existe; não é admin.
- **Fluxo principal**:
  1. Jogador solicita exclusão via `DELETE /jogadores/{id}`.
  2. Sistema verifica privilégios e apaga o registro.
  3. Retorna confirmação.
- **Fluxos alternativos**:
  - A1: Jogador não encontrado → erro 404.
  - A2: Conta é admin → erro 403.
- **Pós-condições**: Conta removida.

---

## **UC05 — Cadastrar Novo Item (Admin)**
- **Ator**: Admin/Professor
- **Pré-condições**: Usuário autenticado como admin.
- **Fluxo principal**:
  1. Admin envia dados do item via `POST /loja/itens`.
  2. Sistema valida permissão e cria item.
  3. Registra transação administrativa e retorna item criado.
- **Fluxos alternativos**:
  - A1: Usuário não é admin → erro 403.
  - A2: Dados inválidos → erro 400.
- **Pós-condições**: Item disponível na loja.

## **UC06 — Visualizar Catálogo da Loja**
- **Ator**: Qualquer jogador (ou anônimo)
- **Pré-condições**: Existem itens ativos.
- **Fluxo principal**:
  1. Cliente solicita listagem via `GET /loja/itens`.
  2. Sistema retorna itens ativos ordenados por preço.
- **Fluxos alternativos**:
  - A1: Nenhum item ativo → lista vazia.
- **Pós-condições**: Catálogo exibido.

## **UC07 — Atualizar Item (Admin)**
- **Ator**: Admin
- **Pré-condições**: Admin autenticado; item existe e ativo.
- **Fluxo principal**:
  1. Admin envia campos a alterar via `PUT /loja/itens/{item_id}`.
  2. Sistema valida alterações e atualiza.
  3. Registra transação e retorna item atualizado.
- **Fluxos alternativos**:
  - A1: Sem alterações enviadas → erro 400.
  - A2: Não é admin → erro 403.
  - A3: Item não encontrado → erro 404.
- **Pós-condições**: Item atualizado no catálogo.

## **UC08 — Alterar Preço do Item (Admin)**
- **Ator**: Admin
- **Pré-condições**: Admin autenticado; item existe.
- **Fluxo principal**:
  1. Admin envia novo preço via `PUT /loja/itens/{item_id}/preco`.
  2. Sistema valida `novo_preco > 0` e atualiza.
  3. Retorna item com novo preço.
- **Fluxos alternativos**:
  - A1: Preço inválido → erro 400.
  - A2: Item não encontrado → erro 404.
- **Pós-condições**: Preço atualizado.

## **UC09 — Deletar Item da Loja (Admin)**
- **Ator**: Admin
- **Pré-condições**: Admin autenticado; item existe e ativo.
- **Fluxo principal**:
  1. Admin solicita remoção via `DELETE /loja/itens/{item_id}`.
  2. Sistema marca item `ativo = FALSE` e remove inventário relacionado.
  3. Registra transação e confirma remoção.
- **Fluxos alternativos**:
  - A1: Item não encontrado → erro 404.
  - A2: Não é admin → erro 403.
- **Pós-condições**: Item inativo e não aparece no catálogo.

## **UC10 — Comprar Item da Loja**
- **Ator**: Jogador
- **Pré-condições**: Jogador autenticado; item ativo; saldo suficiente.
- **Fluxo principal**:
  1. Jogador solicita compra via `POST /inventario/comprar/{jogador_id}/{item_id}`.
  2. Sistema verifica saldo e item; deduz saldo; insere no inventário; registra transação.
  3. Retorna confirmação.
- **Fluxos alternativos**:
  - A1: Jogador ou item não encontrado → erro 404.
  - A2: Saldo insuficiente → erro 400.
  - A3: Já possui o item ou erro de BD → rollback e erro 400.
- **Pós-condições**: Item vinculado ao inventário; saldo reduzido.

## **UC11 — Listar Itens do Inventário**
- **Ator**: Jogador
- **Pré-condições**: Jogador autenticado.
- **Fluxo principal**:
  1. Jogador solicita inventário via `GET /inventario/{jogador_id}`.
  2. Sistema retorna itens adquiridos (ativos) com detalhes.
- **Fluxos alternativos**:
  - A1: Jogador inexistente → erro 404.
- **Pós-condições**: Inventário exibido.

---

## **UC12 — Sortear Pokémon (Gacha)**
- **Ator**: Jogador
- **Pré-condições**: Jogador existe; saldo >= `CUSTO_GACHA`.
- **Fluxo principal**:
  1. Jogador chama `POST /pokemon/gacha/{jogador_id}`.
  2. Sistema chama PokeAPI para obter Pokémon.
  3. Deduz saldo, insere em `pokemon_time` e registra transação.
  4. Retorna detalhes do Pokémon sorteado.
- **Fluxos alternativos**:
  - A1: Saldo insuficiente → erro 400.
  - A2: Falha PokeAPI → erro 503.
  - A3: Erro de persistência → rollback e erro 500.
- **Pós-condições**: Novo Pokémon associado ao jogador.

## **UC13 — Visualizar Pokémons do Jogador**
- **Ator**: Jogador
- **Pré-condições**: Jogador existe.
- **Fluxo principal**:
  1. Cliente solicita via `GET /pokemon/{jogador_id}`.
  2. Sistema retorna pokémons ativos do jogador.
- **Fluxos alternativos**:
  - A1: Jogador não encontrado → lista vazia ou 404.
- **Pós-condições**: Lista retornada.

## **UC14 — Criar Time Pokémon**
- **Ator**: Jogador
- **Pré-condições**: Nome do time válido; jogador existe.
- **Fluxo principal**:
  1. Jogador envia `nome` via `POST /pokemon/times/{jogador_id}`.
  2. Sistema valida e cria time.
  3. Retorna `id` e `nome` do time.
- **Fluxos alternativos**:
  - A1: Nome inválido → erro 400.
  - A2: Time duplicado → erro 400.
- **Pós-condições**: Time criado.

## **UC15 — Renomear Time**
- **Ator**: Jogador
- **Pré-condições**: Time existe e pertence ao jogador; novo nome válido.
- **Fluxo principal**:
  1. Jogador envia novo nome via `PUT /pokemon/times/{jogador_id}/{time_id}`.
  2. Sistema valida e atualiza.
  3. Retorna novo nome.
- **Fluxos alternativos**:
  - A1: Time não encontrado → erro 404.
  - A2: Nome duplicado → erro 400.
- **Pós-condições**: Nome atualizado.

## **UC16 — Deletar Time**
- **Ator**: Jogador
- **Pré-condições**: Time existe e pertence ao jogador.
- **Fluxo principal**:
  1. Jogador solicita deleção via `DELETE /pokemon/times/{jogador_id}/{time_id}`.
  2. Sistema desvincula pokémons (`time_id = NULL`) e remove o time.
  3. Retorna confirmação.
- **Fluxos alternativos**:
  - A1: Time não encontrado → erro 404.
- **Pós-condições**: Time removido.

## **UC17 — Adicionar Pokémon ao Time**
- **Ator**: Jogador
- **Pré-condições**: Time existe; Pokémon pertence ao jogador; time não cheio (<=6).
- **Fluxo principal**:
  1. Jogador envia `pokemon_id` via `POST /pokemon/times/{jogador_id}/{time_id}/adicionar`.
  2. Sistema verifica limites e vincula o Pokémon.
  3. Retorna confirmação.
- **Fluxos alternativos**:
  - A1: Pokémon não encontrado → erro 404.
  - A2: Time cheio → erro 400.
  - A3: Pokémon já no time → mensagem informativa.
- **Pós-condições**: Pokémon faz parte do time.

## **UC18 — Libertar Pokémon**
- **Ator**: Jogador
- **Pré-condições**: Pokémon existe e pertence ao jogador.
- **Fluxo principal**:
  1. Jogador solicita via `DELETE /pokemon/libertar/{jogador_id}/{pokemon_id}`.
  2. Sistema remove registro do Pokémon.
  3. Retorna confirmação.
- **Fluxos alternativos**:
  - A1: Pokémon não encontrado → erro 404.
- **Pós-condições**: Pokémon removido.

---

## **UC19 — Criar Torneio e Inscrever Time**
- **Ator**: Jogador
- **Pré-condições**: Jogador autenticado; saldo suficiente; time com exatamente 6 pokémons.
- **Fluxo principal**:
  1. Jogador envia `time_id` e `tamanho` via `POST /torneio/{jogador_id}`.
  2. Sistema valida tamanho, saldo e time; deduz custo.
  3. Cria torneio, registra participante do jogador e bots; busca dados na PokeAPI para calcular BST; cria partidas.
  4. Retorna detalhes do torneio.
- **Fluxos alternativos**:
  - A1: Saldo insuficiente → erro 400.
  - A2: Time inválido → erro 404/400.
  - A3: Falha PokeAPI → rollback e erro 503.
- **Pós-condições**: Torneio criado e em andamento.

## **UC20 — Listar Torneios do Jogador**
- **Ator**: Jogador
- **Pré-condições**: Jogador autenticado.
- **Fluxo principal**:
  1. Jogador solicita via `GET /torneio/{jogador_id}`.
  2. Sistema retorna torneios do jogador com resumo.
- **Fluxos alternativos**:
  - A1: Nenhum torneio → lista vazia.
- **Pós-condições**: Lista apresentada.

## **UC21 — Obter Detalhes de um Torneio**
- **Ator**: Jogador (criador)
- **Pré-condições**: Torneio existe e pertence ao jogador.
- **Fluxo principal**:
  1. Jogador solicita via `GET /torneio/{jogador_id}/{torneio_id}`.
  2. Sistema monta e retorna participantes, pokémons e partidas.
- **Fluxos alternativos**:
  - A1: Torneio não encontrado → erro 404.
- **Pós-condições**: Detalhes retornados.

## **UC22 — Resolver Partida do Torneio**
- **Ator**: Jogador (criador)
- **Pré-condições**: Partida existe e não foi resolvida; torneio em andamento.
- **Fluxo principal**:
  1. Jogador chama `POST /torneio/{torneio_id}/partidas/{partida_id}/resolver`.
  2. Sistema compara `total_bst` dos participantes (ou sorteia em empate), marca vencedor e avança vencedor para próxima rodada ou finaliza o torneio.
  3. Se finalizado e jogador venceu, sistema credita prêmio e registra transação.
  4. Retorna resultado da resolução.
- **Fluxos alternativos**:
  - A1: Partida já resolvida → erro 400.
  - A2: Partida não pronta → erro 400.
  - A3: Torneio já finalizado → erro 400.
- **Pós-condições**: Partida resolvida; torneio atualizado.

## **UC23 — Deletar Torneio**
- **Ator**: Jogador (criador)
- **Pré-condições**: Torneio finalizado.
- **Fluxo principal**:
  1. Jogador solicita deleção via `DELETE /torneio/{torneio_id}`.
  2. Sistema verifica status e remove torneio.
  3. Retorna confirmação.
- **Fluxos alternativos**:
  - A1: Torneio não finalizado → erro 400.
  - A2: Torneio não encontrado → erro 404.
- **Pós-condições**: Torneio removido.

---

## **UC24 — Adicionar Amigo (Bilateral)**
- **Ator**: Jogador
- **Pré-condições**: Ambos os jogadores existem e ativos; não existe amizade ativa; `jogador_id != amigo_id`.
- **Fluxo principal**:
  1. Jogador envia `jogador_id` e `amigo_id` via `POST /amigos/adicionar`.
  2. Sistema valida e insere amizade bilateral (A→B e B→A).
  3. Retorna registros criados.
- **Fluxos alternativos**:
  - A1: Jogador == amigo → erro 400.
  - A2: Já são amigos → erro 400.
  - A3: Jogador não encontrado → erro 404.
- **Pós-condições**: Amizade registrada bilateralmente.

## **UC25 — Obter Lista de Amigos**
- **Ator**: Jogador
- **Pré-condições**: Jogador existe.
- **Fluxo principal**:
  1. Jogador solicita via `GET /amigos/{jogador_id}`.
  2. Sistema retorna amigos ordenados por favorito e data.
- **Fluxos alternativos**:
  - A1: Jogador não encontrado → erro 404.
  - A2: Sem amigos → total 0 e lista vazia.
- **Pós-condições**: Lista entregue.

## **UC26 — Marcar / Remover Favorito**
- **Ator**: Jogador
- **Pré-condições**: Amizade existe e pertence ao jogador.
- **Fluxo principal**:
  1. Jogador chama `PUT /amigos/{amizade_id}/favoritar` ou `/desfavoritar` com `jogador_id`.
  2. Sistema valida e atualiza o campo `favorito`.
  3. Retorna confirmação.
- **Fluxos alternativos**:
  - A1: Amizade não encontrada → erro 404.
- **Pós-condições**: Flag `favorito` atualizada.

## **UC27 — Remover Amigo (Soft Delete)**
- **Ator**: Jogador
- **Pré-condições**: Amizade existe e pertence ao jogador.
- **Fluxo principal**:
  1. Jogador solicita remoção via `DELETE /amigos/{amizade_id}` com `jogador_id`.
  2. Sistema marca `ativo = FALSE` para a entrada solicitada.
  3. Retorna confirmação.
- **Fluxos alternativos**:
  - A1: Amizade não encontrada → erro 404.
- **Pós-condições**: Entrada de amizade marcada como inativa.

## **UC28 — Buscar Jogador por Email (para amizade)**
- **Ator**: Jogador
- **Pré-condições**: Email válido.
- **Fluxo principal**:
  1. Jogador chama `POST /amigos/buscar?email=...`.
  2. Sistema valida formato e busca por email.
  3. Retorna resultados.
- **Fluxos alternativos**:
  - A1: Email inválido → erro 400.
  - A2: Nenhum jogador encontrado → erro 404.
- **Pós-condições**: Lista de candidatos retornada.

---

### Observações finais
- Os casos de uso acima se baseiam na implementação atual e nas validações explícitas presentes nos routers e schemas.
- Se desejar, posso:
  - Gerar uma versão em PDF;
  - Criar uma versão em tabela ou CSV;
  - Adicionar links diretos para rotas e linhas nos arquivos.

Arquivo gerado: `CASOS_DE_USO.md` no diretório raiz do projeto.
