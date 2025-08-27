import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime, date
from functools import wraps
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import re


app = Flask(__name__)

app.secret_key = 'chave_segura'  # Necessário para usar sessões

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'beatrizzaraujo0203@gmail.com' # SEU EMAIL AQUI
app.config['MAIL_PASSWORD'] = 'flpbmmkrbmgprmnb'     # SUA SENHA AQUI
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# Configuração do Serializer para gerar tokens seguros
serializer = URLSafeTimedSerializer(app.secret_key)

def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                flash("Você precisa estar logado para acessar esta página.", "warning")
                return redirect(url_for("login"))
            
            user_role = session.get("user_type") # Usar user_type conforme definido no login
            if user_role not in allowed_roles:
                flash("Você não tem permissão para acessar esta página.", "danger")
                
                if user_role == "gestor":
                    return redirect(url_for("index"))
                elif user_role == "professor":
                    if "user_id" in session:
                        return redirect(url_for("professor_dashboard", professor_id=session["user_id"]))
                    else:
                        return redirect(url_for("login"))
                elif user_role == "aluno" or user_role == "responsavel":
                    if "user_id" in session:
                        return redirect(url_for("aluno_dashboard"))
                    else:
                        return redirect(url_for("login"))
                else:
                    return redirect(url_for("login"))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def get_db_connection():
    """Cria uma conexão com o banco de dados."""
    conn = sqlite3.connect('escola.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
@role_required('gestor')
def index():
    """Página inicial - Dashboard do Gestor."""
    conn = get_db_connection()
    
    stats = {
        'alunos': conn.execute("SELECT COUNT(id) FROM usuario WHERE tipo_usuario = 'aluno'").fetchone()[0],
        'professores': conn.execute("SELECT COUNT(id) FROM usuario WHERE tipo_usuario = 'professor'").fetchone()[0],
        'responsaveis': conn.execute("SELECT COUNT(id) FROM usuario WHERE tipo_usuario = 'responsavel'").fetchone()[0],
        'disciplinas': conn.execute('SELECT COUNT(id) FROM disciplina').fetchone()[0]
    }
    
    # Busca os avisos do banco de dados
    avisos_db = conn.execute('SELECT id, titulo, data_publicacao FROM aviso ORDER BY data_publicacao DESC LIMIT 4').fetchall()
    
    # --- CORREÇÃO APLICADA AQUI ---
    # Converte a data de string para um objeto datetime
    avisos_formatados = []
    for aviso in avisos_db:
        aviso_dict = dict(aviso)  # Transforma o resultado em um dicionário editável
        # Converte a string da data para um objeto datetime do Python
        aviso_dict['data_publicacao'] = datetime.strptime(aviso_dict['data_publicacao'], '%Y-%m-%d %H:%M:%S')
        avisos_formatados.append(aviso_dict)

    conn.close()
    
    # Envia a lista de avisos com as datas já convertidas
    return render_template('index.html', stats=stats, avisos=avisos_formatados)

@app.route('/usuarios', methods=('GET', 'POST'))
@role_required('gestor')
def usuarios():
    conn = get_db_connection()

    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        tipo_usuario = request.form['tipo_usuario']

        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        
        if not email_pattern.match(email):
            flash('Formato de email inválido. Por favor, verifique e tente novamente.', 'danger')
            conn.close()
            return redirect(url_for('usuarios'))

        email_existente = conn.execute('SELECT id FROM usuario WHERE email = ?', (email,)).fetchone()
        
        if email_existente:
            flash('Este endereço de email já está cadastrado.', 'danger')
            conn.close()
            return redirect(url_for('usuarios'))

        conn.execute('INSERT INTO usuario (nome, email, senha, tipo_usuario) VALUES (?, ?, ?, ?)',
                     (nome, email, senha, tipo_usuario))
        conn.commit()
        flash('Usuário cadastrado com sucesso!', 'success')
        
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
            # A linha "senha = request.form['senha']" foi removida.
            
            # ... (a validação de e-mail que você tem continua aqui) ...

            # A lógica "if senha:" foi removida. Agora temos apenas uma consulta UPDATE.
            conn.execute('UPDATE usuario SET nome = ?, email = ?, tipo_usuario = ? WHERE id = ?',
                         (nome, email, tipo_usuario, usuario_id))
            
            conn.commit()
            flash('Usuário atualizado com sucesso!', 'success')
            return redirect(url_for('editar_usuario', usuario_id=usuario_id))

    filhos_associados = []
    outros_alunos = []
    if usuario['tipo_usuario'] == 'responsavel':
        # Busca os filhos que JÁ ESTÃO associados a este responsável
        filhos_associados = conn.execute('''
            SELECT u.id, u.nome FROM usuario u 
            JOIN responsavel_aluno ra ON u.id = ra.aluno_id 
            WHERE ra.responsavel_id = ?
        ''', (usuario_id,)).fetchall()

        # --- CORREÇÃO APLICADA AQUI ---
        # Busca alunos que ainda NÃO TÊM NENHUM responsável associado
        outros_alunos = conn.execute('''
            SELECT id, nome FROM usuario 
            WHERE tipo_usuario = "aluno" AND id NOT IN (
                SELECT aluno_id FROM responsavel_aluno
            )
        ''').fetchall()

    conn.close()
    return render_template('editar_usuario.html', 
                           usuario=usuario, 
                           filhos_associados=filhos_associados, 
                           outros_alunos=outros_alunos)


@app.route('/usuario/<int:usuario_id>/remover')
@role_required('gestor')
def remover_usuario(usuario_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM usuario WHERE id = ?', (usuario_id,))
    conn.commit()
    conn.close()
    flash('Usuário removido com sucesso.', 'info')
    return redirect(url_for('usuarios'))


@app.route('/responsavel/<int:responsavel_id>/adicionar_aluno', methods=['POST'])
@role_required('gestor')
def adicionar_associacao_responsavel(responsavel_id):
    aluno_id = request.form.get('aluno_id')
    if aluno_id:
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO responsavel_aluno (responsavel_id, aluno_id) VALUES (?, ?)',
                         (responsavel_id, aluno_id))
            conn.commit()
            flash('Aluno associado com sucesso!', 'success')
        except conn.IntegrityError:
            flash('Esta associação já existe.', 'warning')
        finally:
            conn.close()
    return redirect(url_for('editar_usuario', usuario_id=responsavel_id))


@app.route('/responsavel/<int:responsavel_id>/remover_aluno/<int:aluno_id>')
@role_required('gestor')
def remover_associacao_responsavel(responsavel_id, aluno_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM responsavel_aluno WHERE responsavel_id = ? AND aluno_id = ?',
                 (responsavel_id, aluno_id))
    conn.commit()
    conn.close()
    flash('Associação removida com sucesso.', 'info')
    return redirect(url_for('editar_usuario', usuario_id=responsavel_id))


@app.route('/meu_perfil', methods=['GET', 'POST'])
@role_required('gestor', 'professor', 'aluno', 'responsavel') # Permite todos os tipos de usuário logados
def meu_perfil():
    user_id = session.get('user_id')
    conn = get_db_connection()
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        # Pega o email atual para verificação
        usuario_atual = conn.execute('SELECT email FROM usuario WHERE id = ?', (user_id,)).fetchone()

        # Verifica se o novo e-mail já está em uso por OUTRO usuário
        if email != usuario_atual['email']:
            email_existente = conn.execute('SELECT id FROM usuario WHERE email = ?', (email,)).fetchone()
            if email_existente:
                flash('O novo endereço de e-mail já está em uso por outro usuário.', 'danger')
                return redirect(url_for('meu_perfil'))

        # Se o campo senha foi preenchido, atualiza a senha
        if senha:
            conn.execute('UPDATE usuario SET nome = ?, email = ?, senha = ? WHERE id = ?',
                         (nome, email, senha, user_id))
        else: # Senão, atualiza tudo menos a senha
            conn.execute('UPDATE usuario SET nome = ?, email = ? WHERE id = ?',
                         (nome, email, user_id))
        
        conn.commit()
        
        # Atualiza o nome na sessão para que a navbar mostre o nome novo imediatamente
        session['user_name'] = nome
        
        flash('Seu perfil foi atualizado com sucesso!', 'success')
        return redirect(url_for('meu_perfil'))

    # Se for um GET, apenas busca os dados e exibe a página
    usuario = conn.execute('SELECT * FROM usuario WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return render_template('meu_perfil.html', usuario=usuario)


# ===================================================================
# (REFATORADO) ROTAS PARA GERENCIAMENTO DE DISCIPLINAS
# ===================================================================

@app.route('/disciplinas', methods=('GET', 'POST'))
@role_required('gestor')
def disciplinas():
    conn = get_db_connection()
    if request.method == 'POST':
        nome = request.form['nome']
        ano = request.form['ano']
        periodo = request.form['periodo']

        if not nome or not ano:
            flash('Nome e Ano são campos obrigatórios!', 'danger')
        else:
            conn.execute('INSERT INTO disciplina (nome, ano, periodo) VALUES (?, ?, ?)',
                         (nome, ano, periodo))
            conn.commit()
            flash('Disciplina criada com sucesso!', 'success')
            return redirect(url_for('disciplinas'))

    lista_disciplinas = conn.execute('SELECT * FROM disciplina ORDER BY ano DESC, nome').fetchall()
    conn.close()
    return render_template('disciplinas.html', disciplinas=lista_disciplinas)


@app.route('/disciplina/<int:disciplina_id>')
@role_required('gestor')
def detalhes_disciplina(disciplina_id):
    conn = get_db_connection()
    disciplina = conn.execute('SELECT * FROM disciplina WHERE id = ?', (disciplina_id,)).fetchone()

    professores_associados = conn.execute('''
        SELECT u.id, u.nome FROM usuario u JOIN leciona l ON u.id = l.professor_id
        WHERE l.disciplina_id = ?
    ''', (disciplina_id,)).fetchall()

    alunos_inscritos = conn.execute('''
        SELECT u.id, u.nome FROM usuario u JOIN inscricao i ON u.id = i.aluno_id
        WHERE i.disciplina_id = ?
    ''', (disciplina_id,)).fetchall()

    professores_disponiveis = conn.execute('SELECT id, nome FROM usuario WHERE tipo_usuario = "professor"').fetchall()
    alunos_disponiveis = conn.execute('SELECT id, nome FROM usuario WHERE tipo_usuario = "aluno"').fetchall()

    conn.close()
    return render_template('detalhes_disciplina.html', 
                           disciplina=disciplina,
                           professores_associados=professores_associados,
                           alunos_inscritos=alunos_inscritos,
                           professores_disponiveis=professores_disponiveis,
                           alunos_disponiveis=alunos_disponiveis)


@app.route('/disciplina/<int:disciplina_id>/associar_professor', methods=['POST'])
@role_required('gestor')
def associar_professor(disciplina_id):
    professor_id = request.form.get('professor_id')
    if professor_id:
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO leciona (professor_id, disciplina_id) VALUES (?, ?)', (professor_id, disciplina_id))
            conn.commit()
            flash('Professor associado com sucesso!', 'success')
        except conn.IntegrityError:
            flash('Este professor já está associado a esta disciplina.', 'warning')
        finally:
            conn.close()
    return redirect(url_for('detalhes_disciplina', disciplina_id=disciplina_id))


@app.route('/disciplina/<int:disciplina_id>/inscrever_aluno', methods=['POST'])
@role_required('gestor')
def inscrever_aluno(disciplina_id):
    aluno_id = request.form.get('aluno_id')
    if aluno_id:
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO inscricao (aluno_id, disciplina_id) VALUES (?, ?)', (aluno_id, disciplina_id))
            conn.commit()
            flash('Aluno inscrito com sucesso!', 'success')
        except conn.IntegrityError:
            flash('Este aluno já está inscrito nesta disciplina.', 'warning')
        finally:
            conn.close()
    return redirect(url_for('detalhes_disciplina', disciplina_id=disciplina_id))


@app.route('/disciplina/<int:disciplina_id>/editar', methods=('GET', 'POST'))
@role_required('gestor')
def editar_disciplina(disciplina_id):
    conn = get_db_connection()
    disciplina = conn.execute('SELECT * FROM disciplina WHERE id = ?', (disciplina_id,)).fetchone()

    if request.method == 'POST':
        nome = request.form['nome']
        ano = request.form['ano']
        periodo = request.form['periodo']

        if not nome or not ano:
            flash('Nome e Ano são campos obrigatórios!', 'danger')
        else:
            conn.execute('UPDATE disciplina SET nome = ?, ano = ?, periodo = ? WHERE id = ?',
                         (nome, ano, periodo, disciplina_id))
            conn.commit()
            flash('Disciplina atualizada com sucesso!', 'success')
            return redirect(url_for('disciplinas'))

    conn.close()
    return render_template('editar_disciplina.html', disciplina=disciplina)


@app.route('/disciplina/<int:disciplina_id>/remover')
@role_required('gestor')
def remover_disciplina(disciplina_id):
    conn = get_db_connection()
    try:
        conn.execute('DELETE FROM leciona WHERE disciplina_id = ?', (disciplina_id,))
        conn.execute('DELETE FROM inscricao WHERE disciplina_id = ?', (disciplina_id,))
        conn.execute('DELETE FROM nota WHERE avaliacao_id IN (SELECT id FROM avaliacao WHERE disciplina_id = ?)', (disciplina_id,))
        conn.execute('DELETE FROM avaliacao WHERE disciplina_id = ?', (disciplina_id,))
        conn.execute('DELETE FROM frequencia WHERE disciplina_id = ?', (disciplina_id,))
        conn.execute('DELETE FROM planoaula WHERE disciplina_id = ?', (disciplina_id,))

        conn.execute('DELETE FROM disciplina WHERE id = ?', (disciplina_id,))
        conn.commit()
        flash('Disciplina removida com sucesso.', 'info')
    except Exception as e:
        conn.rollback()
        flash(f'Erro ao remover disciplina: {e}', 'danger')
    finally:
        conn.close()
    return redirect(url_for('disciplinas'))


@app.route('/disciplina/<int:disciplina_id>/remover_professor/<int:professor_id>')
@role_required('gestor')
def remover_associacao_professor(disciplina_id, professor_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM leciona WHERE disciplina_id = ? AND professor_id = ?',
                 (disciplina_id, professor_id))
    conn.commit()
    conn.close()
    flash('Associação de professor removida.', 'info')
    return redirect(url_for('detalhes_disciplina', disciplina_id=disciplina_id))


@app.route('/disciplina/<int:disciplina_id>/remover_aluno/<int:aluno_id>')
@role_required('gestor')
def remover_inscricao_aluno(disciplina_id, aluno_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM inscricao WHERE disciplina_id = ? AND aluno_id = ?',
                 (disciplina_id, aluno_id))
    conn.commit()
    conn.close()
    flash('Inscrição de aluno removida.', 'info')
    return redirect(url_for('detalhes_disciplina', disciplina_id=disciplina_id))


# ===================================================================
# (REFATORADO) ROTAS PARA O DASHBOARD DO PROFESSOR
# ===================================================================

@app.route('/professor/<int:professor_id>')
@role_required('professor')
def professor_dashboard(professor_id):
    conn = get_db_connection()
    
    professor = conn.execute('SELECT * FROM usuario WHERE id = ? AND tipo_usuario = "professor"', 
                             (professor_id,)).fetchone()
    
    if professor is None:
        return "Professor não encontrado", 404

    disciplinas_lecionadas = conn.execute('''
        SELECT d.* FROM disciplina d
        JOIN leciona l ON d.id = l.disciplina_id
        WHERE l.professor_id = ?
    ''', (professor_id,)).fetchall()
    
    avisos_db = conn.execute('SELECT * FROM aviso ORDER BY data_publicacao DESC LIMIT 3').fetchall()
    avisos_formatados = []
    for aviso in avisos_db:
        aviso_dict = dict(aviso)
        aviso_dict['data_publicacao'] = datetime.strptime(aviso_dict['data_publicacao'], '%Y-%m-%d %H:%M:%S')
        avisos_formatados.append(aviso_dict)

    conn.close()
    return render_template('professor_dashboard.html', professor=professor, disciplinas=disciplinas_lecionadas, avisos=avisos_formatados)


# ===================================================================
# (REFATORADO) ROTAS PARA GERENCIAMENTO DE NOTAS (PROFESSOR)
# ===================================================================

@app.route('/disciplina/<int:disciplina_id>/notas')
@role_required('professor')
def gerenciar_notas(disciplina_id):
    conn = get_db_connection()
    
    disciplina = conn.execute('SELECT * FROM disciplina WHERE id = ?', (disciplina_id,)).fetchone()
    
    professor_id = session.get('user_id')
    professor = conn.execute('SELECT * FROM usuario WHERE id = ?', (professor_id,)).fetchone()

    alunos = conn.execute('''
        SELECT u.* FROM usuario u JOIN inscricao i ON u.id = i.aluno_id
        WHERE i.disciplina_id = ? ORDER BY u.nome
    ''', (disciplina_id,)).fetchall()

    avaliacoes = conn.execute('SELECT * FROM avaliacao WHERE disciplina_id = ? ORDER BY id', (disciplina_id,)).fetchall()

    notas_db = conn.execute('SELECT aluno_id, avaliacao_id, valor FROM nota').fetchall()
    notas = {(n['aluno_id'], n['avaliacao_id']): n['valor'] for n in notas_db}

    conn.close()
    
    return render_template('gerenciar_notas.html', disciplina=disciplina, professor=professor, alunos=alunos, avaliacoes=avaliacoes, notas=notas)


@app.route('/disciplina/<int:disciplina_id>/avaliacoes/nova', methods=['POST'])
@role_required('professor')
def criar_avaliacao(disciplina_id):
    nome_avaliacao = request.form['nome_avaliacao']
    
    conn = get_db_connection()
    
    conn.execute('INSERT INTO avaliacao (disciplina_id, titulo, data_avaliacao) VALUES (?, ?, date("now"))',
                 (disciplina_id, nome_avaliacao))
    conn.commit()
    conn.close()
    
    return redirect(url_for('gerenciar_notas', disciplina_id=disciplina_id))


@app.route('/disciplina/<int:disciplina_id>/notas/salvar', methods=['POST'])
@role_required('professor')
def salvar_notas(disciplina_id):
    conn = get_db_connection()
    
    for key, value in request.form.items():
        if key.startswith('nota-') and value:
            parts = key.split('-')
            aluno_id = int(parts[1])
            avaliacao_id = int(parts[2])
            nota_valor = float(value)

            existe = conn.execute('SELECT aluno_id, avaliacao_id FROM nota WHERE aluno_id = ? AND avaliacao_id = ?', 
                                  (aluno_id, avaliacao_id)).fetchone()
            
            if existe:
                conn.execute('UPDATE nota SET valor = ? WHERE aluno_id = ? AND avaliacao_id = ?', (nota_valor, aluno_id, avaliacao_id))
            else:
                conn.execute('INSERT INTO nota (aluno_id, avaliacao_id, valor) VALUES (?, ?, ?)',
                             (aluno_id, avaliacao_id, nota_valor))
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('gerenciar_notas', disciplina_id=disciplina_id))


# ===================================================================
# (REFATORADO) ROTAS PARA GERENCIAMENTO DE FREQUÊNCIA (PROFESSOR)
# ===================================================================

@app.route('/disciplina/<int:disciplina_id>/frequencia', methods=['GET', 'POST'])
@role_required('professor')
def registrar_frequencia(disciplina_id):
    conn = get_db_connection()
    
    disciplina = conn.execute('SELECT * FROM disciplina WHERE id = ?', (disciplina_id,)).fetchone()
    
    professor_id = session.get('user_id')
    professor = conn.execute('SELECT * FROM usuario WHERE id = ?', (professor_id,)).fetchone()

    alunos = conn.execute('''
        SELECT u.* FROM usuario u JOIN inscricao i ON u.id = i.aluno_id
        WHERE i.disciplina_id = ? ORDER BY u.nome
    ''', (disciplina_id,)).fetchall()

    if request.method == 'POST':
        data_selecionada = request.form['data']
    else:
        data_selecionada = request.args.get('data', date.today().isoformat())

    if request.method == 'POST':
        conn.execute('DELETE FROM frequencia WHERE disciplina_id = ? AND data = ?', (disciplina_id, data_selecionada))
        
        for aluno in alunos:
            aluno_id = aluno['id']
            presente = 1 if f'presenca-{aluno_id}' in request.form else 0
            
            conn.execute('INSERT INTO frequencia (data, presente, aluno_id, disciplina_id) VALUES (?, ?, ?, ?)',
                         (data_selecionada, presente, aluno_id, disciplina_id))
        conn.commit()

    registros_db = conn.execute('SELECT aluno_id, presente FROM frequencia WHERE disciplina_id = ? AND data = ?',
                                (disciplina_id, data_selecionada)).fetchall()
    registros_frequencia = {r['aluno_id']: r['presente'] for r in registros_db}
    
    conn.close()

    return render_template('registrar_frequencia.html', 
                           disciplina=disciplina, 
                           professor=professor, 
                           alunos=alunos, 
                           data_selecionada=data_selecionada, 
                           registros_frequencia=registros_frequencia)


# ===================================================================
# (REFATORADO) ROTAS PARA GERENCIAMENTO DE PLANOS DE AULA (PROFESSOR)
# ===================================================================

@app.route('/disciplina/<int:disciplina_id>/planos_aula', methods=['GET', 'POST'])
@role_required('professor')
def planos_aula(disciplina_id):
    conn = get_db_connection()
    disciplina = conn.execute('SELECT * FROM disciplina WHERE id = ?', (disciplina_id,)).fetchone()

    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        data_prevista = request.form['data_prevista']

        if not titulo:
            flash('O título do plano de aula é obrigatório!', 'danger')
        else:
            conn.execute('INSERT INTO PlanoAula (disciplina_id, titulo, descricao, data_prevista) VALUES (?, ?, ?, ?)',
                         (disciplina_id, titulo, descricao, data_prevista))
            conn.commit()
            flash('Plano de aula criado com sucesso!', 'success')
            return redirect(url_for('planos_aula', disciplina_id=disciplina_id))

    lista_planos = conn.execute('SELECT * FROM PlanoAula WHERE disciplina_id = ? ORDER BY data_prevista DESC, titulo',
                                (disciplina_id,)).fetchall()
    conn.close()
    return render_template('planos_aula.html', disciplina=disciplina, planos=lista_planos)


@app.route('/plano_aula/<int:plano_id>/editar', methods=['GET', 'POST'])
@role_required('professor')
def editar_plano_aula(plano_id):
    conn = get_db_connection()
    plano = conn.execute('SELECT * FROM PlanoAula WHERE id = ?', (plano_id,)).fetchone()

    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        data_prevista = request.form['data_prevista']

        if not titulo:
            flash('O título do plano de aula é obrigatório!', 'danger')
        else:
            conn.execute('UPDATE PlanoAula SET titulo = ?, descricao = ?, data_prevista = ? WHERE id = ?',
                         (titulo, descricao, data_prevista, plano_id))
            conn.commit()
            flash('Plano de aula atualizado com sucesso!', 'success')
            return redirect(url_for('planos_aula', disciplina_id=plano['disciplina_id']))

    conn.close()
    return render_template('editar_plano_aula.html', plano=plano)


@app.route('/plano_aula/<int:plano_id>/remover', methods=['POST'])
@role_required('professor')
def remover_plano_aula(plano_id):
    conn = get_db_connection()
    plano = conn.execute('SELECT disciplina_id FROM PlanoAula WHERE id = ?', (plano_id,)).fetchone()
    if plano:
        disciplina_id = plano['disciplina_id']
        conn.execute('DELETE FROM PlanoAula WHERE id = ?', (plano_id,))
        conn.commit()
        flash('Plano de aula removido com sucesso!', 'info')
        conn.close()
        return redirect(url_for('planos_aula', disciplina_id=disciplina_id))
    flash('Plano de aula não encontrado.', 'danger')
    conn.close()
    return redirect(url_for('index'))


# ===================================================================
# (REFATORADO) ROTAS PARA O DASHBOARD DO ALUNO/RESPONSÁVEL
# ===================================================================

@app.route('/aluno_dashboard')
@role_required('aluno', 'responsavel')
def aluno_dashboard():
    conn = get_db_connection()
    user_id = session.get('user_id')
    user_type = session.get('user_type')

    aluno_selecionado_id = None
    alunos_associados = []
    
    if user_type == 'aluno':
        aluno_selecionado_id = user_id
    elif user_type == 'responsavel':
        alunos_associados = conn.execute('''
            SELECT u.id, u.nome FROM usuario u JOIN responsavel_aluno ra ON u.id = ra.aluno_id
            WHERE ra.responsavel_id = ? ORDER BY u.nome
        ''', (user_id,)).fetchall()

        if not alunos_associados:
            flash('Você não tem nenhum aluno associado.', 'warning')
            conn.close()
            return render_template('aluno_dashboard.html', aluno=None, avisos=[], alunos_associados=[])

        aluno_selecionado_id = request.args.get('aluno_id', alunos_associados[0]['id'], type=int)

    aluno = conn.execute('SELECT * FROM usuario WHERE id = ?', (aluno_selecionado_id,)).fetchone()
    
    if not aluno:
        flash('Aluno não encontrado.', 'danger')
        conn.close()
        return redirect(url_for('login'))

    disciplinas_aluno_db = conn.execute('''
        SELECT d.* FROM disciplina d JOIN inscricao i ON d.id = i.disciplina_id
        WHERE i.aluno_id = ? ORDER BY d.nome
    ''', (aluno_selecionado_id,)).fetchall()

    disciplinas_aluno = []
    for disciplina in disciplinas_aluno_db:
        disciplina_id = disciplina['id']
        disciplina_dict = dict(disciplina)
        
        # Lógica de Notas
        notas = conn.execute('SELECT valor FROM nota JOIN avaliacao ON nota.avaliacao_id = avaliacao.id WHERE aluno_id = ? AND disciplina_id = ?', (aluno_selecionado_id, disciplina_id)).fetchall()
        if notas:
            disciplina_dict['media'] = round(sum(n['valor'] for n in notas) / len(notas), 1)
        else:
            disciplina_dict['media'] = None
        
        disciplina_dict['notas_detalhadas'] = conn.execute('''
            SELECT a.titulo as titulo_avaliacao, n.valor as nota, a.data_avaliacao 
            FROM nota n 
            JOIN avaliacao a ON n.avaliacao_id = a.id 
            WHERE n.aluno_id = ? AND a.disciplina_id = ?
            ORDER BY a.data_avaliacao ASC
        ''', (aluno_selecionado_id, disciplina_id)).fetchall()

        # Lógica de Frequência
        frequencia = conn.execute('SELECT presente FROM frequencia WHERE aluno_id = ? AND disciplina_id = ?', (aluno_selecionado_id, disciplina_id)).fetchall()
        if frequencia:
            total_aulas = len(frequencia)
            presencas = sum(f['presente'] for f in frequencia)
            faltas = total_aulas - presencas
            disciplina_dict['percentual_frequencia'] = int((presencas / total_aulas) * 100)
            disciplina_dict['presencas'] = presencas
            disciplina_dict['faltas'] = faltas
        else:
            disciplina_dict['percentual_frequencia'] = 100
            disciplina_dict['presencas'] = 0
            disciplina_dict['faltas'] = 0
        
        # --- CORREÇÃO APLICADA AQUI ---
        # Recria a lista de forma explícita para garantir que a chave 'presente' seja mantida
        frequencia_detalhada_db = conn.execute('SELECT data, presente FROM frequencia WHERE aluno_id = ? AND disciplina_id = ? ORDER BY data DESC', (aluno_selecionado_id, disciplina_id)).fetchall()
        
        lista_frequencia_corrigida = []
        for registro in frequencia_detalhada_db:
            lista_frequencia_corrigida.append({
                'data': datetime.strptime(registro['data'], '%Y-%m-%d').date(),
                'presente': registro['presente']
            })
        disciplina_dict['frequencia_detalhada'] = lista_frequencia_corrigida
        # --- FIM DA CORREÇÃO ---

        disciplinas_aluno.append(disciplina_dict)

    avisos_db = conn.execute('SELECT * FROM aviso ORDER BY data_publicacao DESC LIMIT 3').fetchall()
    avisos_formatados = []
    for aviso in avisos_db:
        aviso_dict = dict(aviso)
        aviso_dict['data_publicacao'] = datetime.strptime(aviso_dict['data_publicacao'], '%Y-%m-%d %H:%M:%S')
        avisos_formatados.append(aviso_dict)

    conn.close()

    return render_template('aluno_dashboard.html', 
                           aluno=aluno, 
                           disciplinas_aluno=disciplinas_aluno, 
                           avisos=avisos_formatados,
                           alunos_associados=alunos_associados)

@app.route('/aluno/<int:aluno_id>/boletim')
@role_required('aluno', 'responsavel')
def boletim_aluno(aluno_id):
    conn = get_db_connection()
    aluno = conn.execute('SELECT * FROM usuario WHERE id = ? AND tipo_usuario = "aluno"', (aluno_id,)).fetchone()
    
    if not aluno:
        flash('Aluno não encontrado.', 'danger')
        conn.close()
        return redirect(url_for('aluno_dashboard'))

    if session.get('user_type') == 'aluno' and session.get('user_id') != aluno_id:
        flash('Você não tem permissão para ver este boletim.', 'danger')
        conn.close()
        return redirect(url_for('aluno_dashboard'))
    elif session.get('user_type') == 'responsavel':
        associacao = conn.execute('SELECT * FROM responsavel_aluno WHERE responsavel_id = ? AND aluno_id = ?',
                                 (session.get('user_id'), aluno_id)).fetchone()
        if not associacao:
            flash('Você não está associado a este aluno.', 'danger')
            conn.close()
            return redirect(url_for('aluno_dashboard'))

    disciplinas_do_aluno = conn.execute('''
        SELECT d.id, d.nome, d.ano, d.periodo FROM disciplina d
        JOIN inscricao i ON d.id = i.disciplina_id
        WHERE i.aluno_id = ?
        ORDER BY d.nome
    ''', (aluno_id,)).fetchall()

    boletim_disciplinas = []
    for disciplina in disciplinas_do_aluno:
        avaliacoes_disciplina = conn.execute('''
            SELECT a.id, a.titulo, a.data_avaliacao, n.valor FROM avaliacao a
            LEFT JOIN nota n ON a.id = n.avaliacao_id AND n.aluno_id = ?
            WHERE a.disciplina_id = ?
            ORDER BY a.data_avaliacao
        ''', (aluno_id, disciplina['id'])).fetchall()

        frequencia_disciplina = conn.execute('''
            SELECT data, presente FROM frequencia
            WHERE aluno_id = ? AND disciplina_id = ?
            ORDER BY data
        ''', (aluno_id, disciplina['id'])).fetchall()

        total_aulas = len(frequencia_disciplina)
        total_presencas = sum(1 for f in frequencia_disciplina if f['presente'] == 1)
        percentual_presenca = (total_presencas / total_aulas * 100) if total_aulas > 0 else 100

        boletim_disciplinas.append({
            'disciplina': disciplina,
            'avaliacoes': avaliacoes_disciplina,
            'frequencia': frequencia_disciplina,
            'total_aulas': total_aulas,
            'total_presencas': total_presencas,
            'percentual_presenca': round(percentual_presenca, 2)
        })

    avisos_db = conn.execute('SELECT * FROM aviso ORDER BY data_publicacao DESC LIMIT 3').fetchall()
    avisos_formatados = []
    for aviso in avisos_db:
        aviso_dict = dict(aviso)
        aviso_dict['data_publicacao'] = datetime.strptime(aviso_dict['data_publicacao'], '%Y-%m-%d %H:%M:%S')
        avisos_formatados.append(aviso_dict)

    conn.close()
    return render_template('boletim_aluno.html', 
                           aluno=aluno, 
                           boletim_disciplinas=boletim_disciplinas, 
                           avisos=avisos_formatados)

# ===================================================================
# ROTAS PARA REDEFINIÇÃO DE SENHA
# ===================================================================

@app.route('/esqueci_senha', methods=['GET', 'POST'])
def esqueci_senha():
    if request.method == 'POST':
        email = request.form.get('email')
        conn = get_db_connection()
        usuario = conn.execute('SELECT * FROM usuario WHERE email = ?', (email,)).fetchone()
        conn.close()

        if usuario:
            # Gera um token seguro com o email do usuário
            token = serializer.dumps(email, salt='email-confirm-salt')
            
            # Cria o link de redefinição
            reset_url = url_for('redefinir_senha_com_token', token=token, _external=True)
            
            # Envia o e-mail
            msg = Message('Redefinição de Senha - Sistema Escolar',
                          sender='SEU_EMAIL@gmail.com', # DEVE SER O MESMO EMAIL DA CONFIGURAÇÃO
                          recipients=[email])
            msg.body = f'Olá! Para redefinir sua senha, clique no link a seguir: {reset_url}\n\nSe você не solicitou isso, por favor ignore este email.'
            mail.send(msg)
            
            flash('Um e-mail de redefinição de senha foi enviado para você.', 'success')
            return redirect(url_for('login'))
        else:
            flash('O endereço de e-mail informado não foi encontrado.', 'danger')

    return render_template('esqueci_senha.html')


@app.route('/redefinir_senha/<token>', methods=['GET', 'POST'])
def redefinir_senha_com_token(token):
    try:
        # Valida o token (expira em 1 hora por padrão)
        email = serializer.loads(token, salt='email-confirm-salt', max_age=3600)
    except SignatureExpired:
        flash('O link de redefinição de senha expirou.', 'danger')
        return redirect(url_for('esqueci_senha'))
    except Exception:
        flash('O link de redefinição de senha é inválido.', 'danger')
        return redirect(url_for('esqueci_senha'))

    if request.method == 'POST':
        nova_senha = request.form.get('nova_senha')
        
        conn = get_db_connection()
        conn.execute('UPDATE usuario SET senha = ? WHERE email = ?', (nova_senha, email))
        conn.commit()
        conn.close()
        
        flash('Sua senha foi redefinida com sucesso! Você já pode fazer login.', 'success')
        return redirect(url_for('login'))

    return render_template('redefinir_senha.html', token=token)


# ===================================================================
# ROTAS DE AUTENTICAÇÃO
# ===================================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['password']
        conn = get_db_connection()
        usuario = conn.execute('SELECT * FROM usuario WHERE email = ? AND senha = ?', (email, senha)).fetchone()
        conn.close()

        if usuario:
            session['user_id'] = usuario['id']
            session['user_name'] = usuario['nome']
            session['user_type'] = usuario['tipo_usuario']
            flash(f'Bem-vindo(a), {usuario["nome"]}!', 'success')
            
            if usuario['tipo_usuario'] == 'gestor':
                return redirect(url_for('index'))
            elif usuario['tipo_usuario'] == 'professor':
                return redirect(url_for('professor_dashboard', professor_id=usuario['id']))
            elif usuario['tipo_usuario'] == 'aluno' or usuario['tipo_usuario'] == 'responsavel':
                return redirect(url_for('aluno_dashboard'))

        else:
            flash('Email ou senha incorretos.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Você foi desconectado(a).', 'info')
    return redirect(url_for('login'))


# ===================================================================
# ROTAS DE AVISOS
# ===================================================================

@app.route('/gerenciar_avisos', methods=['GET', 'POST'])
@role_required('gestor')
def gerenciar_avisos():
    conn = get_db_connection()
    if request.method == 'POST':
        titulo = request.form['titulo']
        conteudo = request.form['conteudo']
        if not titulo or not conteudo:
            flash('Título e conteúdo do aviso são obrigatórios!', 'danger')
        else:
            conn.execute('INSERT INTO aviso (titulo, conteudo) VALUES (?, ?)', (titulo, conteudo))
            conn.commit()
            flash('Aviso publicado com sucesso!', 'success')
            return redirect(url_for('gerenciar_avisos'))

    avisos_db = conn.execute('SELECT * FROM aviso ORDER BY data_publicacao DESC').fetchall()
    avisos_formatados = []
    for aviso in avisos_db:
        aviso_dict = dict(aviso)
        aviso_dict['data_publicacao'] = datetime.strptime(aviso_dict['data_publicacao'], '%Y-%m-%d %H:%M:%S')
        avisos_formatados.append(aviso_dict)

    conn.close()
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

# ===================================================================
# ROTA DE RELATÓRIOS
# ===================================================================

@app.route('/relatorios')
@role_required('gestor')
def relatorios():
    conn = get_db_connection()
    
    # Consulta para calcular a média de notas por disciplina
    dados_grafico = conn.execute('''
        SELECT 
            d.nome,
            AVG(n.valor) as media_notas
        FROM disciplina d
        JOIN avaliacao a ON d.id = a.disciplina_id
        JOIN nota n ON a.id = n.avaliacao_id
        GROUP BY d.nome
        ORDER BY media_notas DESC
    ''').fetchall()
    
    conn.close()
    
    # Prepara os dados para enviar ao JavaScript
    labels = [dado['nome'] for dado in dados_grafico]
    data = [round(dado['media_notas'], 2) for dado in dados_grafico]
    
    return render_template('relatorios.html', labels=labels, data=data)


if __name__ == '__main__':
    app.run(debug=True)
