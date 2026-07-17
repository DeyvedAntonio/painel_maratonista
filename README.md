# 🎬 Painel Maratonista

> **Uma plataforma interativa para gerenciar mídias assistidas, visualizar estatísticas de consumo e simular maratonas personalizadas.**

Este projeto foi desenvolvido utilizando a metodologia ágil **Scrum** (dividido em 3 Sprints) como um desafio prático para dominar o ecossistema **Streamlit**, manipulação de estados globais (`st.session_state`), navegação multipáginas nativa e análise de dados com **Pandas**.

---

## 🚀 O Problema que o Projeto Resolve

Quem consome muitos filmes e séries frequentemente se depara com dois problemas:
1. **Falta de centralização de registros:** É difícil manter um histórico limpo, rápido e visual do que já foi assistido e das respectivas avaliações pessoais sem recorrer a planilhas complexas ou aplicativos pesados.
2. **Ansiedade da maratona:** Ao iniciar uma nova série, é difícil estimar de forma realista em quantos dias ela será concluída com base no tempo real que a pessoa tem disponível para assistir diariamente.

O **Painel Maratonista** resolve isso ao centralizar o cadastro em uma interface amigável de múltiplas páginas, consolidando estatísticas visuais instantâneas e oferecendo um **Simulador de Maratona** preditivo e livre de falhas de divisão por zero.

---

## 🛠️ Tecnologias e Conceitos Utilizados

*   **Python 3.x**
*   **Streamlit** (Navegação dinâmica com `st.navigation` e `st.Page`, controle de estado com `st.session_state`, agrupamento com `st.form`)
*   **Pandas** (Tratamento, renomeação e agregação de dados)
*   **Metodologia Ágil (Scrum)** (Planejamento de Sprints, refinamento de requisitos baseado em usabilidade)

---

## ✨ Funcionalidades Desenvolvidas

O aplicativo é estruturado em três áreas principais de forma modular:

### 1. 📝 Cadastro de Produções
*   Formulário inteligente que previne recarregamentos indesejados da página a cada entrada do usuário (`st.form`).
*   Entradas ricas como controle deslizante de notas com estrelas do Material Design (`st.select_slider`) e validações de campos obrigatórios.

### 2. 📊 Dashboard Analítico
*   **Métricas de Alto Nível:** Cards dinâmicos exibindo o total de produções assistidas e o tempo total acumulado em minutos.
*   **Gráfico de Distribuição:** Gráfico interativo que agrupa e exibe as produções assistidas por categoria.
*   **Tabela de Histórico:** Tabela dinâmica que exibe os dados salvos em memória (`st.session_state`), com colunas renomeadas e tratamento para evitar erros visuais caso nenhum dado tenha sido cadastrado ainda.

### 3. ⏱️ Simulador de Maratona
*   Ferramenta preditiva que calcula o tempo total de uma nova série (Episódios × Duração) e estima com precisão quantos dias o usuário levará para concluí-la com base em sua disponibilidade diária real de minutos, blindado contra erros de divisão por zero.

---

## 📁 Estrutura de Arquivos do Projeto

```text
painel-maratonista/
│
├── app.py              # Arquivo principal de inicialização e navegação global
├── pyproject.toml      # Configuração do projeto e declaração de dependências modernas
├── README.md           # Documentação técnica
└── pages/              # Módulos das subpáginas do Streamlit
    ├── cadastro.py     # Página do formulário de cadastro
    ├── painel.py       # Página do Dashboard com gráficos e métricas
    └── simulador.py    # Página do simulador de maratonas
```

---

## ⚙️ Como Executar o Projeto Localmente
Siga o passo a passo abaixo para rodar o projeto na sua máquina:

### 1. Clonar o repositório
```Bash
git clone https://github.com/seu-usuario/painel_maratonista.git
cd painel-maratonista
```

### 2. Criar e ativar um ambiente virtual (Recomendado)
```Bash
# No Linux/macOS
python3 -m venv venv
source venv/bin/activate

# No Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar as dependências do projeto
Como as dependências do projeto estão declaradas no moderno padrão pyproject.toml, você pode instalá-las usando o gerenciador de pacotes do Python:
```Bash
pip install .
```

### 4. Executar o aplicativo Streamlit
```Bash
streamlit run app.py
```

---

## 🧠 Aprendizados e Evolução Técnica (Foco em Recrutadores)
Durante o desenvolvimento deste projeto, foram superados desafios comuns de arquitetura no Streamlit:

- Persistência de Dados Sem Banco: Compreensão profunda do ciclo de vida do Streamlit. Uso do st.session_state para garantir que os dados sobrevivam à transição de páginas e interações de botões.

- Design Clean e UX: Implementação de navegação superior, organização de dados com st.columns, tratamento amigável de estados vazios (evitando telas de erro) e validação de erros lógicos (Edge Cases).

- Flexibilidade Ágil: Pivoteamento de escopo durante a Sprint 3 ao perceber que a modelagem de dados original não favorecia uma média automática de datas, decidindo por um input de tempo disponível do usuário muito mais simples e eficaz.

---

## 🤝 Contato & Conexão

Estou em busca de novas oportunidades e desafios técnicos onde eu possa aplicar boas práticas de engenharia de software, metodologias ágeis e desenvolvimento focado em dados!

Se você gostou deste projeto e quer conversar sobre desenvolvimento, boas práticas de arquitetura ou oportunidades de carreira:

*   **💼 Conecte-se comigo no LinkedIn:** [Deyved Antonio](https://linkedin.com/in/deyvdantonio)
*   **✉️ Envie um E-mail:** [deyved.antonio@gmail.com](mailto:deyved.antonio@gmail.com)
*   **🐙 Conheça meus outros projetos:** [github.com/DeyvedAntonio](https://github.com/DeyvedAntonio)

*Adoraria receber feedbacks, sugestões de melhorias ou bater um papo sobre tecnologia!* 🚀

