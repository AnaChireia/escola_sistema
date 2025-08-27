import sqlite3

# Conecta ao banco de dados (cria o arquivo se não existir)
connection = sqlite3.connect('escola.db')

# Abre o arquivo schema.sql e executa os comandos
with open('schema.sql') as f:
    connection.executescript(f.read())

# Cria um usuário gestor padrão para o primeiro acesso
# cur = connection.cursor()
# cur.execute("INSERT INTO usuario (nome, email, senha, tipo_usuario) VALUES (?, ?, ?, ?)",
#             ('Admin Gestor', 'admin@escola.com', 'admin123', 'gestor')
#             )

connection.commit()
connection.close()

print("Banco de dados e usuário gestor criados com sucesso!")
