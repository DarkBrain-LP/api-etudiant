from crypt import methods
from pydoc import render_doc
from time import clock_settime
from urllib.parse import quote_plus
from flask import Flask, app, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
password = quote_plus('emmanuel')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:{}@localhost:5432/app_1'.format(
    password)
# permet de refuser mes warning dans le code sur le serveur flask
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Etudiant(db.Model):
    __tablename__ = 'etudiants'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    adresse = db.Column(db.String(100), nullable=True)


db.create_all()

# Liste de tous les étudiants


@app.route('/')  # route
def get_all_students():  # controleur
    liste_etudiants = Etudiant.query.all()
    return render_template('index.html', data=liste_etudiants)


@app.route('/create')
def print_form_creat():
    return render_template('create.html')


# /add sera utilisé en POST, d'apres le formulaire. Il faut donc le dire
@app.route('/add', methods=['POST', 'GET'])
def add_from_form():

    try:
        if request.method == 'GET':
            return render_template('create.html')
        elif request.method == 'POST':
            # Recupération des elements du formulaires
            nom = request.form.get('nom')
            prenom = request.form.get('prenom')
            adresse = request.form.get('adresse')

            # Création de l'instance à ajouter
            etudiant = Etudiant(nom=nom, prenom=prenom, adresse=adresse)
            db.session.add(etudiant)
            db.session.commit()

            return redirect(url_for('get_all_students'))
    except:
        db.session.rollback
    finally:
        db.session.close

    return '<script>Alert("Vous etes enregistré avec succes")</script>'
