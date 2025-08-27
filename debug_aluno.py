import sqlite3

def debug_aluno_dados():
    """
    Script de debug para verificar os dados do aluno no banco de dados
    e identificar onde está o problema no carregamento das informações.
    """
    
    conn = sqlite3.connect('escola.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("🔍 DEBUG: Verificando dados do aluno no banco de dados")
    print("=" * 60)
    
    # 1. Verificar se o aluno Pedro Oliveira existe
    print("\n1. VERIFICANDO USUÁRIO 'Pedro Oliveira':")
    pedro = cursor.execute(
        'SELECT * FROM usuario WHERE nome LIKE "%Pedro%" AND tipo_usuario = "aluno"'
    ).fetchone()
    
    if pedro:
        print(f"✅ Aluno encontrado:")
        print(f"   ID: {pedro['id']}")
        print(f"   Nome: {pedro['nome']}")
        print(f"   Email: {pedro['email']}")
        print(f"   Tipo: {pedro['tipo_usuario']}")
        
        user_id = pedro['id']
        
        # 2. Verificar inscrições do aluno
        print(f"\n2. VERIFICANDO INSCRIÇÕES DO ALUNO (ID: {user_id}):")
        inscricoes = cursor.execute('''
            SELECT i.*, d.nome as disciplina_nome, d.ano, d.periodo 
            FROM inscricao i 
            JOIN disciplina d ON i.disciplina_id = d.id 
            WHERE i.aluno_id = ?
        ''', (user_id,)).fetchall()
        
        if inscricoes:
            print(f"✅ {len(inscricoes)} inscrições encontradas:")
            for inscricao in inscricoes:
                print(f"   - {inscricao['disciplina_nome']} ({inscricao['ano']}º ano - {inscricao['periodo']})")
        else:
            print("❌ Nenhuma inscrição encontrada para este aluno!")
        
        # 3. Verificar disciplinas disponíveis
        print(f"\n3. VERIFICANDO DISCIPLINAS DISPONÍVEIS:")
        disciplinas = cursor.execute('SELECT * FROM disciplina').fetchall()
        
        if disciplinas:
            print(f"✅ {len(disciplinas)} disciplinas encontradas:")
            for disciplina in disciplinas:
                print(f"   - ID: {disciplina['id']} | {disciplina['nome']} ({disciplina['ano']}º ano)")
        else:
            print("❌ Nenhuma disciplina encontrada no banco!")
        
        # 4. Verificar a consulta exata que o código está fazendo
        print(f"\n4. TESTANDO CONSULTA DO CÓDIGO (aluno_dashboard):")
        disciplinas_inscritas = cursor.execute('''
            SELECT d.* FROM disciplina d JOIN inscricao i ON d.id = i.disciplina_id
            WHERE i.aluno_id = ?
        ''', (user_id,)).fetchall()
        
        if disciplinas_inscritas:
            print(f"✅ Consulta retornou {len(disciplinas_inscritas)} disciplinas:")
            for disciplina in disciplinas_inscritas:
                print(f"   - {disciplina['nome']} (ID: {disciplina['id']})")
        else:
            print("❌ A consulta do código não retornou nenhuma disciplina!")
            print("   Isso explica por que o erro 'Não foi possível carregar as informações do aluno' aparece.")
        
        # 5. Verificar notas do aluno
        print(f"\n5. VERIFICANDO NOTAS DO ALUNO:")
        notas = cursor.execute('''
            SELECT n.*, a.titulo, d.nome as disciplina_nome
            FROM Nota n 
            JOIN Avaliacao a ON n.avaliacao_id = a.id
            JOIN disciplina d ON a.disciplina_id = d.id
            WHERE n.aluno_id = ?
        ''', (user_id,)).fetchall()
        
        if notas:
            print(f"✅ {len(notas)} notas encontradas:")
            for nota in notas:
                print(f"   - {nota['disciplina_nome']}: {nota['titulo']} = {nota['valor']}")
        else:
            print("⚠ Nenhuma nota encontrada para este aluno.")
        
        # 6. Verificar frequência do aluno
        print(f"\n6. VERIFICANDO FREQUÊNCIA DO ALUNO:")
        frequencia = cursor.execute('''
            SELECT f.*, d.nome as disciplina_nome
            FROM Frequencia f 
            JOIN disciplina d ON f.disciplina_id = d.id
            WHERE f.aluno_id = ?
            ORDER BY f.data DESC
            LIMIT 10
        ''', (user_id,)).fetchall()
        
        if frequencia:
            print(f"✅ {len(frequencia)} registros de frequência encontrados (últimos 10):")
            for freq in frequencia:
                status = "Presente" if freq['presente'] == 1 else "Ausente"
                print(f"   - {freq['data']} | {freq['disciplina_nome']}: {status}")
        else:
            print("⚠ Nenhum registro de frequência encontrado para este aluno.")
        
    else:
        print("❌ Aluno 'Pedro Oliveira' não encontrado no banco de dados!")
        
        # Listar todos os alunos disponíveis
        print("\n📋 ALUNOS DISPONÍVEIS NO BANCO:")
        alunos = cursor.execute('SELECT * FROM usuario WHERE tipo_usuario = "aluno"').fetchall()
        
        if alunos:
            for aluno in alunos:
                print(f"   - ID: {aluno['id']} | {aluno['nome']} | {aluno['email']}")
        else:
            print("❌ Nenhum aluno encontrado no banco de dados!")
    
    # 7. Verificar estrutura das tabelas
    print(f"\n7. VERIFICANDO ESTRUTURA DAS TABELAS:")
    
    # Tabela usuario
    usuarios_count = cursor.execute('SELECT COUNT(*) FROM usuario').fetchone()[0]
    print(f"   - Tabela 'usuario': {usuarios_count} registros")
    
    # Tabela disciplina
    disciplinas_count = cursor.execute('SELECT COUNT(*) FROM disciplina').fetchone()[0]
    print(f"   - Tabela 'disciplina': {disciplinas_count} registros")
    
    # Tabela inscricao
    inscricoes_count = cursor.execute('SELECT COUNT(*) FROM inscricao').fetchone()[0]
    print(f"   - Tabela 'inscricao': {inscricoes_count} registros")
    
    # Tabela Avaliacao
    avaliacoes_count = cursor.execute('SELECT COUNT(*) FROM Avaliacao').fetchone()[0]
    print(f"   - Tabela 'Avaliacao': {avaliacoes_count} registros")
    
    # Tabela Nota
    notas_count = cursor.execute('SELECT COUNT(*) FROM Nota').fetchone()[0]
    print(f"   - Tabela 'Nota': {notas_count} registros")
    
    # Tabela Frequencia
    frequencia_count = cursor.execute('SELECT COUNT(*) FROM Frequencia').fetchone()[0]
    print(f"   - Tabela 'Frequencia': {frequencia_count} registros")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("🔍 DEBUG CONCLUÍDO")
    print("=" * 60)

if __name__ == '__main__':
    debug_aluno_dados()

