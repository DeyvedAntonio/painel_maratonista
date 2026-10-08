# 🎬 Painel Maratonista

> **Uma plataforma interativa para gerenciar mídias assistidas, visualizar estatísticas de consumo e simular maratonas personalizadas.**

Este projeto foi desenvolvido utilizando a metodologia ágil **Scrum** (dividido em 3 Sprints) como um desafio prático para dominar o ecossistema **Streamlit**, manipulação de estados globais (`st.session_state`), navegação multipáginas nativa e análise de dados com **Pandas**. Agora com **persistência em SQLite**, **dashboard analítico avançado**, **multi-perfil**, **integração TMDb** e **gamificação**.

---

## 🚀 O Problema que o Projeto Resolve

Quem consome muitos filmes e séries frequentemente se depara com dois problemas:
1. **Falta de centralização de registros:** É difícil manter um histórico limpo, rápido e visual do que já foi assistido e das respectivas avaliações pessoais sem recorrer a planilhas complexas ou aplicativos pesados.
2. **Ansiedade da maratona:** Ao iniciar uma nova série, é difícil estimar de forma realista em quantos dias ela será concluída com base no tempo real que a pessoa tem disponível para assistir diariamente.

O **Painel Maratonista** resolve isso ao centralizar o cadastro em uma interface amigável de múltiplas páginas, consolidando estatísticas visuais instantâneas e oferecendo um **Simulador de Maratona** preditivo e livre de falhas de divisão por zero.

---

## 🛠️ Tecnologias e Conceitos Utilizados

*   **Python 3.10+** (tipagem estrita, dataclasses, pattern matching)
*   **Streamlit** (Navegação dinâmica com `st.navigation`/`st.Page`, controle de estado com `st.session_state`, agrupamento com `st.form`, edição inline com `st.data_editor`, tabs/expander)
*   **Pandas** (Tratamento, renomeação e agregação de dados)
*   **SQLite** (Persistência local leve, zero-config, índices otimizados, migrações versionadas)
*   **TMDb API** (The Movie Database - autocomplete e metadados automáticos com cache LRU)
*   **Docker** (Containerização multi-stage, non-root user, healthcheck)
*   **GitHub Actions** (CI/CD: lint (ruff), format (black), type-check (mypy), test (pytest), build docker)
*   **Pydantic + Pydantic-Settings** (Validação de config, settings management)
*   **Clean Architecture** (Domain → Data → Services → Presentation)
*   **Repository Pattern** (Abstração de persistência, testabilidade)
*   **Dependency Injection** (ServiceContainer, ciclo de vida gerenciado)
*   **Domain-Driven Design** (Entidades ricas, Value Objects, regras de negócio encapsuladas)
*   **Metodologia Ágil (Scrum)** (Planejamento de Sprints, refinamento contínuo)

---

## ✨ Funcionalidades Desenvolvidas

O aplicativo é estruturado em **4 áreas principais** de forma modular:

### 1. 📝 Cadastro de Produções (com TMDb)
*   Formulário inteligente que previne recarregamentos indesejados (`st.form`).
*   **Tipos:** Filme vs Série (campos adaptativos: temporadas/episódios para séries).
*   **Campos ricos:** Temporadas, episódios assistidos/total, status (Assistido/Assistindo/Pretendo/Abandonado), data de visualização.
*   **Busca TMDb integrada:** Autocomplete com pôster, sinopse, gênero, duração, nota — preenchimento automático do formulário.
*   Categorias expandidas (10 opções) e nota com slider de estrelas (Material Design).
*   Persistência automática em SQLite com isolamento por perfil.

### 2. 📊 Dashboard Analítico Avançado
*   **Métricas de Alto Nível:** Total de produções, tempo total, média de avaliação, diversidade de tipos.
*   **Gráficos Interativos (4 abas):**
    *   📈 Distribuição por Categoria
    *   🎬 Comparativo Filme vs Série (quantidade e minutos)
    *   📅 Timeline mensal (últimos 12 meses)
    *   🏆 Rankings: Top 5 mais longas e Top 5 melhor avaliadas
*   **Filtros Dinâmicos:** Por tipo, categoria, status e nota mínima.
*   **Edição Inline:** `st.data_editor` com validação por coluna (SelectboxColumn, NumberColumn, DateColumn).
*   **Exclusão Segura:** Confirmação obrigatória antes de deletar.
*   **Exportação:** CSV, JSON e Excel (com `openpyxl`).

### 3. 👥 Multi-Perfil (Sidebar)
*   Troca de perfil instantânea na sidebar (dados isolados por perfil).
*   Criação/exclusão de perfis com emoji personalizado.
*   Perfil padrão protegido (não pode ser excluído).

### 4. 🏅 Gamificação (Badges/Conquistas)
*   **9 badges únicos** com critérios automáticos:
    *   👶 Primeiros Passos (1ª produção)
    *   🏃 Maratonista (10+ produções)
    *   🎭 Crítico (5+ notas máximas)
    *   🍿 Binge Watcher (50+ episódios)
    *   🎬 Cinéfila (20+ filmes)
    *   📺 Viciado em Séries (10+ séries)
    *   🌈 Explorador de Gêneros (5+ categorias)
    *   ⏰ Senhor do Tempo (5000+ minutos)
    *   ✅ Completionista (10+ séries completas)
*   Notificação visual (balões) ao desbloquear.
*   Painel de progresso para próximas conquistas.

### 5. ⏱️ Simulador de Maratona
*   Ferramenta preditiva que calcula o tempo total de uma nova série (Episódios × Duração) e estima com precisão quantos dias o usuário levará para concluí-la com base em sua disponibilidade diária real de minutos.
*   Validações robustas (min/max, step=1, proteção contra divisão por zero).

---

## 📁 Estrutura de Arquivos do Projeto (Clean Architecture)

```text
painel-maratonista/
│
├── app.py                              # Entry point (delega para src/painel_maratonista/app.py)
├── pyproject.toml                      # Config moderna + deps [dev, export]
├── .env.example                        # Template variáveis de ambiente (TMDB_API_KEY)
├── Dockerfile                          # Multi-stage, non-root, healthcheck
├── docker-compose.yml                  # Orquestração (prod + dev hot-reload)
├── README.md                           # Documentação técnica
├── maratonista.db                      # Banco SQLite (criado automaticamente)
├── .github/workflows/ci.yml            # CI/CD: ruff, black, mypy, pytest, docker build
└── src/
    └── painel_maratonista/             # Pacote principal
        ├── __init__.py
        ├── app.py                      # Main app: DI container, navegação, session_state
        ├── config.py                   # Pydantic Settings (env, validação)
        ├── domain/                     # 🎯 Camada de Domínio (regras de negócio puras)
        │   ├── __init__.py
        │   ├── enums.py                # MediaType, MediaStatus, MediaCategory, BadgeKey
        │   ├── value_objects.py        # Rating(1-5), Duration, EpisodeCount, SeasonCount, WatchedDate
        │   └── entities.py             # Profile, Production, Badge, Stats (com validação e métodos)
        ├── data/                       # 💾 Camada de Dados (Repository Pattern)
        │   ├── __init__.py
        │   ├── database.py             # Conexão SQLite + Schema + Migrações
        │   └── repositories/           # Um por agregado
        │       ├── __init__.py
        │       ├── profile_repo.py     # CRUD perfis
        │       ├── production_repo.py  # CRUD produções + Stats SQL otimizadas
        │       └── badge_repo.py       # CRUD badges
        ├── services/                   # ⚙️ Camada de Serviços (Use Cases)
        │   ├── __init__.py             # ProfileService, ProductionService, BadgeService, ServiceContainer (DI)
        │   └── tmdb_service.py         # Cliente TMDb (busca, metadados, cache LRU, degradação graciosa)
        ├── exceptions/                 # 🛡️ Tratamento de Erros Tipado
        │   ├── __init__.py             # DomainError, ValidationError, NotFoundError, BusinessRuleError, etc.
        │   └── handlers.py             # Integração Streamlit (st.error, st.warning, st.success)
        └── presentation/               # 🎨 Camada de Apresentação (Streamlit)
            ├── __init__.py
            ├── components/             # Componentes reutilizáveis (UI kit)
            │   └── __init__.py         # forms, tables, charts, badges, export, profile selector
            ├── pages/                  # Páginas (Thin Controllers - só orquestram)
            │   ├── home.py             # Home + seletor de perfil + gerenciamento
            │   ├── cadastro.py         # Formulário + busca TMDb
            │   ├── painel.py           # Dashboard: métricas, gráficos, filtros, editor, export, badges
            │   └── simulador.py        # Simulador de maratona
            └── navigation.py           # Configuração st.navigation (top-level)
```

---

## ⚙️ Como Executar o Projeto Localmente

### 1. Clonar o repositório
```bash
git clone https://github.com/seu-usuario/painel_maratonista.git
cd painel-maratonista
```

### 2. Criar e ativar um ambiente virtual (Recomendado)
```bash
# No Linux/macOS
python3 -m venv venv
source venv/bin/activate

# No Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar as dependências do projeto
```bash
# Dependências base (inclui pydantic, requests, python-dotenv)
pip install -e .

# Para desenvolvimento completo (lint, test, format, types)
pip install -e .[dev]

# Para exportação Excel
pip install -e .[export]
```

### 4. Configurar variáveis de ambiente (opcional - para TMDb)
```bash
cp .env.example .env
# Edite .env e adicione sua TMDB_API_KEY (obtenha em https://www.themoviedb.org/settings/api)
```

### 5. Executar o aplicativo Streamlit
```bash
# Opção 1: Entry point direto
streamlit run app.py

# Opção 2: Módulo Python (equivalente)
python -m src.painel_maratonista.app
```

---

## 🐳 Deploy com Docker

O projeto usa **multi-stage build** para imagem otimizada e **non-root user** para segurança.

### Build e execução local
```bash
# Build da imagem
docker build -t painel-maratonista .

# Executar (porta 8501)
docker run -p 8501:8501 \
  -v $(pwd)/maratonista.db:/app/maratonista.db \
  -v $(pwd)/.env:/app/.env:ro \
  painel-maratonista
```

### Com docker-compose (recomendado)
```bash
# Produção (porta 8501)
docker-compose up -d

# Desenvolvimento com hot-reload (porta 8502)
docker-compose --profile dev up dev
```

### Dockerfile Highlights
- **Base**: `python:3.11-slim` (menor superfície de ataque)
- **Dependency cache**: `poetry` + cache de layers
- **Non-root user**: `app` user com home directory
- **Healthcheck**: `curl /_stcore/health` a cada 30s
- **Headless mode**: Configurado via ENV

---

## 🧪 Qualidade de Código (CI/CD)

O pipeline GitHub Actions (`.github/workflows/ci.yml`) executa em cada push/PR na branch `main` ou `develop`:

| Etapa | Ferramenta | Comando | Descrição |
|-------|------------|---------|-----------|
| **Lint** | Ruff | `ruff check src/` | Linting rápido, substitui flake8+isort |
| **Formatação** | Black | `black --check src/` | Formatação consistente |
| **Tipagem** | MyPy | `mypy src/` | Verificação de tipos estática |
| **Testes** | Pytest | `pytest -v` | Unit + Integration tests |
| **Build** | Docker | `docker build` | Multi-stage, push para registry |

### Executar localmente
```bash
# Instalar deps de dev
pip install -e .[dev]

# Lint
ruff check src/

# Formatar
black src/

# Type check
mypy src/

# Testes
pytest -v

# Coverage
pytest --cov=src/painel_maratonista --cov-report=term-missing
```

### Configuração de Qualidade (pyproject.toml)
```toml
[tool.ruff]
line-length = 100
target-version = "py310"
select = ["E", "F", "I", "UP", "B", "C4", "W", "T20"]

[tool.black]
line-length = 100
target-version = ["py310"]

[tool.mypy]
python_version = "3.10"
warn_return_any = true
disallow_untyped_defs = false
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --tb=short --strict-markers"
```

---

## 🏛️ Arquitetura: Clean Architecture + DDD

Este projeto foi refatorado para seguir **Clean Architecture** com **Domain-Driven Design**, separando responsabilidades em camadas independentes:

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION                             │
│  Streamlit Pages (Thin Controllers) + Reusable Components   │
└──────────────────────────┬──────────────────────────────────┘
                           │ Depende de (Interfaces)
┌──────────────────────────▼──────────────────────────────────┐
│                      SERVICES                               │
│  Use Cases / Business Logic (ProfileService, etc.)          │
│  Orquestra repositórios, aplica regras, emite eventos       │
└──────────────────────────┬──────────────────────────────────┘
                           │ Depende de (Interfaces)
┌──────────────────────────▼──────────────────────────────────┐
│                       DATA                                  │
│  Repository Implementations (SQLite, TMDb HTTP)             │
│  Implementa interfaces definidas no Domain                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                       DOMAIN                                │
│  Entities, Value Objects, Enums, Repository Interfaces      │
│  ZERO dependências externas - puro Python                   │
└─────────────────────────────────────────────────────────────┘
```

### Benefícios Alcançados

| Característica | Antes (Flat) | Depois (Clean) |
|----------------|--------------|----------------|
| **Testabilidade** | ❌ UI acoplada ao DB | ✅ Repositories mockáveis |
| **Troca de DB** | ❌ Impossível | ✅ Implementar nova interface |
| **Validação** | ❌ Espalhada | ✅ Centralizada em Value Objects/Entities |
| **Type Safety** | ❌ `dict` solto | ✅ Dataclasses + Pydantic |
| **Reutilização** | ❌ Copy-paste | ✅ Services independentes de UI |
| **Onboarding** | ❌ Difícil | ✅ Camadas claras, responsabilidades únicas |

### Camadas em Detalhes

#### 🎯 Domain (`src/painel_maratonista/domain/`)
- **Enums**: `MediaType`, `MediaStatus`, `MediaCategory`, `BadgeKey` — type-safe, extensíveis
- **Value Objects**: `Rating(1-5)`, `Duration`, `EpisodeCount`, `SeasonCount`, `WatchedDate` — imutáveis, auto-validáveis
- **Entities**: `Profile`, `Production`, `Badge`, `Stats` — regras de negócio encapsuladas (`is_completed`, `progress_percentage`, `estimated_days_to_complete`)
- **Repository Interfaces**: Protocols (`Protocol`) para inversão de dependência

#### 💾 Data (`src/painel_maratonista/data/`)
- **Database**: Conexão SQLite com context manager, PRAGMA foreign_keys, schema versionado
- **Repositories**: `SQLiteProfileRepository`, `SQLiteProductionRepository`, `SQLiteBadgeRepository` — SQL otimizado com índices
- **Migrações**: Schema versionado em `SCHEMA` constant

#### ⚙️ Services (`src/painel_maratonista/services/`)
- **ProfileService**: CRUD perfis + regras (perfil padrão protegido)
- **ProductionService**: CRUD produções + integração automática com BadgeService
- **BadgeService**: Verificação de condições + concessão automática (9 badges configuráveis)
- **TMDBService**: Cliente HTTP com cache LRU, degradação graciosa sem API key, mapeamento gêneros
- **ServiceContainer**: DI container simples (lazy singleton, ciclo de vida gerenciado)

#### 🎨 Presentation (`src/painel_maratonista/presentation/`)
- **Components**: UI kit reutilizável (forms, tables, charts, badges, export, profile selector)
- **Pages**: Thin controllers — só obtêm serviços do `st.session_state` e delegam para components
- **Navigation**: `st.navigation` configurado centralmente

#### 🛡️ Exceptions (`src/painel_maratonista/exceptions/`)
- Hierarquia tipada: `DomainError` → `ValidationError`, `NotFoundError`, `ConflictError`, `BusinessRuleError`, `ExternalServiceError`, `DatabaseError`
- Handlers Streamlit: convertem exceções em `st.error/st.warning/st.success` apropriados

---

## 🧠 Aprendizados e Evolução Técnica (Foco em Recrutadores)

Durante o desenvolvimento deste projeto, foram superados desafios comuns de arquitetura no Streamlit e evoluído para **Clean Architecture**:

- **Clean Architecture Real:** Separação clara em 4 camadas (Domain, Data, Services, Presentation) com inversão de dependência via Repository Pattern e interfaces `Protocol`.
- **Domain-Driven Design:** Entidades ricas (`Production.is_completed`, `progress_percentage`, `estimated_days_to_complete`), Value Objects imutáveis auto-validáveis (`Rating`, `Duration`, `WatchedDate`), Enums type-safe.
- **Repository Pattern:** `SQLiteProductionRepository` implementa interface `ProductionRepository` — permite trocar SQLite por PostgreSQL/Redis sem tocar em Services.
- **Dependency Injection:** `ServiceContainer` gerencia ciclo de vida (lazy singletons), facilita testes com mocks.
- **Persistência Robusta:** SQLite com schema versionado, índices otimizados, foreign keys, migrações embutidas, transações ACID.
- **Type Safety Total:** Dataclasses `slots=True`, Pydantic Settings, MyPy strict mode, zero `dict` solto.
- **Error Handling Estruturado:** Hierarquia de exceções customizadas (`DomainError` → `ValidationError`, `BusinessRuleError`, etc.) com handlers Streamlit dedicados.
- **Integração Externa Resiliente:** `TMDBService` com cache LRU (`functools.lru_cache`), timeout configurável, degradação graciosa sem API key, mapeamento de gêneros.
- **Multi-Tenancy Leve:** Isolamento por `profile_id` em todas as queries, troca de contexto via sidebar, perfil padrão protegido.
- **Gamificação Orientada a Dados:** `BadgeService` verifica condições via Stats agregadas (SQL otimizado), concede automaticamente, 9 badges configuráveis via `Settings.badge_thresholds`.
- **Containerização Profissional:** Dockerfile multi-stage, non-root user, healthcheck, headless mode, docker-compose dev/prod com hot-reload.
- **CI/CD Completo:** GitHub Actions com ruff, black, mypy, pytest, docker build, cache de dependências.
- **Componentização Streamlit:** UI kit reutilizável (`render_production_form`, `render_production_editor`, `render_badges`, etc.) — páginas viram thin controllers.
- **Flexibilidade Ágil:** Refatoração incremental (Strangler Fig), preservando funcionalidades enquanto moderniza arquitetura.

---

## 🗺️ Roadmap Futuro (Ideias para Próximas Sprints)

- [ ] **Recomendações Inteligentes:** Content-based filtering usando categorias/avaliações + TMDb.
- [ ] **Autenticação Real:** OAuth (Google/GitHub) + JWT para multi-usuário real.
- [ ] **Streaks & Calendário:** Heatmap estilo GitHub de dias assistidos.
- [ ] **Compartilhamento:** Exportar/importar perfil, link público read-only.
- [ ] **Notificações:** Lembrete diário, nova temporada de séries acompanhadas.
- [ ] **PWA / Mobile:** Service worker, manifest, otimização touch.
- [ ] **Testes E2E:** Playwright para fluxos críticos (cadastro, edição, badges).
- [ ] **Observabilidade:** Logs estruturados (structlog), métricas (Prometheus), tracing.

---

## 🤝 Contato & Conexão

Estou em busca de novas oportunidades e desafios técnicos onde eu possa aplicar boas práticas de engenharia de software, metodologias ágeis e desenvolvimento focado em dados!

Se você gostou deste projeto e quer conversar sobre desenvolvimento, boas práticas de arquitetura ou oportunidades de carreira:

*   **💼 Conecte-se comigo no LinkedIn:** [Deyved Antonio](https://linkedin.com/in/deyvdantonio)
*   **✉️ Envie um E-mail:** [deyved.antonio@gmail.com](mailto:deyved.antonio@gmail.com)
*   **🐙 Conheça meus outros projetos:** [github.com/DeyvedAntonio](https://github.com/DeyvedAntonio)

*Adoraria receber feedbacks, sugestões de melhorias ou bater um papo sobre tecnologia!* 🚀