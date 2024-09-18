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
    people = People.query.filter_by(id = people_id).first()
    if people:
        response_body = {
        'message': 'Personaje encontrado',
        'people': people.serialize()
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
    planet = Planet.query.filter_by(id = planet_id).first()
    if planet:
        response_body = {
            'message': 'Planeta encontrado',
            'planet': planet.serialize()
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
    user = User.query.filter_by(id = user_id).first()
    if user:
        response_body = {
        'message': 'Usuario encontrado',
        'user': user.serialize()
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
    

# Agrega un people favorito con el id = people_id.

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
        
# Elimina un planet favorito con el id = planet_id.

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    # Obtener el cuerpo de la solicitud (JSON) enviado por el cliente.
    body = request.get_json()

    # Verificar si el user_id fue proporcionado en el cuerpo de la solicitud.
    # Si no se proporciona, devolver un error 400 con un mensaje explicativo.
    user_id = body.get('user_id', None)
    if user_id is None:
        return jsonify({
            'msg': 'Usuario Id requerido'
        }), 400
    
    # Buscar si el usuario existe en la base de datos.
    user = User.query.get(user_id)
    if user is None:
        return jsonify({
            'msg': 'Usuario no encontrado'
        }), 404
    
    # Buscar si el planeta está en los favoritos del usuario.
    planet_delete = Favorites.query.filter_by(user_id=user_id, planet_id=planet_id).first()

    if planet_delete:
        db.session.delete(planet_delete)
        db.session.commit()

        return jsonify({
            'msg': 'Planeta eliminado con éxito'
        }), 200
    else:
        return jsonify({
            'msg': 'El planeta no está en favoritos'
        }), 404


# Elimina un people favorito con el id = people_id.

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    body = request.get_json()
    user_id = body.get('user_id', None)

    if user_id is None:
        return jsonify({
            'msg': 'Usuario Id requerido'
        }), 400
    user = User.query.get(user_id)
    if user is None:
        return jsonify({
            'msg': 'El usuario no existe'
        }), 404
    
    people_delete = Favorites.query.filter_by(user_id=user_id, people_id=people_id).first()
    if people_delete:
        db.session.delete(people_delete)
        db.session.commit()
        response_body = {
            'msg': 'Personaje eliminado con éxito'
        }
        return jsonify(response_body), 200
    else:
        response_body = {
            'msg': 'El personaje no está en favoritos'
        } 
        return jsonify(response_body), 404


# Crear un nuevo personaje.
@app.route('/people', methods=['POST'])
def create_character():
    body = request.get_json()
    if not body.get('name') or not body.get('gender') or not body.get('species'):
        return jsonify({
            'msg': 'Faltan datos'
        }), 400
    new_character = People(name=body['name'], gender=body['gender'], species=body['species'])
    db.session.add(new_character)
    db.session.commit()
    return jsonify(new_character.serialize()), 201



# Crear nuevo planeta.

@app.route('/planet', methods=['POST'])
def create_planet():
    body = request.get_json()
    if not body.get('name') or not body.get('climate') or not body.get('terrain'):
        return jsonify({
            'msg': 'Faltan datos'
        }), 400
    new_planet = Planet(name=body['name'], climate=body['climate'], terrain=body['terrain'])
    db.session.add(new_planet)
    db.session.commit()
    return jsonify(new_planet.serialize()), 201


# Editar personaje:

@app.route('/people/<int:people_id>', methods=['PUT'])
def update_character(people_id):
    body = request.get_json()
    character = People.query.get(people_id)
    if not character:
        return jsonify({
            'msg': 'Personaje no encontrado'
        }), 404
    character.name = body.get('name', character.name)
    character.gender = body.get('gender', character.gender)
    character.species = body.get('species', character.species)
    db.session.commit()
    return jsonify(character.serialize()), 200


# Editar planeta:

@app.route('/planet/<int:planet_id>', methods=['PUT'])
def update_planet(planet_id):
    body = request.get_json()
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({
            'msg': 'Planeta no encontrado'
        }), 404
    planet.name = body.get('name', planet.name)
    planet.climate = body.get('climate', planet.climate)
    planet.terrain = body.get('terrain', planet.terrain)
    db.session.commit()
    return jsonify(planet.serialize()), 200


# Delete personaje:
@app.route('/people/<int:people_id>', methods=['DELETE'])
def delete_character(people_id):
    character = People.query.get(people_id)
    if not character:
        return jsonify({
            'msg': 'Personaje no encontrado'
        }), 404
    db.session.delete(character)
    db.session.commit()
    return jsonify({
        'msg': 'Personaje eliminado con éxito'
    }), 200

# Delete planeta:
@app.route('/planet/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({
            'msg': 'Planeta no encontrado'
        }), 404
    db.session.delete(planet)
    db.session.commit()
    return jsonify({
        'msg': 'Planeta eliminado con éxito'
    }), 200



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
