# Test Cases (In Progress)

This document tracks the initial test coverage for Sprint 2. Status is updated as tests are implemented.

## Unit Tests

| ID | Area | Scenario | Expected | Status | Test File |
| --- | --- | --- | --- | --- | --- |
| UT-001 | schemas | JogadorCreate accepts valid email | Model builds successfully | Done | tests/unit/test_schemas.py |
| UT-002 | schemas | JogadorCreate rejects invalid email | ValidationError raised | Done | tests/unit/test_schemas.py |
| UT-003 | schemas | ItemCreate sets defaults | raridade="comum" and vendivel=True | Done | tests/unit/test_schemas.py |
| UT-004 | users | Cadastro persiste dados e nome_exibicao default | Jogador criado com default | Done | tests/unit/users/test_cadastro.py |
| UT-005 | users | Cadastro com email duplicado | 400 with duplicate email | Done | tests/unit/users/test_cadastro.py |
| UT-006 | game | Dar aula sem itens | ganho base de 10.0 | Done | tests/unit/game/test_dar_aula.py |
| UT-007 | game | Dar aula soma multiplicadores | ganho base + soma itens | Done | tests/unit/game/test_dar_aula.py |

## Integration Tests

| ID | Area | Scenario | Expected | Status | Test File |
| --- | --- | --- | --- | --- | --- |
| IT-001 | users | Update display name (valid) | 200 and name updated | Done | tests/test_users.py |
| IT-002 | users | Update display name (invalid chars) | 400 with validation error | Done | tests/test_users.py |
| IT-003 | game | Dar aula with no items | ganho=10.0 and saldo updated | Done | tests/test_game.py |
| IT-004 | inventory | Comprar item without saldo | 400 with "Saldo insuficiente" | Done | tests/test_inventory.py |
| IT-005 | users | Login with valid credentials | 200 and token returned | Planned | tests/test_users.py |
| IT-006 | shop | Admin price update | 200 and preco updated | Planned | tests/test_shop.py |

## Data Flow Tests

| ID | Area | Scenario | Expected | Status | Test File |
| --- | --- | --- | --- | --- | --- |
| DF-001 | users | Cadastro e consulta do jogador | GET retorna dados persistidos | Done | tests/integration/flows/test_cadastro_flow.py |
| DF-002 | game | Dar aula atualiza saldo e transacao | saldo e transacao consistentes | Done | tests/integration/flows/test_dar_aula_flow.py |
