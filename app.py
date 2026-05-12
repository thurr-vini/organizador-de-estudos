from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import psycopg2
import psycopg2.extras


app = Flask(__name__)

# Chave obrigatória para usar session no Flask.
app.secret_key = 'chave_super_secreta_organizador'


# ==========================================
# CONFIGURAÇÃO DO BANCO
# ==========================================

def conectar_banco():
    database_url = os.environ.get('DATABASE_URL')

    # No Render, usa PostgreSQL
    if database_url:
        return psycopg2.connect(
            database_url,
            cursor_factory=psycopg2.extras.DictCursor
        )

    # No seu PC, usa SQLite
    conexao = sqlite3.connect('historico_estudos.db')
    conexao.row_factory = sqlite3.Row
    return conexao


def executar(cursor, sql, parametros=()):
    """
    Essa função adapta os comandos SQL:
    - SQLite usa ?
    - PostgreSQL usa %s
    """
    if os.environ.get('DATABASE_URL'):
        sql = sql.replace('?', '%s')

    cursor.execute(sql, parametros)


def inicializar_banco():
    conexao = conectar_banco()
    cursor = conexao.cursor()

    # Se estiver no Render/PostgreSQL
    if os.environ.get('DATABASE_URL'):
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                admin INTEGER DEFAULT 0
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS estudos (
                id SERIAL PRIMARY KEY,
                usuario_id INTEGER NOT NULL,
                materia TEXT NOT NULL,
                tempo INTEGER NOT NULL,
                categoria TEXT NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
        ''')

    # Se estiver no seu PC/SQLite
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                admin INTEGER DEFAULT 0
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS estudos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                materia TEXT NOT NULL,
                tempo INTEGER NOT NULL,
                categoria TEXT NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
        ''')

    conexao.commit()
    conexao.close()


inicializar_banco()


# ==========================================
# ROTAS DE AUTENTICAÇÃO
# ==========================================

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        senha_hash = generate_password_hash(senha)

        conexao = conectar_banco()
        cursor = conexao.cursor()

        try:
            # O primeiro usuário cadastrado será administrador
            executar(cursor, "SELECT COUNT(*) as total FROM usuarios")
            total_usuarios = cursor.fetchone()['total']

            admin = 1 if total_usuarios == 0 else 0

            executar(
                cursor,
                "INSERT INTO usuarios (nome, email, senha, admin) VALUES (?, ?, ?, ?)",
                (nome, email, senha_hash, admin)
            )

            conexao.commit()
            return redirect('/login')

        except Exception:
            conexao.rollback()
            return render_template('cadastro.html', erro="E-mail já cadastrado ou erro no cadastro.")

        finally:
            conexao.close()

    return render_template('cadastro.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        conexao = conectar_banco()
        cursor = conexao.cursor()

        executar(cursor, "SELECT * FROM usuarios WHERE email = ?", (email,))
        usuario = cursor.fetchone()

        conexao.close()

        if usuario and check_password_hash(usuario['senha'], senha):
            session['usuario_id'] = usuario['id']
            session['usuario_nome'] = usuario['nome']
            session['admin'] = usuario['admin']

            return redirect('/')

        return render_template('login.html', erro="E-mail ou senha incorretos.")

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# ==========================================
# ROTAS DO SISTEMA
# ==========================================

@app.route('/')
def index():
    if 'usuario_id' not in session:
        return redirect('/login')

    usuario_id = session['usuario_id']

    conexao = conectar_banco()
    cursor = conexao.cursor()

    executar(
        cursor,
        "SELECT * FROM estudos WHERE usuario_id = ? ORDER BY id DESC",
        (usuario_id,)
    )
    estudos = cursor.fetchall()

    executar(
        cursor,
        "SELECT SUM(tempo) as total FROM estudos WHERE usuario_id = ?",
        (usuario_id,)
    )
    resultado = cursor.fetchone()['total']
    total_minutos = resultado if resultado else 0

    executar(
        cursor,
        '''
        SELECT categoria, SUM(tempo) as total_categoria
        FROM estudos
        WHERE usuario_id = ?
        GROUP BY categoria
        ''',
        (usuario_id,)
    )
    dados_grafico = cursor.fetchall()

    resumo_categorias = {}
    for linha in dados_grafico:
        resumo_categorias[linha['categoria']] = linha['total_categoria']

    conexao.close()

    return render_template(
        'index.html',
        estudos=estudos,
        total_minutos=total_minutos,
        nome_usuario=session.get('usuario_nome'),
        resumo_categorias=resumo_categorias
    )


@app.route('/adicionar', methods=['POST'])
def adicionar():
    if 'usuario_id' not in session:
        return redirect('/login')

    materia = request.form['materia']
    tempo = request.form['tempo']
    categoria = request.form['categoria']
    usuario_id = session['usuario_id']

    conexao = conectar_banco()
    cursor = conexao.cursor()

    executar(
        cursor,
        "INSERT INTO estudos (usuario_id, materia, tempo, categoria) VALUES (?, ?, ?, ?)",
        (usuario_id, materia, tempo, categoria)
    )

    conexao.commit()
    conexao.close()

    return redirect('/')


@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    if 'usuario_id' not in session:
        return redirect('/login')

    usuario_id = session['usuario_id']

    conexao = conectar_banco()
    cursor = conexao.cursor()

    if request.method == 'POST':
        nova_materia = request.form['materia']
        novo_tempo = request.form['tempo']
        nova_categoria = request.form['categoria']

        executar(
            cursor,
            '''
            UPDATE estudos
            SET materia = ?, tempo = ?, categoria = ?
            WHERE id = ? AND usuario_id = ?
            ''',
            (nova_materia, novo_tempo, nova_categoria, id, usuario_id)
        )

        conexao.commit()
        conexao.close()

        return redirect('/')

    executar(
        cursor,
        "SELECT * FROM estudos WHERE id = ? AND usuario_id = ?",
        (id, usuario_id)
    )
    estudo = cursor.fetchone()

    conexao.close()

    if estudo is None:
        return redirect('/')

    return render_template('editar.html', estudo=estudo)


@app.route('/deletar/<int:id>')
def deletar(id):
    if 'usuario_id' not in session:
        return redirect('/login')

    usuario_id = session['usuario_id']

    conexao = conectar_banco()
    cursor = conexao.cursor()

    executar(
        cursor,
        "DELETE FROM estudos WHERE id = ? AND usuario_id = ?",
        (id, usuario_id)
    )

    conexao.commit()
    conexao.close()

    return redirect('/')


# ==========================================
# ÁREA ADMIN
# ==========================================

@app.route('/admin/usuarios')
def admin_usuarios():
    if 'usuario_id' not in session or session.get('admin') != 1:
        return redirect('/')

    conexao = conectar_banco()
    cursor = conexao.cursor()

    executar(
        cursor,
        '''
        SELECT 
            usuarios.id,
            usuarios.nome,
            usuarios.email,
            COUNT(estudos.id) as total_estudos
        FROM usuarios
        LEFT JOIN estudos ON estudos.usuario_id = usuarios.id
        GROUP BY usuarios.id, usuarios.nome, usuarios.email
        ORDER BY usuarios.id DESC
        '''
    )

    usuarios = cursor.fetchall()
    conexao.close()

    html = '''
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Usuários cadastrados</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                padding: 30px;
                background: #f5f5f5;
            }

            h1 {
                color: #111827;
            }

            table {
                width: 100%;
                border-collapse: collapse;
                background: white;
            }

            th, td {
                padding: 12px;
                border: 1px solid #ddd;
                text-align: left;
            }

            th {
                background: #2563eb;
                color: white;
            }

            a {
                display: inline-block;
                margin-top: 20px;
                color: #2563eb;
                text-decoration: none;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <h1>Usuários cadastrados</h1>

        <table>
            <tr>
                <th>ID</th>
                <th>Nome</th>
                <th>E-mail</th>
                <th>Total de estudos</th>
            </tr>
    '''

    for usuario in usuarios:
        html += f'''
            <tr>
                <td>{usuario['id']}</td>
                <td>{usuario['nome']}</td>
                <td>{usuario['email']}</td>
                <td>{usuario['total_estudos']}</td>
            </tr>
        '''

    html += '''
        </table>

        <a href="/">Voltar ao painel</a>
    </body>
    </html>
    '''

    return html


if __name__ == '__main__':
    app.run(debug=True)