import os
from crypt import methods
from urllib.parse import quote_plus
from flask import Flask, jsonify, abort, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

app=Flask(__name__)

password=quote_plus(os.getenv('db_password'))
host=os.getenv('hostname')
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:{}@{}:5432/app_1'.format(password,host)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # permet de refuser mes warning dans le code sur le serveur flask

db=SQLAlchemy(app)

########################################################################################
#
#                                  Classe Etudiant
#
########################################################################################

class Etudiant(db.Model):
    __tablename__='etudiants'

    id=db.Column(db.Integer, primary_key=True)
    nom=db.Column(db.String(50), nullable=False)
    prenom=db.Column(db.String(100), nullable=True)
    adresse=db.Column(db.String(100), nullable=True)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id':self.id,
            'nom':self.nom,
            'prenom':self.prenom,
            'adresse':self.adresse
        }

db.create_all()

'''
Les endpoints de l'API

GET /etudiants (liste de tous étudiants)
GET /etudiants/id (sélectionner un étudiant en particulier)
POST /etudiants (créer un nouvel étudiant)
PATCH /etudiants/id (Modifier un étudiant)
DELETE /etudiants/id (Supprimer un étudiant)
'''

########################################################################################
#
#                            Endpoint liste de tous les étudiants
#
########################################################################################

@app.route('/etudiants')
def get_all_students(): 
    # requete avec SQLAlchemy pour recuperer la liste de tous les étudiants
    students = Etudiant.query.all()
    formated_students = [et.format() for et in students]

    return jsonify({
        'success' : True,
        'total etudiants' : len(students), #Etudiant.query.count()
        'etudiants' : formated_students
    })

    
########################################################################################
#
#                         Endpoint liste d'un étudiant en particulier'
#
########################################################################################

@app.route('/etudiants/<int:id>')
def get_one_student(id):
    # requete SQLAlchemy pour sélectionner un étudiant
    student = Etudiant.query.get(id)

    # On vérifie si l'étudiant existe
    if student is None:
        abort(404) # 404 est le status code pour dire que la ressource n'existe pas
    # Si l'étudiant existe alors on le retourne
    else:
        return jsonify({
            'success' : True,
            'selected_id' : id,
            'etudiant' : student.format()
        })



########################################################################################
#
#                         Endpoint liste d'un étudiant en particulier'
#
########################################################################################
@app.route('/etudiants', methods=['POST'])
def create_student():
    # recupération des informations qui seront envoyées dans un format json
    body = request.get_json()
    new_nom = body.get('nom', None)
    new_prenom = body.get('prenom', None)
    new_adresse = body.get('adresse', None)

    etudiant = Etudiant(nom=new_nom, prenom=new_prenom, adresse=new_adresse)
    etudiant.insert()

    return jsonify({
        'success' : True,
        'total etudiants' : Etudiant.query.count(),
        'etudiants' : [et.format() for et in Etudiant.query.all()]
    })


########################################################################################
#
#                         Endpoint supprimer un étudiant
#
########################################################################################
@app.route('/etudiants/<int:id>', methods=['DELETE'])
def delete_student(id):
    student = Etudiant.query.get(id)

    if student is None:
        abort(404)
    else:
        student.delete()
        return jsonify({
            'success' : True,
            'id' : id,
            'etudiant' : student.format(),
            'total_etudiants' : Etudiant.query.count()
        })



########################################################################################
#
#                         Endpoint modifier un étudiant
#
########################################################################################
@app.route('/etudiants/<int:id>', methods=['PATCH'])
def update_student(id):
    # recupération de l'etudiant à modifier
    student = Etudiant.query.get(id)
    
    if student is None:
        abort(404)
    else:

        # recupération des informations qui seront envoyées dans un format json et modification de l'étudiant
        body = request.get_json()
        student.nom = body.get('nom', None)
        student.prenom = body.get('prenom', None)
        student.adresse = body.get('adresse', None)

        student.update()

        return jsonify({
            'success' : True,
            'updated_id' : id,
            'etudiant' : student.format()
        })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success" : False,
        "error" : 404,
        "message" : "Not Found"
    }), 404

@app.errorhandler(500)
def not_found(error):
    return jsonify({
        "success" : False,
        "error" : 500,
        "message" : "Internal Server Error"
    }), 500


@app.errorhandler(400)
def not_found(error):
    return jsonify({
        "success" : False,
        "error" : 400,
        "message" : "Bad Request"
    }), 400


@app.errorhandler(403)
def not_found(error):
    return jsonify({
        "success" : False,
        "error" : 403,
        "message" : "Not Allowed"
    }), 403