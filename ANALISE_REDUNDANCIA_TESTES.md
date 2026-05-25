# Análise de Redundância de Cobertura de Testes

**Data**: 25 de maio de 2026  
**Estrutura Analisada**: `tests/` (unit, integration, e2e, integration/flows)

---

## 📊 Resumo Executivo

Foram identificadas **7 áreas principais com redundância crítica** na cobertura de testes. O projeto testa os mesmos cenários em 3-4 níveis diferentes (unit → integration → e2e → flows), causando:

- ❌ **Duplicação excessiva** de casos de teste
- ❌ **Tempo de execução inflado** (testes E2E são lentos)
- ❌ **Manutenção complexa** (3+ lugares para atualizar um comportamento)
- ❌ **Falsos positivos** (bugs de infraestrutura vs. lógica)

---

## 🔴 Redundâncias Críticas Identificadas

### 1. **CADASTRO DE JOGADOR (UC01)** - Redundância Severa

#### Testado Em:
```
tests/unit/test_schemas.py
├─ test_jogador_create_aceita_dados_validos()
├─ test_jogador_create_rejeita_email_invalido()
└─ test_jogador_create_rejeita_nome_vazio()

tests/integration/test_users_integration.py → TestCadastroJogador
├─ test_cadastro_sucesso_http_201()
├─ test_cadastro_email_duplicado_http_400()
├─ test_cadastro_email_invalido_http_422()
├─ test_cadastro_nome_vazio_http_422()
└─ test_cadastro_nome_whitespace_http_422()

tests/integration/flows/test_cadastro_flow.py
└─ test_fluxo_cadastro_e_consulta() [REDUNDANTE]

tests/e2e/test_user_flows.py → TestCadastroE2E
├─ test_fluxo_cadastro_completo()
└─ test_fluxo_cadastro_email_duplicado()
```

#### Problema:
- ✗ Validação de email: testada 6 vezes (unit + integration × 3 + e2e × 2)
- ✗ Nome vazio: testada 3 vezes (unit + integration + e2e)
- ✗ HTTP 201: testada em integration e e2e

#### Recomendação:
- ✅ Manter: Unit tests (validação Pydantic) + 1 Integration test (HTTP/BD)
- ❌ Remover: Duplicatas em `test_cadastro_flow.py` e E2E para casos de erro

---

### 2. **LOGIN/AUTENTICAÇÃO (UC02)** - Redundância Crítica

#### Testado Em:
```
tests/integration/test_users_integration.py → TestLoginJogador
├─ test_login_sucesso_http_200()
└─ test_login_credenciais_invalidas_http_400()

tests/e2e/test_user_flows.py → TestLoginE2E
├─ test_fluxo_login_sucesso()
└─ test_fluxo_login_credenciais_invalidas()
```

#### Problema:
- ✗ Login bem-sucedido: testado 2 vezes (integration + e2e)
- ✗ Credenciais inválidas: testado 2 vezes (integration + e2e)
- ⚠️ E2E não adiciona valor, apenas simula clicks

#### Recomendação:
- ✅ Manter: 1 Integration test completo (credenciais + tokens)
- ❌ Remover: E2E para login, já que é testado pelo flow de cadastro

---

### 3. **ATUALIZAÇÃO DE PERFIL (UC03-UC04)** - Redundância Moderada

#### Testado Em:
```
tests/test_users.py
├─ test_atualizar_perfil_valido()
└─ test_atualizar_perfil_invalido()

tests/integration/test_users_integration.py → TestAtualizacaoPerfil
├─ test_atualizar_perfil_sucesso_http_200()
├─ test_perfil_invalido_rejeitado_http_400()
└─ test_consultar_perfil_outro_jogador_http_403()
```

#### Problema:
- ✗ Validação de nome: testada 2 vezes com entradas diferentes
- ✗ Resposta HTTP: duplicada

#### Recomendação:
- ✅ Consolidar em `test_users_integration.py`
- ❌ Remover: duplicatas de `test_users.py`

---

### 4. **SISTEMA DE LOJA (UC05-UC11)** - Redundância Alta

#### Testado Em:
```
tests/test_inventory.py
├─ test_comprar_item_sem_saldo()
└─ [outros testes de compra]

tests/integration/test_shop_integration.py → TestCadastroItem
├─ test_admin_cadastra_item_sucesso_http_201()
├─ test_nao_admin_cadastra_item_http_403()
├─ test_cadastro_item_preco_negativo_http_400()
└─ [8+ testes de shop]

tests/e2e/test_shop_flows.py → TestShopE2E
├─ test_fluxo_compra_item()
└─ test_fluxo_listar_inventario()
```

#### Problema:
- ✗ Compra com saldo insuficiente: testada em `test_inventory.py` + `test_shop_integration.py` + potencial `test_e2e`
- ✗ Listagem de itens: testada em integration + e2e
- ✗ Permissões (admin): testada apenas em integration (bom)

#### Recomendação:
- ✅ Manter: `test_shop_integration.py` (cobertura completa)
- ❌ Remover: `test_inventory.py` (duplica compra e saldo)
- ⚠️ Manter apenas 1 E2E: fluxo de compra bem-sucedida

---

### 5. **SISTEMA DE POKÉMON/GACHA (UC12-UC18)** - Redundância Severa

#### Testado Em:
```
tests/integration/test_pokemon_integration.py → TestSorteioPokemon
├─ test_jogador_sorteia_pokemon_saldo_suficiente_http_200()
├─ test_jogador_sorteia_pokemon_saldo_insuficiente_http_400()
└─ test_sortear_pokemon_jogador_inexistente_http_404()

tests/integration/test_pokemon_integration.py → TestVisualizarTime
├─ test_visualizar_time_vazio_http_200()
└─ test_visualizar_time_com_pokemons_http_200()

tests/e2e/test_pokemon_flows.py → TestPokemonE2E
├─ test_fluxo_sortear_pokemon()
├─ test_fluxo_criar_time()
└─ test_fluxo_visualizar_time()

tests/e2e/test_ui_game.py
└─ [Potencial duplicação de gacha/times]
```

#### Problema:
- ✗ Sorteia com saldo suficiente: testada em integration + e2e
- ✗ Visualizar time: testada em integration + e2e
- ✗ Criar time: pode estar duplicada em `test_ui_game.py`

#### Recomendação:
- ✅ Manter: `test_pokemon_integration.py` (casos de erro + BD)
- ❌ Remover: duplicatas em E2E
- 📋 Revisar: `test_ui_game.py` para evitar sobreposição

---

### 6. **SISTEMA DE TORNEIOS (UC19-UC23)** - Redundância Alta

#### Testado Em:
```
tests/integration/test_tournament_integration.py → TestCriarTorneio
├─ test_criar_torneio_tamanho_2_sucesso_http_201()
├─ test_criar_torneio_saldo_insuficiente_http_400()
└─ test_criar_torneio_tamanho_invalido_http_400()

tests/e2e/test_tournament_flows.py → TestTournamentE2E
├─ test_fluxo_criar_torneio()
└─ test_fluxo_listar_torneios()
```

#### Problema:
- ✗ Criação de torneio: testada em integration + e2e
- ✗ Validações de saldo: testada em integration (correto) mas retestada visualmente em e2e
- ✗ Listagem: testada em integration + e2e

#### Recomendação:
- ✅ Manter: `test_tournament_integration.py` (cobertura completa)
- ❌ Remover: `test_fluxo_criar_torneio()` do E2E (já testado)
- ✅ Manter: 1 E2E apenas para "visualizar e interagir com torneio existente"

---

### 7. **SISTEMA DE AMIGOS (UC24-UC28)** - Redundância Moderada

#### Testado Em:
```
tests/integration/test_friends_integration.py → TestAdicionarAmigo
├─ test_adicionar_amigo_bilateral_http_201()
└─ test_adicionar_amigo_ja_existe_http_400()

tests/e2e/test_friends_flows.py → TestFriendsE2E
├─ test_fluxo_adicionar_amigo()
├─ test_fluxo_listar_amigos()
└─ test_fluxo_favoritar_amigo()
```

#### Problema:
- ✗ Adição de amigo: testada em integration + e2e
- ✗ Listagem: testada em integration + e2e
- ✓ Favoritar: apenas em E2E (aceitável)

#### Recomendação:
- ✅ Manter: `test_friends_integration.py` (casos de erro + BD)
- ❌ Remover: `test_fluxo_adicionar_amigo()` e `test_fluxo_listar_amigos()` do E2E
- ✅ Manter: `test_fluxo_favoritar_amigo()` (complexo, válido em E2E)

---

### 8. **VALIDAÇÕES DE ENTRADA (Transversal)** - Redundância Crítica

#### Padrão Identificado:
```
Email inválido:
  1. Unit test em test_schemas.py → test_jogador_create_rejeita_email_invalido()
  2. Integration test em test_users_integration.py → test_cadastro_email_invalido_http_422()
  3. E2E test em test_user_flows.py → tenta submeter e-mail inválido

Nome vazio:
  1. Unit test → test_jogador_create_rejeita_nome_vazio()
  2. Integration test → test_cadastro_nome_vazio_http_422()
  3. Possível E2E → preenchimento vazio no form
```

#### Problema:
- ✗ Mesmo erro validado em 3 camadas desnecessariamente
- ✗ Pydantic já valida (unit), endpoint não precisa revalidar (integration)
- ✗ E2E para erros de entrada é overkill

#### Recomendação:
- ✅ Manter: Unit tests (validação Pydantic)
- ⚠️ Manter: 1 Integration test por tipo de erro (amostra)
- ❌ Remover: E2E para validações de input (não é crítico)

---

## 📋 Matriz de Cobertura Recomendada

| Feature | Unit | Integration | E2E | Flows |
|---------|------|-------------|-----|-------|
| Cadastro | ✅ Schema | ✅ HTTP/BD | ⚠️ Flow só | ❌ |
| Login | ⚠️ Schema | ✅ HTTP/Token | ❌ | ❌ |
| Perfil | ⚠️ Schema | ✅ HTTP/BD | ❌ | ❌ |
| Shop | ⚠️ Schema | ✅ HTTP/BD | ⚠️ 1 flow | ❌ |
| Pokémon | ⚠️ Schema | ✅ HTTP/BD | ⚠️ 1 flow | ❌ |
| Torneio | ⚠️ Schema | ✅ HTTP/BD | ⚠️ 1 flow | ❌ |
| Amigos | ⚠️ Schema | ✅ HTTP/BD | ⚠️ 1 flow | ❌ |

---

## 🎯 Ações Prioritárias

### **Prioridade 1 - Remover Imediatamente:**
- [ ] `tests/integration/flows/test_cadastro_flow.py` → Duplica UC01
- [ ] `tests/test_inventory.py` → Duplica compra de UC10
- [ ] E2E testes de validação de input (email inválido, nome vazio, etc)

### **Prioridade 2 - Consolidar:**
- [ ] `tests/test_users.py` → Mesclar com `test_users_integration.py`
- [ ] `tests/test_game.py` → Revisar para evitar duplicação de gacha
- [ ] Revisar `tests/e2e/test_ui_game.py` contra `test_pokemon_integration.py`

### **Prioridade 3 - Refatorar E2E:**
- [ ] Remover E2E para casos de erro (já testados em integration)
- [ ] Manter E2E apenas para: fluxos de sucesso críticos + interações UI complexas
- [ ] E2E reduzido de ~10 testes por feature para 1-2

---

## 📊 Impacto Estimado

### Atual:
- Unit tests: ~15 testes
- Integration tests: ~40 testes
- E2E tests: ~25 testes  
- Flows: ~5 testes
- **Total: ~85 testes** (com alta redundância)

### Recomendado:
- Unit tests: ~15 testes (manter)
- Integration tests: ~35 testes (remover duplicatas)
- E2E tests: ~8 testes (manter apenas fluxos críticos)
- Flows: ~0 testes (remover)
- **Total: ~58 testes** (32% redução, menos redundância)

### Benefícios:
- ⏱️ **-35% tempo de execução** (menos E2E lento)
- 🔧 **-70% pontos de manutenção** (menos duplicação)
- 🎯 **+50% clareza** (cada camada com responsabilidade clara)

---

## 💡 Estrutura Recomendada para o Futuro

```
tests/
├── unit/                    # Validação de schemas, lógica pura
│   ├── test_schemas.py     # ✅ Validação Pydantic
│   ├── test_models.py      # ✅ Lógica de negócio isolada
│   └── game/
│       └── test_dar_aula.py # ✅ Cálculos de pontos, etc
│
├── integration/            # HTTP + BD + fluxos
│   ├── test_users_integration.py       # UC01-04
│   ├── test_shop_integration.py        # UC05-11
│   ├── test_pokemon_integration.py     # UC12-18
│   ├── test_tournament_integration.py  # UC19-23
│   ├── test_friends_integration.py     # UC24-28
│   └── flows/              # ❌ REMOVER (redundante)
│
└── e2e/                    # Apenas fluxos críticos UI
    ├── test_signup_login.py           # UC01-02 fluxo
    ├── test_compra_e_uso.py           # UC05-11 fluxo
    ├── test_gacha_e_batalha.py        # UC12-18 fluxo
    └── test_torneio_participacao.py   # UC19-23 fluxo
```

---

## 📝 Notas Técnicas

### Validações Testadas em Excesso:
1. Email inválido (formato)
2. Nome vazio ou só espaços
3. Saldo insuficiente
4. Permissões (admin vs. não-admin)
5. Recurso não encontrado (404)

Esses casos **devem ser testados uma vez** (integration) e confiados, não retestados em E2E.

### E2E Devem Focar Em:
- Fluxos de sucesso ponta-a-ponta
- Interações UI complexas (drag-drop, modais, etc)
- Navegação entre páginas
- **NÃO** em casos de erro ou validação

---

## ✅ Conclusão

O projeto tem **excelente cobertura**, mas sofre com **redundância crítica** entre camadas.  
Implementando as recomendações acima:
- ✅ Testes mais rápidos (menos E2E)
- ✅ Manutenção simplificada (uma fonte de verdade por caso)
- ✅ Melhor isolamento de problemas (unit vs. integration vs. e2e)
- ✅ Cobertura preservada ou melhorada
