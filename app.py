from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
# secret_key é obrigatória para usar 'session' no Flask. Ela criptografa os cookies do usuário.
app.secret_key = 'chave_super_secreta_organizador' 

# Função para garantir que o banco e as tabelas existem
def inicializar_banco():
    conexao = sqlite3.connect('historico_estudos.db')
    cursor = conexao.cursor()
    
    # 1. Cria a Tabela de Usuários (A que estava faltando!)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL
        )
    ''')

    # 2. Cria a Tabela de Estudos
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


# Função auxiliar para conectar no banco mais fácil
def conectar_banco():
    conexao = sqlite3.connect('historico_estudos.db')
    conexao.row_factory = sqlite3.Row # Permite acessar as colunas pelo nome (ex: linha['materia'])
    return conexao

# ROTAS DE AUTENTICAÇÃO (LOGIN E CADASTRO)
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        
        # Criptografando a senha antes de salvar!
        senha_hash = generate_password_hash(senha)

        conexao = conectar_banco()
        cursor = conexao.cursor()
        try:
            # Tenta inserir. Se o e-mail já existir, vai dar erro pois marcamos como UNIQUE na tabela
            cursor.execute("INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)", (nome, email, senha_hash))
            conexao.commit()
            return redirect('/login')
        except sqlite3.IntegrityError:
            # Se der erro de integridade, é porque o e-mail já está em uso
            return render_template('cadastro.html', erro="E-mail já cadastrado!")
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
        cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        usuario = cursor.fetchone()
        conexao.close()

        # Verifica se o usuário existe E se a senha digitada bate com o hash salvo
        if usuario and check_password_hash(usuario['senha'], senha):
            # Cria a sessão do usuário (o "crachá" virtual)
            session['usuario_id'] = usuario['id']
            session['usuario_nome'] = usuario['nome']
            return redirect('/')
        else:
            return render_template('login.html', erro="E-mail ou senha incorretos.")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear() # Rasga o "crachá" e encerra a sessão
    return redirect('/login')

# ==========================================
# ROTAS DO SISTEMA PROTEGIDAS
# ==========================================

@app.route('/')
def index():
    if 'usuario_id' not in session:
        return redirect('/login')

    usuario_id = session['usuario_id']
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    # 1. Busca os estudos para a tabela
    cursor.execute("SELECT * FROM estudos WHERE usuario_id = ? ORDER BY id DESC", (usuario_id,))
    estudos = cursor.fetchall()
    
    # 2. Soma o total geral de minutos
    cursor.execute("SELECT SUM(tempo) FROM estudos WHERE usuario_id = ?", (usuario_id,))
    resultado = cursor.fetchone()[0]
    total_minutos = resultado if resultado else 0 

    # 3. NOVO: Agrupa o tempo por categoria para o gráfico
    cursor.execute('''
        SELECT categoria, SUM(tempo) as total_categoria 
        FROM estudos 
        WHERE usuario_id = ? 
        GROUP BY categoria
    ''', (usuario_id,))
    dados_grafico = cursor.fetchall()
    
    # Transforma o resultado do banco num dicionário do Python (ex: {'Teoria': 120, 'Prática': 90})
    resumo_categorias = {}
    for linha in dados_grafico:
        resumo_categorias[linha['categoria']] = linha['total_categoria']
    
    conexao.close()
    
    # Adicionamos a variável resumo_categorias no render_template
    return render_template('index.html', 
                           estudos=estudos, 
                           total_minutos=total_minutos, 
                           nome_usuario=session.get('usuario_nome'),
                           resumo_categorias=resumo_categorias)

@app.route('/adicionar', methods=['POST'])
def adicionar():
    if 'usuario_id' not in session:
        return redirect('/login')

    materia = request.form['materia']
    tempo = request.form['tempo']
    categoria = request.form['categoria']
    usuario_id = session['usuario_id'] # Descobre quem está logado para vincular

    conexao = conectar_banco()
    cursor = conexao.cursor()
    # Adicionamos a coluna usuario_id no INSERT
    cursor.execute("INSERT INTO estudos (usuario_id, materia, tempo, categoria) VALUES (?, ?, ?, ?)", 
                   (usuario_id, materia, tempo, categoria))
    conexao.commit()
    conexao.close()

    return redirect('/')

# Rota para editar um estudo específico
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    # 1. Segurança na porta
    if 'usuario_id' not in session:
        return redirect('/login')

    usuario_id = session['usuario_id']
    conexao = conectar_banco()
    cursor = conexao.cursor()

    if request.method == 'POST':
        nova_materia = request.form['materia']
        novo_tempo = request.form['tempo']
        nova_categoria = request.form['categoria']

        # 2. Segurança no UPDATE: Atualiza apenas se o ID e o dono baterem
        cursor.execute('''
            UPDATE estudos 
            SET materia = ?, tempo = ?, categoria = ? 
            WHERE id = ? AND usuario_id = ?
        ''', (nova_materia, novo_tempo, nova_categoria, id, usuario_id))
        
        conexao.commit()
        conexao.close()
        return redirect('/')
        
    else:
        # Busca os dados para preencher o formulário, garantindo que seja do dono
        cursor.execute("SELECT * FROM estudos WHERE id = ? AND usuario_id = ?", (id, usuario_id))
        estudo = cursor.fetchone()
        conexao.close()
        
        # 3. Se o estudo não for encontrado (ou for de outra pessoa), chuta de volta pro início
        if estudo is None:
            return redirect('/')
            
        return render_template('editar.html', estudo=estudo)

# Rota para deletar um estudo específico pelo ID
@app.route('/deletar/<int:id>')
def deletar(id):
    # 1. Segurança na porta
    if 'usuario_id' not in session:
        return redirect('/login')

    usuario_id = session['usuario_id'] # Pega quem está logado

    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    # 2. Segurança no Banco: Apaga onde o ID do estudo bate AND o ID do dono bate
    cursor.execute("DELETE FROM estudos WHERE id = ? AND usuario_id = ?", (id, usuario_id))
    
    conexao.commit()
    conexao.close()
    
    return redirect('/')

if __name__ == '__main__':
    inicializar_banco() # Cria o banco na primeira vez que rodar
    app.run(debug=True)