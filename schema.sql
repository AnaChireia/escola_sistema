-- Remove tabelas existentes se elas já existirem, na ordem correta para evitar erros de chave estrangeira.
DROP TABLE IF EXISTS responsavel_aluno;
DROP TABLE IF EXISTS inscricao;
DROP TABLE IF EXISTS leciona;
DROP TABLE IF EXISTS Nota;
DROP TABLE IF EXISTS Avaliacao;
DROP TABLE IF EXISTS Frequencia;
DROP TABLE IF EXISTS PlanoAula;
DROP TABLE IF EXISTS aviso;
DROP TABLE IF EXISTS disciplina;
DROP TABLE IF EXISTS usuario;

-- Tabela de Usuários: Estrutura principal para todos os tipos de usuários.
CREATE TABLE usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL,
    tipo_usuario TEXT NOT NULL CHECK(tipo_usuario IN ('gestor', 'professor', 'aluno', 'responsavel'))
);

-- (NOVO) Tabela de Disciplinas: Substitui a antiga tabela 'turma'.
-- Representa uma matéria ou disciplina ofertada (ex: "Matemática 9º Ano - 2025").
CREATE TABLE disciplina (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    ano INTEGER NOT NULL,
    periodo TEXT -- Ex: "1º Semestre", "Anual"
);

-- Tabela de Leciona: Associa um professor a uma ou mais disciplinas que ele leciona.
CREATE TABLE leciona (
    professor_id INTEGER NOT NULL,
    disciplina_id INTEGER NOT NULL,
    PRIMARY KEY (professor_id, disciplina_id),
    FOREIGN KEY (professor_id) REFERENCES usuario (id),
    FOREIGN KEY (disciplina_id) REFERENCES disciplina (id)
);

-- (NOVO) Tabela de Inscrição: Substitui a antiga 'matricula'.
-- Permite que um aluno se inscreva em várias disciplinas.
CREATE TABLE inscricao (
    aluno_id INTEGER NOT NULL,
    disciplina_id INTEGER NOT NULL,
    PRIMARY KEY (aluno_id, disciplina_id),
    FOREIGN KEY (aluno_id) REFERENCES usuario (id),
    FOREIGN KEY (disciplina_id) REFERENCES disciplina (id)
);

-- Tabela de Avaliações: Cada avaliação agora pertence a uma disciplina.
CREATE TABLE Avaliacao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    disciplina_id INTEGER NOT NULL,
    titulo TEXT NOT NULL,
    data_avaliacao DATE NOT NULL,
    FOREIGN KEY (disciplina_id) REFERENCES disciplina (id)
);

-- Tabela de Notas: Vincula a nota de um aluno a uma avaliação específica.
CREATE TABLE Nota (
    aluno_id INTEGER NOT NULL,
    avaliacao_id INTEGER NOT NULL,
    valor REAL,
    PRIMARY KEY (aluno_id, avaliacao_id),
    FOREIGN KEY (aluno_id) REFERENCES usuario (id),
    FOREIGN KEY (avaliacao_id) REFERENCES Avaliacao (id)
);

-- Tabela de Frequência: O registro de frequência agora é por disciplina.
CREATE TABLE Frequencia (
    aluno_id INTEGER NOT NULL,
    disciplina_id INTEGER NOT NULL,
    data DATE NOT NULL,
    presente INTEGER NOT NULL CHECK(presente IN (0, 1)), -- 1 para presente, 0 para ausente
    PRIMARY KEY (aluno_id, disciplina_id, data),
    FOREIGN KEY (aluno_id) REFERENCES usuario (id),
    FOREIGN KEY (disciplina_id) REFERENCES disciplina (id)
);

-- Tabela de Planos de Aula: O plano de aula pertence a uma disciplina.
CREATE TABLE PlanoAula (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    disciplina_id INTEGER NOT NULL,
    titulo TEXT NOT NULL,
    descricao TEXT,
    data_prevista DATE,
    FOREIGN KEY (disciplina_id) REFERENCES disciplina (id)
);

-- Tabela de Avisos: Permanece inalterada.
CREATE TABLE aviso (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    conteudo TEXT NOT NULL,
    data_publicacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Associação Responsável-Aluno: Permanece inalterada.
CREATE TABLE responsavel_aluno (
    responsavel_id INTEGER NOT NULL,
    aluno_id INTEGER NOT NULL,
    PRIMARY KEY (responsavel_id, aluno_id),
    FOREIGN KEY (responsavel_id) REFERENCES usuario (id),
    FOREIGN KEY (aluno_id) REFERENCES usuario (id)
);

-- Insere o usuário gestor padrão para o primeiro acesso.
INSERT INTO usuario (nome, email, senha, tipo_usuario) VALUES ('Admin Gestor', 'admin@escola.com', 'pbkdf2:sha256:600000$zWJpGff3hG3hF3a3$3e362b7121739b544325082163908a0534262165593c15a37b31b3a5148a2436', 'gestor');

