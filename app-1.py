import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime, date
from functools import wraps
import re


app = Flask(__name__)

app.secret_key = 'chave_segura'  # Necessário para usar sessões

# def login_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if 'user_id' not in session:
#             flash('Por favor, faça o login para acessar esta página.', 'warning')
#             return redirect(url_for('login'))
#         return f(*args, **kwargs)
#     return decorated_function

# def role_required(role):
#     """
#     Decorador que verifica se o usuário está logado E se tem a função necessária.
#     """
#     def wrapper(f):
#         @wraps(f)
#         def decorated_function(*args, **kwargs):
#             if 'user_id' not in session:
#                 flash('Por favor, faça o login para acessar esta página.', 'warning')
#                 return redirect(url_for('login'))
            
#             if session.get('user_type') != role:
#                 flash('Você não tem permissão para acessar esta página.', 'danger')
#                 if session.get('user_type') == 'professor':
#                     return redirect(url_for('professor_dashboard', professor_id=session.get('user_id')))
#                 return redirect(url_for('index'))
            
#             return f(*args, **kwargs)
#         return decorated_function
#     return wrapper

def role_required(roles): # Agora aceita uma lista de roles
    """
    Decorador que verifica se o usuário está logado E se tem a função(ões) necessária(s).
    """
    if not isinstance(roles, list): # Garante que 'roles' é sempre uma lista
        roles = [roles]

    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Por favor, faça o login para acessar esta página.', 'warning')
                return redirect(url_for('login'))
            
            # Verifica se o tipo de usuário está na lista de roles permitidas
            if session.get('user_type') not in roles: 
                flash('Você não tem permissão para acessar esta página.', 'danger')
                # Redireciona para o dashboard apropriado ou para o login
                if session.get('user_type') == 'professor':
                    return redirect(url_for('professor_dashboard', professor_id=session.get('user_id')))
                elif session.get('user_type') == 'gestor':
                    return redirect(url_for('index'))
                # Se for aluno/responsável tentando acessar algo que não pode, vai para o dashboard do aluno
                elif session.get('user_type') in ['aluno', 'responsavel']:
                    return redirect(url_for('aluno_dashboard'))
                return redirect(url_for('login')) # Caso não caia em nenhum dos anteriores
            
            return f(*args, **kwargs)
        return decorated_function
    return wrapper



def get_db_connection():
    """Cria uma conexão com o banco de dados."""
    conn = sqlite3.connect('escola.db')
    conn.row_factory = sqlite3.Row # Permite acessar colunas por nome
    return conn

@app.route('/')
@role_required('gestor')
def index():
    """Página inicial - Dashboard do Gestor."""
    conn = get_db_connection()
    total_usuarios = conn.execute('SELECT COUNT(id) FROM usuario').fetchone()[0]
    total_turmas = conn.execute('SELECT COUNT(id) FROM turma').fetchone()[0]
    conn.close()
    return render_template('index.html', total_usuarios=total_usuarios, total_turmas=total_turmas)

@app.route('/usuarios', methods=('GET', 'POST'))
@role_required('gestor')
def usuarios():
    conn = get_db_connection()

    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        tipo_usuario = request.form['tipo_usuario']

        # --- INÍCIO DA VALIDAÇÃO NO BACKEND ---
        # 1. Define o padrão de email que queremos
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        
        # 2. Verifica se o email não corresponde ao padrão
        if not email_pattern.match(email):
            flash('Formato de email inválido. Por favor, verifique e tente novamente.', 'danger')
            conn.close() # Fechar conexão antes de redirecionar
            return redirect(url_for('usuarios')) # Volta para a página sem cadastrar

        # 3. Verifica se o email já existe no banco de dados
        email_existente = conn.execute('SELECT id FROM usuario WHERE email = ?', (email,)).fetchone()
        
        if email_existente:
            flash('Este endereço de email já está cadastrado.', 'danger')
            conn.close() # Fechar conexão antes de redirecionar
            return redirect(url_for('usuarios'))
        # --- FIM DA VALIDAÇÃO ---

        # Se todas as validações passaram, insere o novo usuário
        conn.execute('INSERT INTO usuario (nome, email, senha, tipo_usuario) VALUES (?, ?, ?, ?)',
                     (nome, email, senha, tipo_usuario))
        conn.commit()
        flash('Usuário cadastrado com sucesso!', 'success')
        
    # Se for GET, ou se o POST falhou na validação e redirecionou, busca e exibe todos os usuários
    lista_usuarios = conn.execute('SELECT * FROM usuario').fetchall()
    conn.close()
    return render_template('usuarios.html', usuarios=lista_usuarios)

@app.route('/usuario/<int:usuario_id>/editar', methods=('GET', 'POST'))
@role_required('gestor')
def editar_usuario(usuario_id):
    conn = get_db_connection()
    usuario = conn.execute('SELECT * FROM usuario WHERE id = ?', (usuario_id,)).fetchone()

    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        tipo_usuario = request.form['tipo_usuario']
        senha = request.form['senha']

        # Validação de email (semelhante ao cadastro)
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not email_pattern.match(email):
            flash('Formato de email inválido.', 'danger')
            return render_template('editar_usuario.html', usuario=usuario)

        # Verifica se o email foi alterado e se o novo já existe
        if email != usuario['email']:
            email_existente = conn.execute('SELECT id FROM usuario WHERE email = ?', (email,)).fetchone()
            if email_existente:
                flash('O novo endereço de email já está em uso por outro usuário.', 'danger')
                return render_template('editar_usuario.html', usuario=usuario)

        # Lógica de atualização
        if senha:
            # Se uma nova senha foi fornecida, atualiza
            conn.execute('UPDATE usuario SET nome = ?, email = ?, tipo_usuario = ?, senha = ? WHERE id = ?',
                         (nome, email, tipo_usuario, senha, usuario_id))
        else:
            # Senão, atualiza tudo exceto a senha
            conn.execute('UPDATE usuario SET nome = ?, email = ?, tipo_usuario = ? WHERE id = ?',
                         (nome, email, tipo_usuario, usuario_id))
        
        conn.commit()
        conn.close()
        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('usuarios'))

    # Se for GET, apenas exibe a página
    conn.close()
    return render_template('editar_usuario.html', usuario=usuario)


@app.route('/usuario/<int:usuario_id>/remover')
@role_required('gestor')
def remover_usuario(usuario_id):
    # CUIDADO: Em um sistema real, remover um usuário pode quebrar relações
    # (ex: notas ou frequência associadas a ele). O ideal seria "desativar" o usuário.
    # Para este projeto, a remoção direta é aceitável.
    conn = get_db_connection()
    conn.execute('DELETE FROM usuario WHERE id = ?', (usuario_id,))
    # Também seria necessário remover as associações em 'matricula', 'leciona', 'nota', etc.
    # Vamos manter simples por enquanto.
    conn.commit()
    conn.close()
    flash('Usuário removido com sucesso.', 'info')
    return redirect(url_for('usuarios'))


@app.route('/turmas', methods=('GET', 'POST'))
@role_required('gestor')
def turmas():
    """Página para gerenciar turmas."""
    conn = get_db_connection()

    if request.method == 'POST':
        # Lógica para adicionar uma nova turma
        nome = request.form['nome']
        ano_letivo = request.form['ano_letivo']
        
        conn.execute('INSERT INTO turma (nome, ano_letivo) VALUES (?, ?)',
                     (nome, ano_letivo))
        conn.commit()
        return redirect(url_for('turmas'))

    # Se for GET, busca e exibe todas as turmas
    lista_turmas = conn.execute('SELECT * FROM turma').fetchall()
    conn.close()
    return render_template('turmas.html', turmas=lista_turmas)


@app.route('/professor/<int:professor_id>')
@role_required('professor')
def professor_dashboard(professor_id):
    """
    Página inicial para o professor, mostrando suas turmas.
    Por enquanto, vamos assumir que o login foi feito e temos o ID.
    """
    conn = get_db_connection()
    
    # Busca os dados do professor
    professor = conn.execute('SELECT * FROM usuario WHERE id = ? AND tipo_usuario = "professor"', 
                             (professor_id,)).fetchone()
    
    if professor is None:
        # Se não encontrar um professor com esse ID, retorna erro 404
        return "Professor não encontrado", 404

    # Busca as turmas associadas a este professor
    turmas = conn.execute('''
        SELECT t.* FROM turma t
        JOIN leciona l ON t.id = l.turma_id
        WHERE l.professor_id = ?
    ''', (professor_id,)).fetchall()
    
    # ... (código para buscar professor e turmas) ...

    # Busca os 3 avisos mais recentes para exibir no dashboard
    avisos_db = conn.execute('SELECT * FROM aviso ORDER BY data_publicacao DESC LIMIT 3').fetchall()
    avisos_formatados = []
    for aviso in avisos_db:
        aviso_dict = dict(aviso)
        aviso_dict['data_publicacao'] = datetime.strptime(aviso_dict['data_publicacao'], '%Y-%m-%d %H:%M:%S')
        avisos_formatados.append(aviso_dict)

    conn.close()
    return render_template('professor_dashboard.html', professor=professor, turmas=turmas, avisos=avisos_formatados)


@app.route('/turma/<int:turma_id>/notas')
@role_required('professor')
def gerenciar_notas(turma_id):
    """Exibe a página de gerenciamento de notas para uma turma."""
    conn = get_db_connection()
    
    # Busca a turma e o professor responsável (para o link de "voltar")
    turma = conn.execute('SELECT * FROM turma WHERE id = ?', (turma_id,)).fetchone()
    # Precisamos saber o professor para criar o link de voltar. Em um sistema real,
    # isso viria da sessão do usuário logado.
    leciona = conn.execute('SELECT professor_id FROM leciona WHERE turma_id = ?', (turma_id,)).fetchone()
    professor = conn.execute('SELECT * FROM usuario WHERE id = ?', (leciona['professor_id'],)).fetchone()

    # Busca todos os alunos matriculados na turma
    alunos = conn.execute('''
        SELECT u.* FROM usuario u JOIN matricula m ON u.id = m.aluno_id
        WHERE m.turma_id = ? ORDER BY u.nome
    ''', (turma_id,)).fetchall()

    # Busca todas as avaliações criadas para esta turma
    avaliacoes = conn.execute('SELECT * FROM avaliacao WHERE turma_id = ? ORDER BY id', (turma_id,)).fetchall()

    # Busca todas as notas já lançadas e as organiza em um dicionário para fácil acesso
    # A chave do dicionário será (aluno_id, avaliacao_id)
    notas_db = conn.execute('''
        SELECT aluno_id, avaliacao_id, valor FROM nota
    ''').fetchall()
    notas = {(n['aluno_id'], n['avaliacao_id']): n['valor'] for n in notas_db}

    conn.close()
    
    return render_template('gerenciar_notas.html', turma=turma, professor=professor, alunos=alunos, avaliacoes=avaliacoes, notas=notas)

@app.route('/turma/<int:turma_id>/avaliacoes/nova', methods=['POST'])
@role_required('professor')
def criar_avaliacao(turma_id):
    """Processa o formulário para criar uma nova avaliação."""
    nome_avaliacao = request.form['nome_avaliacao']
    
    # Em um sistema real, o professor_id viria da sessão do usuário logado
    conn = get_db_connection()
    leciona = conn.execute('SELECT professor_id FROM leciona WHERE turma_id = ?', (turma_id,)).fetchone()
    professor_id = leciona['professor_id']
    
    # Insere a nova avaliação no banco de dados
    conn.execute('INSERT INTO avaliacao (nome, data, turma_id, professor_id) VALUES (?, date("now"), ?, ?)',
                 (nome_avaliacao, turma_id, professor_id))
    conn.commit()
    conn.close()
    
    # Redireciona de volta para a página de notas
    return redirect(url_for('gerenciar_notas', turma_id=turma_id))

@app.route('/turma/<int:turma_id>/notas/salvar', methods=['POST'])
@role_required('professor')
def salvar_notas(turma_id):
    """Processa o formulário principal, salvando todas as notas."""
    conn = get_db_connection()
    
    # Itera sobre todos os dados enviados pelo formulário
    for key, value in request.form.items():
        if key.startswith('nota-') and value: 
            parts = key.split('-')
            aluno_id = int(parts[1])
            avaliacao_id = int(parts[2])
            nota_valor = float(value)

            # Verifica se a nota já existe para dar UPDATE, senão, dá INSERT
            existe = conn.execute('SELECT id FROM nota WHERE aluno_id = ? AND avaliacao_id = ?', 
                                  (aluno_id, avaliacao_id)).fetchone()
            
            if existe:
                conn.execute('UPDATE nota SET valor = ? WHERE id = ?', (nota_valor, existe['id']))
            else:
                conn.execute('INSERT INTO nota (aluno_id, avaliacao_id, valor) VALUES (?, ?, ?)',
                             (aluno_id, avaliacao_id, nota_valor))
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('gerenciar_notas', turma_id=turma_id))


@app.route('/turma/<int:turma_id>/frequencia', methods=['GET', 'POST'])
@role_required('professor')
def registrar_frequencia(turma_id):
    """Exibe e processa o registro de frequência para uma turma."""
    conn = get_db_connection()
    
    # Busca informações básicas (turma, professor)
    turma = conn.execute('SELECT * FROM turma WHERE id = ?', (turma_id,)).fetchone()
    leciona = conn.execute('SELECT professor_id FROM leciona WHERE turma_id = ?', (turma_id,)).fetchone()
    professor = conn.execute('SELECT * FROM usuario WHERE id = ?', (leciona['professor_id'],)).fetchone()

    # Busca todos os alunos matriculados na turma
    alunos = conn.execute('''
        SELECT u.* FROM usuario u JOIN matricula m ON u.id = m.aluno_id
        WHERE m.turma_id = ? ORDER BY u.nome
    ''', (turma_id,)).fetchall()

    # Determina a data para a chamada
    # Se uma data for passada via GET ou POST, usa essa data. Senão, usa a data de hoje.
    if request.method == 'POST':
        data_selecionada = request.form['data']
    else: # GET
        data_selecionada = request.args.get('data', date.today().isoformat())

    if request.method == 'POST':
        # Lógica para SALVAR os dados da frequência
        conn.execute('DELETE FROM frequencia WHERE turma_id = ? AND data = ?', (turma_id, data_selecionada))
        
        for aluno in alunos:
            aluno_id = aluno['id']
            # O formulário envia '1' se o checkbox estiver marcado. Se não, não envia nada.
            presente = 1 if f'presenca-{aluno_id}' in request.form else 0
            
            conn.execute('INSERT INTO frequencia (data, presente, aluno_id, turma_id) VALUES (?, ?, ?, ?)',
                         (data_selecionada, presente, aluno_id, turma_id))
        conn.commit()

    # Busca os registros de frequência para a data selecionada para preencher os checkboxes
    registros_db = conn.execute('SELECT aluno_id, presente FROM frequencia WHERE turma_id = ? AND data = ?',
                                (turma_id, data_selecionada)).fetchall()
    registros_frequencia = {r['aluno_id']: r['presente'] for r in registros_db}
    
    conn.close()

    return render_template('registrar_frequencia.html', 
                           turma=turma, 
                           professor=professor, 
                           alunos=alunos, 
                           data_selecionada=data_selecionada,
                           registros_frequencia=registros_frequencia)

# Rota para gerenciar os planos de aula de uma turma
@app.route('/turma/<int:turma_id>/planos', methods=('GET', 'POST'))
@role_required('professor')
def gerenciar_planos_aula(turma_id):
    conn = get_db_connection()
    turma = conn.execute('SELECT * FROM turma WHERE id = ?', (turma_id,)).fetchone()

    if request.method == 'POST':
        titulo = request.form['titulo']
        data_aula = request.form['data_aula']
        descricao = request.form['descricao']
        professor_id = session['user_id']

        if not titulo or not data_aula:
            flash('Título e data da aula são obrigatórios.', 'danger')
        else:
            conn.execute('INSERT INTO plano_aula (titulo, descricao, data_aula, turma_id, professor_id) VALUES (?, ?, ?, ?, ?)',
                         (titulo, descricao, data_aula, turma_id, professor_id))
            conn.commit()
            flash('Plano de aula salvo com sucesso!', 'success')
        
        return redirect(url_for('gerenciar_planos_aula', turma_id=turma_id))

    # Se for GET, busca os planos de aula para listar
    planos_aula = conn.execute('SELECT * FROM plano_aula WHERE turma_id = ? AND professor_id = ? ORDER BY data_aula DESC',
                               (turma_id, session['user_id'])).fetchall()
    conn.close()
    return render_template('planos_aula.html', turma=turma, planos_aula=planos_aula)

# Rota para remover um plano de aula
@app.route('/plano_aula/<int:plano_id>/remover')
@role_required('professor')
def remover_plano_aula(plano_id):
    conn = get_db_connection()
    # Pega o turma_id antes de deletar, para poder redirecionar de volta
    plano = conn.execute('SELECT turma_id FROM plano_aula WHERE id = ?', (plano_id,)).fetchone()
    if plano:
        turma_id = plano['turma_id']
        conn.execute('DELETE FROM plano_aula WHERE id = ?', (plano_id,))
        conn.commit()
        flash('Plano de aula removido com sucesso.', 'info')
        conn.close()
        return redirect(url_for('gerenciar_planos_aula', turma_id=turma_id))
    
    conn.close()
    flash('Plano de aula não encontrado.', 'danger')
    return redirect(url_for('professor_dashboard', professor_id=session['user_id']))


@app.route('/login', methods=['GET','POST'])
def login():

        
        conn = get_db_connection()
        print('------------------------------------')
        print(conn)
        teste = conn.execute('SELECT * FROM usuario').fetchall()
        print(teste)
        print('------------------------------------')
    #Pagina de login
        if request.method == 'POST':
            email = request.form['email']
            senha = request.form['senha']
                
            usuario = conn.execute('SELECT * FROM usuario WHERE email = ? AND senha = ?', (email, senha)).fetchone()

            
        
            if usuario:
                # Se o usuário foi encontrado, AGORA podemos acessar seus dados
                session['user_id'] = usuario['id']
                session['user_name'] = usuario['nome']
                session['user_type'] = usuario['tipo_usuario']
                conn.close() # Fechamos a conexão aqui
                
                
                
                if usuario['tipo_usuario'] == 'gestor':
                    return redirect(url_for('index'))
                elif usuario['tipo_usuario'] == 'professor':
                    return redirect(url_for('professor_dashboard', professor_id=usuario['id']))
                elif usuario['tipo_usuario'] == 'aluno' or usuario['tipo_usuario'] == 'responsavel':
                    return redirect(url_for('aluno_dashboard')) # Redireciona para o novo dashboard do aluno
                else:
                    return redirect(url_for('index')) # Redirecionamento padrão para outros tipos

            else:
                # Se o usuário NÃO foi encontrado (usuario é None)
                conn.close() # Também fechamos a conexão aqui
                flash('Email ou senha incorretos. Tente novamente.', 'danger')
                return redirect(url_for('login'))
        return render_template('login.html')

# ===============================================================
# ROTAS PARA O PORTAL DO ALUNO/RESPONSÁVEL (INCREMENTO 2 - FINAL)
# ===============================================================

@app.route('/aluno/dashboard')
@role_required(['aluno', 'responsavel']) # Corrigido para aceitar a lista
def aluno_dashboard():
    conn = get_db_connection()
    aluno_id = None

    # Passo 1: Identificar qual aluno devemos buscar
    if session['user_type'] == 'aluno':
        aluno_id = session['user_id']
    elif session['user_type'] == 'responsavel':
        # Lógica para encontrar o filho do responsável.
        # Como ainda não temos a tabela de associação, vamos simular.
        # Esta parte precisará ser melhorada no futuro.
        # Por agora, vamos buscar o primeiro aluno que não seja o próprio responsável.
        filho = conn.execute('SELECT id FROM usuario WHERE tipo_usuario = "aluno" LIMIT 1').fetchone()
        if filho:
            aluno_id = filho['id']
        else:
            flash('Nenhum aluno encontrado no sistema para associar a este responsável.', 'warning')
            conn.close()
            # Redireciona para o logout para evitar loops se não houver o que mostrar.
            return redirect(url_for('logout'))

    # Se não conseguimos identificar um aluno, não há o que fazer.
    if not aluno_id:
        flash('Não foi possível identificar o aluno. Por favor, contate o suporte.', 'danger')
        conn.close()
        return redirect(url_for('logout'))

    # Passo 2: Buscar os dados do aluno identificado
    aluno = conn.execute('SELECT * FROM usuario WHERE id = ?', (aluno_id,)).fetchone()
    if not aluno:
        flash('Os dados do aluno não foram encontrados.', 'danger')
        conn.close()
        return redirect(url_for('logout'))

    # O resto da lógica continua a mesma...
    matricula = conn.execute('SELECT turma_id FROM matricula WHERE aluno_id = ?', (aluno['id'],)).fetchone()
    if not matricula:
        flash(f"O aluno {aluno['nome']} não está matriculado em nenhuma turma.", 'warning')
        # Renderiza a página com uma mensagem, em vez de redirecionar, para evitar loops.
        return render_template('aluno_dashboard.html', aluno=aluno, turma={'nome': 'N/A', 'ano_letivo': 'N/A'}, avaliacoes=[], notas={}, total_aulas=0, total_presencas=0, total_faltas=0, porcentagem_presenca=0)

    turma = conn.execute('SELECT * FROM turma WHERE id = ?', (matricula['turma_id'],)).fetchone()
    avaliacoes = conn.execute('SELECT * FROM avaliacao WHERE turma_id = ? ORDER BY data, id', (turma['id'],)).fetchall()
    notas_db = conn.execute('SELECT avaliacao_id, valor FROM nota WHERE aluno_id = ?', (aluno['id'],)).fetchall()
    notas = {n['avaliacao_id']: n['valor'] for n in notas_db}
    registros_frequencia = conn.execute('SELECT presente FROM frequencia WHERE aluno_id = ?', (aluno['id'],)).fetchall()
    total_aulas = len(registros_frequencia)
    total_presencas = sum(1 for r in registros_frequencia if r['presente'] == 1)
    total_faltas = total_aulas - total_presencas
    porcentagem_presenca = (total_presencas / total_aulas * 100) if total_aulas > 0 else 0

    avisos_db = conn.execute('SELECT * FROM aviso ORDER BY data_publicacao DESC LIMIT 3').fetchall()
    avisos_formatados = []
    for aviso in avisos_db:
        aviso_dict = dict(aviso)
        aviso_dict['data_publicacao'] = datetime.strptime(aviso_dict['data_publicacao'], '%Y-%m-%d %H:%M:%S')
        avisos_formatados.append(aviso_dict)
    conn.close()
    
    return render_template('aluno_dashboard.html', 
                           aluno=aluno, 
                           turma=turma, 
                           avaliacoes=avaliacoes, 
                           notas=notas,
                           total_aulas=total_aulas,
                           total_presencas=total_presencas,
                           total_faltas=total_faltas,
                           porcentagem_presenca=porcentagem_presenca,
                           avisos=avisos_formatados)                           



@app.route('/logout')
def logout():
    # Limpa a sessão do usuário
    session.clear()
    flash('Você foi desconectado com sucesso.', 'info')
    return redirect(url_for('login'))   


#Adicional de alteração e definição de turma

@app.route('/turma/<int:turma_id>/detalhes')
@role_required('gestor')
def detalhes_turma(turma_id):
    """Exibe a página de detalhes de uma turma com seus professores e alunos."""
    conn = get_db_connection()
    turma = conn.execute('SELECT * FROM turma WHERE id = ?', (turma_id,)).fetchone()

    # Busca professores que JÁ ESTÃO na turma
    professores_da_turma = conn.execute('''
        SELECT u.id, u.nome FROM usuario u JOIN leciona l ON u.id = l.professor_id
        WHERE l.turma_id = ?
    ''', (turma_id,)).fetchall()
    
    # Busca professores que NÃO ESTÃO na turma para popular o dropdown
    ids_professores_na_turma = [p['id'] for p in professores_da_turma]
    placeholders = ','.join('?' for _ in ids_professores_na_turma)
    query_outros_prof = 'SELECT id, nome FROM usuario WHERE tipo_usuario = "professor"'
    if ids_professores_na_turma:
        query_outros_prof += f' AND id NOT IN ({placeholders})'
    outros_professores = conn.execute(query_outros_prof, ids_professores_na_turma).fetchall()

    # Busca alunos que JÁ ESTÃO na turma
    alunos_da_turma = conn.execute('''
        SELECT u.id, u.nome FROM usuario u JOIN matricula m ON u.id = m.aluno_id
        WHERE m.turma_id = ?
    ''', (turma_id,)).fetchall()

    # Busca alunos que NÃO ESTÃO na turma
    ids_alunos_na_turma = [a['id'] for a in alunos_da_turma]
    placeholders = ','.join('?' for _ in ids_alunos_na_turma)
    query_outros_alunos = 'SELECT id, nome FROM usuario WHERE tipo_usuario = "aluno"'
    if ids_alunos_na_turma:
        query_outros_alunos += f' AND id NOT IN ({placeholders})'
    outros_alunos = conn.execute(query_outros_alunos, ids_alunos_na_turma).fetchall()

    conn.close()
    return render_template('detalhes_turma.html', 
                           turma=turma, 
                           professores_da_turma=professores_da_turma,
                           outros_professores=outros_professores,
                           alunos_da_turma=alunos_da_turma,
                           outros_alunos=outros_alunos)

@app.route('/turma/<int:turma_id>/adicionar_professor', methods=['POST'])
@role_required('gestor')
def adicionar_professor_turma(turma_id):
    professor_id = request.form['professor_id']
    conn = get_db_connection()
    conn.execute('INSERT INTO leciona (professor_id, turma_id) VALUES (?, ?)', (professor_id, turma_id))
    conn.commit()
    conn.close()
    flash('Professor adicionado à turma com sucesso!', 'success')
    return redirect(url_for('detalhes_turma', turma_id=turma_id))

@app.route('/turma/<int:turma_id>/remover_professor/<int:professor_id>')
@role_required('gestor')
def remover_professor_turma(turma_id, professor_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM leciona WHERE professor_id = ? AND turma_id = ?', (professor_id, turma_id))
    conn.commit()
    conn.close()
    flash('Professor removido da turma.', 'info')
    return redirect(url_for('detalhes_turma', turma_id=turma_id))

@app.route('/turma/<int:turma_id>/adicionar_aluno', methods=['POST'])
@role_required('gestor')
def adicionar_aluno_turma(turma_id):
    aluno_id = request.form['aluno_id']
    conn = get_db_connection()
    conn.execute('INSERT INTO matricula (aluno_id, turma_id) VALUES (?, ?)', (aluno_id, turma_id))
    conn.commit()
    conn.close()
    flash('Aluno matriculado na turma com sucesso!', 'success')
    return redirect(url_for('detalhes_turma', turma_id=turma_id))

@app.route('/turma/<int:turma_id>/remover_aluno/<int:aluno_id>')
@role_required('gestor')
def remover_aluno_turma(turma_id, aluno_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM matricula WHERE aluno_id = ? AND turma_id = ?', (aluno_id, turma_id))
    conn.commit()
    conn.close()
    flash('Aluno removido da turma.', 'info')
    return redirect(url_for('detalhes_turma', turma_id=turma_id))

# ===============================================
# ROTAS PARA GERENCIAMENTO DE AVISOS (INCREMENTO 3)
# ===============================================

@app.route('/avisos', methods=('GET', 'POST'))
@role_required('gestor')
def gerenciar_avisos():
    conn = get_db_connection()

    if request.method == 'POST':
        titulo = request.form['titulo']
        conteudo = request.form['conteudo']
        gestor_id = session['user_id']

        if not titulo or not conteudo:
            flash('Título e conteúdo são obrigatórios.', 'danger')
        else:
            conn.execute('INSERT INTO aviso (titulo, conteudo, gestor_id) VALUES (?, ?, ?)',
                         (titulo, conteudo, gestor_id))
            conn.commit()
            flash('Aviso publicado com sucesso!', 'success')
        
        return redirect(url_for('gerenciar_avisos'))

   # Se for GET, busca todos os avisos para listar na página
    avisos_db = conn.execute('SELECT * FROM aviso ORDER BY data_publicacao DESC').fetchall()
    conn.close()

    # Converte a string de data do banco em um objeto datetime do Python
    avisos_formatados = []
    for aviso in avisos_db:
        aviso_dict = dict(aviso) # Converte a linha do banco (Row) para um dicionário
        # Converte a string para um objeto datetime
        aviso_dict['data_publicacao'] = datetime.strptime(aviso_dict['data_publicacao'], '%Y-%m-%d %H:%M:%S')
        avisos_formatados.append(aviso_dict)

    return render_template('avisos.html', avisos=avisos_formatados)



@app.route('/aviso/<int:aviso_id>/remover')
@role_required('gestor')
def remover_aviso(aviso_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM aviso WHERE id = ?', (aviso_id,))
    conn.commit()
    conn.close()
    flash('Aviso removido com sucesso.', 'info')
    return redirect(url_for('gerenciar_avisos'))





if __name__ == '__main__':
    app.run(debug=True)
