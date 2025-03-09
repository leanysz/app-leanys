from main import app
from funtions import obter_questao
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'  # O banco de dados será criado como 'usuarios.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'chave_secreta'
db = SQLAlchemy(app)

#consulta ao banco de datos
'''resultado = db.session.execute(
        text('SELECT * FROM usuarios WHERE usuario = :usuario'), 
        {'usuario': usuario}).fetchone()
    
    print(resultado)'''

class Usuario(db.Model):
    __tablename__ = 'usuarios' 
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    pontuacao = db.Column(db.Integer, default=0)
    acertos_consecutivos = db.Column(db.Integer, default=0)  
    erros_consecutivos = db.Column(db.Integer, default=0)  


    def __repr__(self):
        return f"<Usuario {self.usuario}>"
    
with app.app_context():
    db.create_all()


# rotas 

@app.route('/atualizar-pontuacao', methods=['POST'])
def atualizar_pontuacao():
    dados = request.get_json()
    acertou = dados.get('acertou')
    if 'user' in session:
        usuario = session['user']  # Obtém o usuário da sessão
    
    #buscando id do usuario 

    id = db.session.execute(
        text('SELECT id FROM usuarios WHERE usuario = :usuario'),
        {'usuario': usuario}  # Passando o parâmetro de forma segura
    ).fetchone()[0]

    # buacando a pontuaçao do usuario 

    pontuacao = db.session.execute(
        text('SELECT pontuacao FROM usuarios WHERE usuario = :usuario'),
        {'usuario': usuario}  # Passando o parâmetro de forma segura
    ).fetchone()[0]

    # buacando os acertos do usuario 

    acertos_consecutivos = db.session.execute(
        text('SELECT acertos_consecutivos FROM usuarios WHERE usuario = :usuario'),
        {'usuario': usuario}  # Passando o parâmetro de forma segura
    ).fetchone()[0]

    # buacando os erros do usuario 

    erros_consecutivos = db.session.execute(
        text('SELECT erros_consecutivos FROM usuarios WHERE usuario = :usuario'),
        {'usuario': usuario}  # Passando o parâmetro de forma segura
    ).fetchone()[0]

    # Lógica de pontuação

    if acertou:

        # Lógica de pontuação para acertos consecutivos

        if acertos_consecutivos == 0:
            pontuacao = pontuacao + 10

        elif acertos_consecutivos == 1:
            pontuacao = pontuacao + 15
            
        elif acertos_consecutivos >=2:
            pontuacao = pontuacao + 20

        acertos_consecutivos += 1
        erros_consecutivos = 0

    else:
        
        # Lógica de pontuação para erros consecutivos

        if erros_consecutivos == 0:
            pontuacao = max(pontuacao - 5, 0)
        
        elif erros_consecutivos == 1:
            pontuacao = max(pontuacao - 10, 0)

        elif erros_consecutivos>=2:
            pontuacao = max(pontuacao - 15, 0)

        acertos_consecutivos = 0
        erros_consecutivos += 1


    # Salvando as novas informações no banco
    db.session.execute(
        text('UPDATE usuarios SET pontuacao = :pontuacao, acertos_consecutivos = :acertos, erros_consecutivos = :erros WHERE id = :id'),
        {'pontuacao': pontuacao, 'acertos': acertos_consecutivos, 'erros': erros_consecutivos, 'id': id}
    )

    db.session.commit()
    return {'status': 'success', 'pontuacao': pontuacao,}

@app.route('/header')
def header():
    usuario_logado = session.get('user')
    usuario = db.session.query(Usuario).filter_by(usuario=usuario_logado).first()
    if usuario:  
        pontuacao = usuario.pontuacao  # Pega a pontuação do usuário
    else:
        pontuacao = 0 
    return render_template("header.html", usuario=usuario, pontuacao=pontuacao)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']
        user = Usuario.query.filter_by(usuario=usuario).first()

        if user and check_password_hash(user.senha, senha):
            session['user'] = usuario
            return redirect(url_for('homepage'))  # Redireciona para a homepage
        else:
            flash('Usuário ou senha incorretos. Tente novamente!')
            return redirect(url_for('login'))
    return render_template("login.html")

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']
        senha_confirmacao = request.form['senha_confirmacao']
        
        if senha != senha_confirmacao:
            flash('As senhas não coincidem. Tente novamente!')
            return redirect(url_for('registro'))
        
        if Usuario.query.filter_by(usuario=usuario).first():
            flash('usuario já está em uso. Escolha outro.')
            return redirect(url_for('registro'))
        
        hash_senha = generate_password_hash(senha)
        novo_usuario = Usuario(usuario=usuario, senha=hash_senha)
        db.session.add(novo_usuario)
        db.session.commit()
        flash('Conta criada com sucesso! Agora você pode fazer login.')
        return redirect(url_for('login'))
    
    return render_template('registro.html')

@app.route('/logout')
def logout():
    session.pop('user', None)  # Remove o usuário da sessão
    return redirect(url_for('login'))

@app.route("/")
def homepage():
    usuario_logado = session.get('user')
    usuario = db.session.query(Usuario).filter_by(usuario=usuario_logado).first()
    return render_template("homepage.html" , usuario=usuario)

@app.route("/ranking.html")
def ranking():
    # Obtenha o usuário logado
    usuario_logado = session.get('user')
    usuario = db.session.query(Usuario).filter_by(usuario=usuario_logado).first()
    
    if usuario:  
        pontuacao = usuario.pontuacao  # Pega a pontuação do usuário
    else:
        pontuacao = 0
    
    # Obtenha todos os usuários e ordene pela pontuação em ordem crescente
    ranking = db.session.query(Usuario).order_by(Usuario.pontuacao.desc(),Usuario.usuario.asc()).all()
    
    return render_template('ranking.html', ranking=ranking, pontuacao=pontuacao)


@app.route("/contato.html")
def contato():
    return render_template("contato.html")

# inicio

@app.route("/linguagens.html")
def linguegns():
    return render_template("inicio/linguagens.html")

@app.route("/humanas.html")
def humanas():
    return render_template("inicio/humanas.html")

@app.route("/natureza.html")
def natureza():
    return render_template("inicio/natureza.html")

@app.route("/matematica.html")
def matematica():
    return render_template("inicio/matematica.html")

@app.route("/redacao.html")
def redacao():
    return render_template("inicio/redacao.html")

#linguagens

@app.route("/portugues.html")
def portugues():
    return render_template("linguagens/portugues.html")

@app.route("/literatura.html")
def literatura():
    questao = obter_questao("matematica")
    return render_template("linguagens/literatura.html",  questao=questao)

@app.route("/espanhol.html")
def espanhol():
    questao = obter_questao("matematica")
    return render_template("linguagens/espanhol.html", questao=questao)

@app.route("/ingles.html", methods=['GET', 'POST'])
def ingles():
    questao = obter_questao("matematica")
    return render_template("linguagens/ingles.html", questao=questao)

@app.route("/questoes-linguagens.html")
def questoes_l():
    return render_template("linguagens/questoes-l.html")

# humanas

@app.route("/historia.html")
def historia():
    return render_template("humanas/historia.html")

@app.route("/geografia.html")
def geografia():
    return render_template("humanas/geografia.html")

@app.route("/filosofia.html")
def filosofia():
    return render_template("humanas/filosofia.html")

@app.route("/sociologia.html")
def sociologia():
    return render_template("humanas/sociologia.html")

@app.route("/questoes-humanas.html")
def questoes_h():
    return render_template("humanas/questoes-h.html")

# naturezas

@app.route("/biologia.html")
def biologia():
    return render_template("naturezas/biologia.html")

@app.route("/quimica.html")
def quimica():
    return render_template("naturezas/quimica.html")

@app.route("/fisica.html")
def fisica():
    return render_template("naturezas/fisica.html")

@app.route("/questoes-naturezas.html")
def questoes_n():
    return render_template("naturezas/questoes-n.html")

# matematica

@app.route("/questoes-matematica.html")
def questoes_m():
    questao = obter_questao("matematica")
    return render_template("matematica/questoes-m.html", questao=questao)

    

