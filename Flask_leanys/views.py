from main import app
from flask import render_template

# rotas 

@app.route("/")
def homepage():
    return render_template("homepage.html")

@app.route("/sobre.html")
def sobre():
    return render_template("sobre.html")

@app.route("/contato.html")
def contato():
    return render_template("contato.html")

