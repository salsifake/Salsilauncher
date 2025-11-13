# Roadmap do Salsilauncher
	
## Fase 1 — Estrutura Inicial (Concluída)
- [x] Criar backend FastAPI básico
- [x] Criar frontend React com Vite
- [x] Criar comunicação frontend → backend
- [x] Estruturar rotas iniciais e layout básico
- [x] Implementar endpoint GET /games com dados estáticos
- [x] Configurar ambiente de desenvolvimento

## Observações:
### Jogo.id é int 
- Isso causa implicações na geração de ID quando há concorrência. considere UUID string para unicidade robusta
### CORS Middleware: 
- não exponha allow_origins=["*"]. Use variável de ambiente para controlar allowed origins. Também verifique se midia_launcher existe (criar pasta se necessário) e evite servir diretórios sensíveis. Sugestão:
```
from starlette.responses import JSONResponse
# validar existencia da pasta no startup
if not os.path.exists("midia_launcher"):
    os.makedirs("midia_launcher", exist_ok=True)
```
### Funções de persistência `(salvar_jogos, carregar_jogos, salvar_colecoes, carregar_colecoes)`: 
- Escrita direta com open(DB_FILE, "w") não é atômica. Em caso de concorrência ou crash, JSON pode corromper.
- **Falta de locking**: dois requests simultâneos (POST/PUT) podem sobrescrever ou perder dados.
- `carregar_jogos()` silencia `JSONDecodeError` retornando `[]`, podendo ocultar corrupções
- Correções:
    - Usar gravação atômica com `tempfile` + `os.replace()` para evitar arquivos parcialmente gravados
    - Usar `portalocker`ou `filelock` para lock de arquivo durante leitura/escrita se for manter JSON
    - Logar e propagar `JSONDecodeError`. EX: mover `jogos_db.json` para `jogos_db.json.broken.timestamp` e alertar

    ou só migrar tudo para **SQLite**.

### `Get /jogos`
- Ao retortar `resultados_ordenados`, o código retorna objetos `Jogo`. Porém, a busca por tags faz `tags.lower()` sem tratar strings vazias. Funciona, mas atenção à normalização.
    - A solução seria normalizar tags - `strip()`, permitir busca em outros campos (genero, tags)
, paginar resultados (limit/offset)

### `/scan` **(POST)**
- Uso de `os.listdir(caminho)` sem validação: se caminho não existir ou for grande, pode lançar `PermissionError` ou travar.
- Ao gerar `novo_id = max([j.id for j in jogos_atuais], default=0) + 1` tem risco de **race condition** se duas varreduras/creations ocorrerem simultaneamente.
- `os.walk` percorre recursivamente, porém você adiciona uma entrada `Jogo(...)` com poucos campos (apenas id, nome, caminhos). Pode faltar metadados.
- Recomendações:
    - Validar caminho recebido (existência e permissões)
    - Tratar exceções durante listagem (try/except).
    - Para ID seguro: use uuid.uuid4() ou uma função atômica (se usar DB, usar autoincrement do DB)
    - Possível otimização: aceitar max_depth ou filtros

Trecho sugerido para validação:
```
if not os.path.exists(caminho) or not os.path.isdir(caminho):
    raise HTTPException(status_code=400, detail="Caminho inválido")
```

### `/jogos/{id}/capa` — upload imagem e conversão para webp
- Usa Image.open(file.file) diretamente sem validar content_type ou tamanho do arquivo.
- Salva arquivo no caminho midia_launcher/{jogo_id}_capa.webp sem checar se midia_launcher existe ou manipular nomes conflitantes.
- Não fecha/consome o upload de forma segura (mas FastAPI faz o gerenciamento).
- Possível path traversal? Não aqui porque você controla o path.

- Recomendações:
    - Verificar file.content_type e limitar tipos:
        ```
        if not (file.content_type and file.content_type.startswith("image/")):
        raise HTTPException(400, "Arquivo não é imagem")
        ```
    - Ler bytes e validar com `Image.open(io.BytesIO(bytes_data))` e `Image.verify()` antes de salvar.

    - Gerar nomes por hash/uuid para evitar sobrescrever imagens de outros IDs (se desejar versões múltiplas).

    - Tratar tamanhos máximos (por ex. 5MB) para evitar ataques de upload.

### CRUD (`GET /jogos/{id}` `PoST /jogos` `PUT` `DELETE`)
- `POST /jogos`: recebe `Jogo` completo e sobrescreve `id` com novo novo_id. **Problema**: cliente pode enviar campos que não deveriam (ex.: `tempo_jogado_segundos` manipulado).
    - Melhoria: criar schemas separados: `JogoCreate` (sem id, sem campos controlados) e `JogoRead` (com id). Use Pydantic para validação e defaults.

- `PUT /jogos/{id}`: substitui totalmente o objeto. Isso é aceitável, mas considere `PATCH` para atualizações parciais.

- `DELETE /jogos/{id}`: retorna `None` com status 204 — ok. Mas remova assets relacionados (imagens) ao deletar — opcional

### `GET /tags` e `GET /jogos/aleatorio`
- `GET /tags` precisa normalizar
- `GET /jogos/aleatorio`: usa `random.sample` sem checar `len(jogos)` quando `num_aleatorios` é 0. `num_aleatorios = min(5, len(jogos))`, random.sample(jogos, 0) returns [] okay. Entretanto, `random.sample` dá erro se k > len — but you guard it.

## Plano de melhorias pré-fase 2

### Prioridade alta
- [ ] Gravação atômica + file lock nas funções salvar_jogos/salvar_colecoes.
- [ ] Validação robusta de uploads (content_type, tamanho, Image.verify, salvar por hash).
- [ ] Criar schemas separados JogoCreate, JogoUpdate, JogoRead para evitar clients definirem campos proibidos.
- [ ] ID generation seguro: migrar para UUID ou controlar geração dentro de DB. Se continuar com ints, usar DB autoincrement.
- [ ] Adicionar logging (uso do logging), e tratamento de exceções globais.
- [ ] Implementar banco de dados SQLite

### Prioridade Média
- [ ] Validar e sanitizar entrada do /scan (caminho com existência/permissões).
- [ ] Remover/limpar assets no DELETE (apagar capa webp e outros arquivos órfãos).
- [ ] Adicionar paginação em GET /jogos (query params limit e offset ou page).
- [ ] CORS configurável via variável de ambiente.

### Prioridade Baixa
- [ ] Migrar persistência para SQLite + SQLModel (boa relação custo/benefício).
- [ ] Adicionar testes unitários (pytest) cobrindo CRUD, upload, scan.
- [ ] Adicionar CI (GitHub Actions) rodando lint + testes.

## Fase 2 — Fundação do Sistema de Jogos (Em andamento)
- [ ] Criar modelos persistentes de jogos
- [ ] Criar CRUD completo (adicionar, editar, remover jogos)
- [ ] Implementar API para upload de imagens de jogos
- [ ] Criar modal para adicionar jogos manualmente
- [ ] Implementar carregamento e tratamento de erros no frontend

## Fase 3 — Biblioteca e Organização
- [ ] Criar layout completo da biblioteca
- [ ] Criar página individual por jogo
- [ ] Criar sistema de busca
- [ ] Criar filtros (por gênero, categoria, tempo jogado, favoritos)
- [ ] Criar categorias personalizadas
- [ ] Implementar ordenação por mais jogados, recentes etc.
- [ ] Paginação e filtros no endpoint `GET /jogos`

## Fase 4 — Sistema de Execução de Jogos
### A
- [ ] Implementar execução direta de jogos no Windows

### B
- [ ] Implementar contagem de horas jogadas
- [ ] Criar sistema que roda em segundo plano para monitorar jogo aberto
- [ ] Registrar estatísticas no banco de dados

## Fase 5 — Sistema de Download de Jogos (Principal)
- [ ] Criar integração com fonte externa de downloads
- [ ] Mapear jogos do fórum e baixar imagens, descrições e metadados
- [ ] Implementar downloader com barra de progresso
- [ ] Gerenciar múltiplos downloads simultâneos
- [ ] Verificar integridade dos arquivos baixados

## Fase 6 — Recursos Avançados
- [ ] Criar sistema de savestates
- [ ] Criar integração com fórum (comentários, posts, notas)
- [ ] Criar sistema de avaliações dos jogos
- [ ] Criar seção de jogos recomendados

## Fase 7 — UI/UX Completa
- [ ] Criar tema visual definitivo
- [ ] Criar tema claro/escuro
- [ ] Criar animações e transições
- [ ] Criar mecanismo de responsive design
- [ ] Criar ícone, splash screen e identidade visual

## Fase 8 — Transformação do Launcher em Aplicativo Desktop
- [ ] Integrar o Salsilauncher com Electron
- [ ] Criar comunicação backend local → Electron
- [ ] Empacotar versão desktop para Windows
- [ ] Criar sistema de auto-update
- [ ] Criar modos portáteis e instaláveis

## Fase 9 — Infraestrutura e Qualidade
- [ ] Criar testes automáticos (backend e frontend)
- [ ] Criar documentação em /docs
- [ ] Criar pipeline de build
- [ ] Criar sistema de logs
- [ ] Otimizar performance geral

## Fase 10 — Futuro e Expansões
- [ ] Suporte a outras plataformas além de Windows
- [ ] Integração com outros launchers
- [ ] Plugin system para extensões
