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

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet_query = Planet.query.filter_by(id = planet_id).first()
    if planet_query:
        response_body = {
            'message': 'Planeta encontrado',
            'planet': planet_query.serialize()
        }
        return jsonify(response_body), 200

    else:
        response_body = {
            'message': 'Planeta no encontrado'
        }
        return jsonify(response_body), 404



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
    

#  Añade un nuevo planeta favorito al usuario actual con el id = planet_id.

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    body = request.get_json()
    user_id = body.get('user_id', None)

    if user_id is None:
        return jsonify ({
            'msg': 'Usuario Id requerido'
        }), 400
    user = User.query.get(user_id)
    if user is None:
        return jsonify ({
            'msg': 'Usuario no encontrado'
        }), 400

    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify ({
            'msg': 'Planeta no encontrado'
        }), 400
    
    exists_favorite = Favorites.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if exists_favorite:
        return jsonify ({
            'msg': 'El planeta ya está en favoritos'
        }), 400

    new_favorite = Favorites(user_id=user_id, planet_id=planet_id)
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify ({
            'msg': 'Se añadió a favoritos'
        }), 200
    

# [GET] /users/favorites Listar todos los favoritos que pertenecen al usuario actual.

@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_favorites(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({
            'msg': 'Usuario no encontrado'
        }), 404
    
    # Obtener todos los favoritos de este usuario
    favorites = Favorites.query.filter_by(user_id=user_id).all()

    # Verificamos si hay favoritos
    if not favorites:
        return jsonify({
            'msg': 'No hay favoritos'
        }), 200
    
    # Crear una lista para almacenar los favoritos
    favorite_list = []

    for favorite in favorites:
        if favorite.people_id is not None:
            people = People.query.get(favorite.people_id)
            favorite_list.append({
                'type': 'person',
                'details': people.serialize()
            })
        
        if favorite.planet_id is not None:
            planet = Planet.query.get(favorite.planet_id)
            favorite_list.append({
                'type': 'planet',
                'details': planet.serialize()
            })

    # Devolver la lista de favoritos en formato JSON
    return jsonify({
        'msg': 'Favoritos encontrados',
        'favorites': favorite_list
    }), 200
    


@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def favorite_people(people_id):
    body = request.get_json()
    user_id = body.get('user_id', None)

    if user_id is None:
        return jsonify({
            'msg': 'Usuario Id requerido'
        }), 400
    
    user = User.query.get(user_id)
    if user is None:
        return jsonify({
            'msg': 'Usuario no encontrado'
        }), 400
    
    people = People.query.get(people_id)
    if people is None:
        return jsonify({
            'msg': 'Personaje no encontrado'
        }), 400
    
    exist_favorite = Favorites.query.filter_by(user_id=user_id, people_id=people_id).first()
    if exist_favorite:
        return jsonify({
            'msg': 'El personaje ya está en favoritos'
        }), 400
    
    new_favorite = Favorites(user_id=user_id, people_id=people_id)
    db.session.add(new_favorite)
    db.session.commit()

    return jsonify({
    'msg': 'Se añadio el personaje a favoritos'
    }), 200
        



    
    
    











# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
