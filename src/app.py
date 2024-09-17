"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, Favorites

#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# # Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# # generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)





# Aquí añado mis endpoints

# Listar todos los registros de people en la base de datos.

@app.route('/people', methods=['GET'])
def get_people():
    people = People.query.all()
    people_list = [person.serialize() for person in people]
    return jsonify(people_list), 200


#  Muestra la información de un solo personaje según su id.

@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    people_query = People.query.filter_by(id = people_id).first()
    if people_query:
        response_body = {
        'message': 'Personaje encontrado',
        'people': people_query.serialize()
    }
        return jsonify(response_body), 200
    else: 
        response_body = {
        'message': 'Personaje no encontrado',
    }
        return jsonify(response_body), 400


# Listar todos los registros de planets en la base de datos.

@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    planets_list = [planet.serialize() for planet in planets]
    return jsonify(planets_list), 200

# Muestra la información de un solo planeta según su id.

# @app.route('/planets/<int:planet_id>', methods=['GET'])
# def get_planet(planets_id):
#     planets_query = Planet.query.filter_by(id = planets_id).first()
#     if planets_query:
#         response_body = {
#         'message': 'Planeta encontrado';
#         'planet': planets_query.serialize()
#     }




@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    users_list = [user.serialize() for user in users]
    response_body = {
        'message': 'Lista de usuarios',
        'users': users_list
    }

    return jsonify(response_body), 200



@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user_query = User.query.filter_by(id = user_id).first()
    if user_query:
        response_body = {
        'message': 'Usuario encontrado',
        'user': user_query.serialize()
    }
        return jsonify(response_body), 200
    else: 
        response_body = {
        'message': 'Usuario no encontrado',
    }
        return jsonify(response_body), 400
    


    











# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
