@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    body = request.get_json()
    user_id = body.get('user_id', None)

    if user_id is None:
        return jsonify ({
            'msg': 'User Id requerido'
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


# Enfoque de Hans

def add_planet_favorite_b(planet_id, user_id):
    new_favorite = Favorites(user_id=user_id, planet_id=planet_id)
    db.session.add(new_favorite)
    db.session.commit()

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_planet_favorite(planet_id):
    body = request.get_json()
    user_id = body['userID']

    add_planet_favorite_b(planet_id, user_id)
    
    
    return jsonify({}), 200