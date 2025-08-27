# Projeto de Software: Sistema de Gestão Escolar

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white)

Este projeto é uma aplicação web completa para gestão escolar, desenvolvida em Python com o framework Flask. O sistema foi construído seguindo um modelo de desenvolvimento incremental, com foco em uma interface de usuário limpa, padronizada e funcionalidades robustas para todos os perfis de usuário.

## 🚀 Funcionalidades

O sistema é dividido em portais específicos para cada tipo de usuário, com uma experiência de usuário consistente em toda a aplicação.

### 👨‍💼 Portal do Gestor
O gestor tem controle total sobre os dados mestres do sistema.
- **Dashboard Principal:** Visão geral com estatísticas-chave (total de alunos, professores, etc.) e acesso rápido às ferramentas de gerenciamento.
- **Gerenciamento de Usuários:** CRUD completo para todos os tipos de usuários, incluindo a associação de responsáveis aos seus filhos.
- **Gerenciamento de Disciplinas:** CRUD completo de disciplinas, com interface dedicada para associar professores e inscrever alunos.
- **Mural de Avisos:** Ferramenta para criar e publicar avisos gerais que são exibidos nos dashboards de todos os outros usuários.
- **Relatórios e Gráficos:** Página com gráficos visuais para análise de desempenho, como a média de notas por disciplina.

### 👩‍🏫 Portal do Professor
Focado nas ferramentas do dia a dia do corpo docente, com uma interface organizada em colunas para máxima produtividade.
- **Dashboard do Professor:** Exibe as disciplinas que o professor leciona em formato de "cards" interativos e os últimos avisos da gestão.
- **Lançamento de Notas:** Interface para criar avaliações (provas, trabalhos) e lançar as notas dos alunos por disciplina.
- **Registro de Frequência:** Ferramenta para registrar a presença e ausência dos alunos em uma data específica.
- **Planos de Aula:** Ferramenta para criar, listar, editar e remover planos de aula por disciplina.

### 🎓 Portal do Aluno / Responsável
Acesso transparente e dinâmico às informações acadêmicas.
- **Boletim Unificado:** Visualização de notas, frequência e médias por disciplina em "cards" interativos com seções expansíveis.
- **Gráfico de Desempenho (Exclusivo para Responsáveis):** Gráfico de linhas que mostra a evolução das notas do aluno em cada disciplina.
- **Seletor de Filhos (Exclusivo para Responsáveis):** Responsáveis com mais de um filho podem alternar facilmente entre os boletins.
- **Mural de Avisos:** Visualização dos avisos publicados pela gestão.

### ✨ Recursos Gerais do Sistema
- **Interface Padronizada:** Todas as telas, de todos os perfis, seguem um padrão visual consistente, com cabeçalhos, cards e ícones (Bootstrap Icons) para melhorar a usabilidade.
- **Recuperação de Senha:** Fluxo completo de "Esqueceu sua senha" com envio de link seguro por e-mail para redefinição.
- **Página de Perfil:** Qualquer usuário logado pode acessar a página "Meu Perfil" para editar suas próprias informações (nome, e-mail e senha).
- **Login Moderno:** Página de login com layout profissional, imagem de fundo customizável e formulário com campos flutuantes.

---

## 📂 Estrutura do Projeto

/escola_sistema/
|
|-- /static/
|   |-- /css/
|   |   |-- style.css
|   |-- /img/
|       |-- logo.png
|       |-- sala_de_aula_login.jpg
|
|-- /templates/
|   |-- base.html
|   |-- base_login.html
|   |-- login.html
|   |-- esqueci_senha.html
|   |-- redefinir_senha.html
|   |-- index.html
|   |-- usuarios.html
|   |-- editar_usuario.html
|   |-- disciplinas.html
|   |-- detalhes_disciplina.html
|   |-- professor_dashboard.html
|   |-- gerenciar_notas.html
|   |-- registrar_frequencia.html
|   |-- aluno_dashboard.html
|   |-- avisos.html
|   |-- planos_aula.html
|   |-- meu_perfil.html
|   |-- relatorios.html
|
|-- app.py
|-- popular_dados_teste.py
|-- escola.db
|-- README.md

---

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python 3, Flask
- **Banco de Dados:** SQLite 3
- **Frontend:** HTML5, CSS3, JavaScript
- **Framework CSS:** Bootstrap 5
- **Envio de E-mail:** Flask-Mail
- **Gráficos:** Chart.js
- **Motor de Templates:** Jinja2

---

## ⚙️ Como Executar o Projeto

1.  **Pré-requisitos:**
    - Python 3 instalado.
    - `pip` (gerenciador de pacotes do Python).

2.  **Instalação de Dependências:**
    - Navegue até a pasta raiz do projeto (`escola_sistema`).
    - (Opcional, mas recomendado) Crie e ative um ambiente virtual.
    - Instale as dependências executando no terminal:
      ```bash
      pip install Flask Flask-Mail itsdangerous
      ```

3.  **Configuração do Banco de Dados:**
    - Para popular o banco de dados com usuários e dados de teste, execute:
      ```bash
      python popular_dados_teste.py
      ```

4.  **Configuração do E-mail:**
    - Abra o arquivo `app.py`.
    - Na seção de configuração do `Flask-Mail`, insira seu e-mail do Gmail e uma **Senha de App** de 16 dígitos gerada na sua conta Google.

5.  **Iniciando a Aplicação:**
    - Execute o arquivo principal `app.py`:
      ```bash
      python app.py
      ```
    - A aplicação estará rodando em `http://127.0.0.1:5000`.

## 🔑 Credenciais de Teste

- **Gestor:**
  - **Email:** `admin@escola.com` | **Senha:** `admin123`
- **Professor:**
  - **Email:** `maria.silva@escola.com` | **Senha:** `prof123`
- **Aluno:**
  - **Email:** `pedro.oliveira@email.com` | **Senha:** `aluno123`
- **Responsável:**
  - **Email:** `jose.oliveira@email.com` | **Senha:** `resp123` (pai do Pedro)

## 🔮 Próximos Passos Planejados

- **Histórico de Alterações (Log de Auditoria):** Criar um log para registrar ações críticas no sistema (ex: alteração de nota, remoção de usuário).
- **Recursos Avançados:** Implementar um calendário escolar, upload de materiais de aula e um sistema de mensagens diretas.
- **Segurança:** Adicionar criptografia (hashing) para as senhas armazenadas no banco de dados.
