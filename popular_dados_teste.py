import sqlite3
from datetime import datetime, date

def popular_dados_teste():
    """
    Script para popular o banco de dados com dados de teste
    para demonstrar o funcionamento do sistema de gestão escolar.
    """
    
    # Conecta ao banco de dados
    conn = sqlite3.connect('escola.db')
    cursor = conn.cursor()
    
    print("Populando banco de dados com dados de teste...")
    
    # 1. INSERIR USUÁRIOS DE TESTE
    usuarios_teste = [
        # Professores
        ('Prof. Maria Silva', 'maria.silva@escola.com', 'prof123', 'professor'),
        ('Prof. João Santos', 'joao.santos@escola.com', 'prof123', 'professor'),
        ('Prof. Ana Costa', 'ana.costa@escola.com', 'prof123', 'professor'),
        
        # Alunos
        ('Pedro Oliveira', 'pedro.oliveira@email.com', 'aluno123', 'aluno'),
        ('Ana Souza', 'ana.souza@email.com', 'aluno123', 'aluno'),
        ('Carlos Lima', 'carlos.lima@email.com', 'aluno123', 'aluno'),
        ('Mariana Santos', 'mariana.santos@email.com', 'aluno123', 'aluno'),
        ('Lucas Ferreira', 'lucas.ferreira@email.com', 'aluno123', 'aluno'),
        
        # Responsáveis
        ('José Oliveira', 'jose.oliveira@email.com', 'resp123', 'responsavel'),
        ('Maria Souza', 'maria.souza@email.com', 'resp123', 'responsavel'),
        ('Roberto Lima', 'roberto.lima@email.com', 'resp123', 'responsavel'),
    ]
    
    for nome, email, senha, tipo in usuarios_teste:
        try:
            cursor.execute(
                'INSERT INTO usuario (nome, email, senha, tipo_usuario) VALUES (?, ?, ?, ?)',
                (nome, email, senha, tipo)
            )
            print(f"✓ Usuário inserido: {nome} ({tipo})")
        except sqlite3.IntegrityError:
            print(f"⚠ Usuário já existe: {nome}")
    
    # 2. INSERIR DISCIPLINAS DE TESTE
    disciplinas_teste = [
        ('Matemática', 9, '1º Semestre'),
        ('Português', 9, '1º Semestre'),
        ('História', 9, '1º Semestre'),
        ('Geografia', 9, '1º Semestre'),
        ('Ciências', 9, '1º Semestre'),
        ('Inglês', 9, '1º Semestre'),
    ]
    
    for nome, ano, periodo in disciplinas_teste:
        try:
            cursor.execute(
                'INSERT INTO disciplina (nome, ano, periodo) VALUES (?, ?, ?)',
                (nome, ano, periodo)
            )
            print(f"✓ Disciplina inserida: {nome} - {ano}º ano")
        except sqlite3.IntegrityError:
            print(f"⚠ Disciplina já existe: {nome}")
    
    # 3. BUSCAR IDs DOS USUÁRIOS E DISCIPLINAS INSERIDOS
    professores = cursor.execute(
        'SELECT id, nome FROM usuario WHERE tipo_usuario = "professor"'
    ).fetchall()
    
    alunos = cursor.execute(
        'SELECT id, nome FROM usuario WHERE tipo_usuario = "aluno"'
    ).fetchall()
    
    responsaveis = cursor.execute(
        'SELECT id, nome FROM usuario WHERE tipo_usuario = "responsavel"'
    ).fetchall()
    
    disciplinas = cursor.execute('SELECT id, nome FROM disciplina').fetchall()
    
    # 4. ASSOCIAR PROFESSORES ÀS DISCIPLINAS (LECIONA)
    if professores and disciplinas:
        # Prof. Maria Silva -> Matemática e Ciências
        if len(professores) >= 1 and len(disciplinas) >= 1:
            cursor.execute(
                'INSERT OR IGNORE INTO leciona (professor_id, disciplina_id) VALUES (?, ?)',
                (professores[0][0], disciplinas[0][0])  # Maria -> Matemática
            )
            if len(disciplinas) >= 5:
                cursor.execute(
                    'INSERT OR IGNORE INTO leciona (professor_id, disciplina_id) VALUES (?, ?)',
                    (professores[0][0], disciplinas[4][0])  # Maria -> Ciências
                )
        
        # Prof. João Santos -> Português e História
        if len(professores) >= 2 and len(disciplinas) >= 2:
            cursor.execute(
                'INSERT OR IGNORE INTO leciona (professor_id, disciplina_id) VALUES (?, ?)',
                (professores[1][0], disciplinas[1][0])  # João -> Português
            )
            if len(disciplinas) >= 3:
                cursor.execute(
                    'INSERT OR IGNORE INTO leciona (professor_id, disciplina_id) VALUES (?, ?)',
                    (professores[1][0], disciplinas[2][0])  # João -> História
                )
        
        # Prof. Ana Costa -> Geografia e Inglês
        if len(professores) >= 3 and len(disciplinas) >= 4:
            cursor.execute(
                'INSERT OR IGNORE INTO leciona (professor_id, disciplina_id) VALUES (?, ?)',
                (professores[2][0], disciplinas[3][0])  # Ana -> Geografia
            )
            if len(disciplinas) >= 6:
                cursor.execute(
                    'INSERT OR IGNORE INTO leciona (professor_id, disciplina_id) VALUES (?, ?)',
                    (professores[2][0], disciplinas[5][0])  # Ana -> Inglês
                )
        
        print("✓ Professores associados às disciplinas")
    
    # 5. INSCREVER ALUNOS NAS DISCIPLINAS
    if alunos and disciplinas:
        for aluno_id, aluno_nome in alunos:
            # Inscrever cada aluno em todas as disciplinas
            for disciplina_id, disciplina_nome in disciplinas:
                cursor.execute(
                    'INSERT OR IGNORE INTO inscricao (aluno_id, disciplina_id) VALUES (?, ?)',
                    (aluno_id, disciplina_id)
                )
            print(f"✓ Aluno {aluno_nome} inscrito em todas as disciplinas")
    
    # 6. ASSOCIAR RESPONSÁVEIS AOS ALUNOS
    if responsaveis and alunos:
        # José Oliveira -> Pedro Oliveira
        if len(responsaveis) >= 1 and len(alunos) >= 1:
            cursor.execute(
                'INSERT OR IGNORE INTO responsavel_aluno (responsavel_id, aluno_id) VALUES (?, ?)',
                (responsaveis[0][0], alunos[0][0])
            )
        
        # Maria Souza -> Ana Souza
        if len(responsaveis) >= 2 and len(alunos) >= 2:
            cursor.execute(
                'INSERT OR IGNORE INTO responsavel_aluno (responsavel_id, aluno_id) VALUES (?, ?)',
                (responsaveis[1][0], alunos[1][0])
            )
        
        # Roberto Lima -> Carlos Lima
        if len(responsaveis) >= 3 and len(alunos) >= 3:
            cursor.execute(
                'INSERT OR IGNORE INTO responsavel_aluno (responsavel_id, aluno_id) VALUES (?, ?)',
                (responsaveis[2][0], alunos[2][0])
            )
        
        print("✓ Responsáveis associados aos alunos")
    
    # 7. CRIAR ALGUMAS AVALIAÇÕES DE TESTE
    if disciplinas:
        avaliacoes_teste = [
            (disciplinas[0][0], 'Prova 1 - Álgebra', '2024-03-15'),  # Matemática
            (disciplinas[0][0], 'Trabalho - Geometria', '2024-04-10'),  # Matemática
            (disciplinas[1][0], 'Prova 1 - Gramática', '2024-03-20'),  # Português
            (disciplinas[1][0], 'Redação', '2024-04-05'),  # Português
            (disciplinas[2][0], 'Prova - Brasil Colonial', '2024-03-25'),  # História
        ]
        
        for disciplina_id, titulo, data in avaliacoes_teste:
            cursor.execute(
                'INSERT OR IGNORE INTO Avaliacao (disciplina_id, titulo, data_avaliacao) VALUES (?, ?, ?)',
                (disciplina_id, titulo, data)
            )
        
        print("✓ Avaliações de teste criadas")
    
    # 8. INSERIR ALGUMAS NOTAS DE TESTE
    avaliacoes = cursor.execute('SELECT id FROM Avaliacao').fetchall()
    if alunos and avaliacoes:
        import random
        for aluno_id, _ in alunos:
            for avaliacao_id, in avaliacoes:
                # Gerar nota aleatória entre 6.0 e 10.0
                nota = round(random.uniform(6.0, 10.0), 1)
                cursor.execute(
                    'INSERT OR IGNORE INTO Nota (aluno_id, avaliacao_id, valor) VALUES (?, ?, ?)',
                    (aluno_id, avaliacao_id, nota)
                )
        
        print("✓ Notas de teste inseridas")
    
    # 9. INSERIR REGISTROS DE FREQUÊNCIA DE TESTE
    if alunos and disciplinas:
        import random
        from datetime import datetime, timedelta
        
        # Criar registros de frequência para os últimos 30 dias
        data_inicio = datetime.now() - timedelta(days=30)
        
        for i in range(30):
            data_atual = data_inicio + timedelta(days=i)
            data_str = data_atual.strftime('%Y-%m-%d')
            
            for aluno_id, _ in alunos:
                for disciplina_id, _ in disciplinas:
                    # 90% de chance de estar presente
                    presente = 1 if random.random() > 0.1 else 0
                    cursor.execute(
                        'INSERT OR IGNORE INTO Frequencia (aluno_id, disciplina_id, data, presente) VALUES (?, ?, ?, ?)',
                        (aluno_id, disciplina_id, data_str, presente)
                    )
        
        print("✓ Registros de frequência inseridos")
    
    # 10. INSERIR ALGUNS AVISOS DE TESTE
    avisos_teste = [
        ('Reunião de Pais', 'Reunião de pais e mestres será realizada no dia 15/04 às 19h no auditório da escola.'),
        ('Feriado Escolar', 'Não haverá aulas no dia 21/04 devido ao feriado de Tiradentes.'),
        ('Entrega de Boletins', 'Os boletins do 1º bimestre estarão disponíveis a partir do dia 30/04.'),
    ]
    
    for titulo, conteudo in avisos_teste:
        cursor.execute(
            'INSERT OR IGNORE INTO aviso (titulo, conteudo) VALUES (?, ?)',
            (titulo, conteudo)
        )
    
    print("✓ Avisos de teste inseridos")
    
    # Confirmar todas as alterações
    conn.commit()
    conn.close()
    
    print("\n🎉 Banco de dados populado com sucesso!")
    print("\n📋 DADOS DE LOGIN PARA TESTE:")
    print("=" * 50)
    print("GESTOR:")
    print("  Email: admin@escola.com")
    print("  Senha: admin123")
    print("\nPROFESSORES:")
    print("  Email: maria.silva@escola.com | Senha: prof123")
    print("  Email: joao.santos@escola.com | Senha: prof123")
    print("  Email: ana.costa@escola.com | Senha: prof123")
    print("\nALUNOS:")
    print("  Email: pedro.oliveira@email.com | Senha: aluno123")
    print("  Email: ana.souza@email.com | Senha: aluno123")
    print("  Email: carlos.lima@email.com | Senha: aluno123")
    print("\nRESPONSÁVEIS:")
    print("  Email: jose.oliveira@email.com | Senha: resp123")
    print("  Email: maria.souza@email.com | Senha: resp123")
    print("  Email: roberto.lima@email.com | Senha: resp123")
    print("=" * 50)

if __name__ == '__main__':
    popular_dados_teste()

