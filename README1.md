# Projeto de Software: Sistema de Gestão Escolar

Este projeto é uma aplicação web completa para gestão escolar, desenvolvida em Python com o framework Flask. O sistema foi construído seguindo um modelo de desenvolvimento incremental, com foco em boas práticas de Engenharia de Software.

## 🚀 Funcionalidades

O sistema é dividido em três portais principais, cada um com funcionalidades específicas baseadas no tipo de usuário.

### 👨‍💼 Portal do Gestor
O gestor tem controle total sobre os dados mestres do sistema.
- **Dashboard Principal:** Visão geral com acesso rápido às ferramentas de gerenciamento.
- **Gerenciamento de Usuários:**
    - Cadastro de novos usuários (gestores, professores, alunos, responsáveis).
    - Validação de formato de email (`@` e `.`) e verificação de duplicidade.
    - Edição e remoção de usuários existentes.
- **Gerenciamento de Turmas:**
    - Cadastro, edição e remoção de turmas.
    - Interface dedicada para associar/desassociar professores e matricular/desmatricular alunos em cada turma.
- **Mural de Avisos:**
    - Ferramenta para criar e publicar avisos gerais que serão exibidos nos dashboards de todos os outros usuários.

### 👩‍🏫 Portal do Professor
Focado nas ferramentas do dia a dia do corpo docente.
- **Dashboard do Professor:** Exibe as turmas que o professor leciona e os últimos avisos da gestão.
- **Lançamento de Notas:** Interface para criar avaliações (provas, trabalhos) e lançar as notas dos alunos por turma.
- **Registro de Frequência:** Ferramenta para registrar a presença e ausência dos alunos em uma data específica.
- **Organizador de Planos de Aula:**
    - Ferramenta para criar, listar, editar e remover planos de aula por turma, ajudando na organização pedagógica.

### 🎓 Portal do Aluno / Responsável
Acesso transparente às informações acadêmicas.
- **Boletim Unificado:** Visualização clara das notas lançadas pelos professores em cada avaliação.
- **Histórico de Frequência:** Acesso ao registro de presenças e faltas.
- **Mural de Avisos:** Visualização dos avisos publicados pela gestão.

### ✨ Melhorias de Design e Experiência do Usuário
- **Identidade Visual:** O sistema agora suporta uma logo personalizada na barra de navegação e tem uma página de login com imagem de fundo customizável.
- **Interface Moderna:** Foram adicionados ícones (Bootstrap Icons) em toda a aplicação para melhorar a usabilidade e a navegação visual.
- **Notificações "Toast":** O sistema de feedback ao usuário foi atualizado para usar "toasts", notificações elegantes que aparecem no canto da tela e desaparecem automaticamente.


## 📂 Estrutura do Projeto

A organização dos arquivos segue o padrão recomendado para aplicações Flask, separando a lógica, os templates e os arquivos estáticos.


/escola_sistema/
|
|-- /static/                # Arquivos estáticos (CSS, JS, Imagens )
|   |-- /css/
|       |-- style.css       # Nossa folha de estilos personalizada
|
|-- /templates/                     # Arquivos HTML com templates Jinja2
|   |-- base.html                   # Template base com a estrutura principal
|   |-- login.html                  # Página de login
|   |-- index.html                  # Dashboard do Gestor
|   |-- usuarios.html               # Página de gerenciamento de usuários
|   |-- editar_usuario.html         # Página para editar um usuário
|   |-- turmas.html                 # Página de gerenciamento de turmas
|   |-- detalhes_turma.html         # Página de detalhes de uma turma
|   |-- professor_dashboard.html    # Dashboard do Professor
|   |-- gerenciar_notas.html        # Página para lançar notas
|   |-- registrar_frequencia.html   # Página para registrar frequência
|   |-- aluno_dashboard.html        # Dashboard do Aluno (Boletim)
|   |-- avisos.html                 # Página do gestor para gerenciar avisos.
|   |-- planos_aula.html            # Página do professor para gerenciar planos de aula.

|
|-- app.py                  # Arquivo principal da aplicação Flask (rotas e lógica)
|-- database.py             # Script para inicializar o banco de dados
|-- schema.sql              # Arquivo com os comandos SQL para criar as tabelas
|-- escola.db               # Arquivo do banco de dados SQLite (gerado automaticamente)
|-- README.md               # Este arquivo de documentação


---

## Estrutura do Banco de Dados (`schema.sql`)

O banco de dados é composto pelas seguintes tabelas:

- **usuario:** Armazena os dados de todos os usuários (gestores, professores, alunos, etc.).
- **turma:** Armazena as informações das turmas.
- **leciona:** Tabela de associação que define qual professor leciona em qual turma.
- **matricula:** Tabela de associação que define qual aluno está matriculado em qual turma.
- **avaliacao:** Armazena as avaliações criadas pelos professores para uma turma.
- **nota:** Armazena a nota de um aluno em uma avaliação específica.
- **frequencia:** Armazena o registro de presença/falta de um aluno em uma data específica.


## 🛠️ Tecnologias Utilizadas

- **Backend:** Python 3
- **Framework Web:** Flask
- **Banco de Dados:** SQLite 3
- **Frontend:** HTML5, CSS3
- **Framework CSS:** Bootstrap 5
- **Biblioteca de Ícones:** Bootstrap Icons
- **Motor de Templates:** Jinja2

## ⚙️ Como Executar o Projeto

1.  **Pré-requisitos:**
    - Python 3 instalado.
    - `pip` (gerenciador de pacotes do Python).

2.  **Instalação de Dependências:**
    - Navegue até a pasta raiz do projeto (`escola_sistema`).
    - Instale o Flask executando no terminal:
      ```bash
      pip install Flask
      ```

3.  **Configuração do Banco de Dados:**
    - **Atenção:** Se o arquivo `escola.db` já existir e você precisar recriar o banco com a estrutura mais recente, delete-o primeiro.
    - Execute o script `database.py` para criar o banco de dados e o usuário gestor padrão:
      ```bash
      python database.py
      ```
    - **Credenciais do Gestor Padrão:**
        - **Email:** `admin@escola.com`
        - **Senha:** `admin123`

4.  **Iniciando a Aplicação:**
    - Execute o arquivo principal `app.py`:
      ```bash
      python app.py
      ```
    - A aplicação estará rodando em `http://127.0.0.1:5000`. Abra este endereço no seu navegador.

## 📋 Próximos Passos Planejados

- **Refatoração do Portal do Responsável:** Implementar suporte completo para um responsável ser associado a múltiplos alunos.
- **Histórico de Alterações (Audit Log ):** Criar um log para registrar ações críticas no sistema (ex: remoção de usuário).
- **Dashboard de Análise de Dados:** Ferramenta para o gestor visualizar gráficos de desempenho e evasão.

