from flask_sqlalchemy import SQLAlchemy

# Inicializamos SQLAlchemy
db = SQLAlchemy()

# Definimos la clase User usando SQLAlchemy
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), nullable=False)
    firstname = db.Column(db.String(15), nullable=False)
    lastname = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(35), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    subscription_date = db.Column(db.String(25), nullable=False)

    favorite = db.relationship('Favorites', backref = 'user')

    def __repr__(self):
        return f'<User {self.username}>'

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "email": self.email,
            # No incluimos el password por razones de seguridad
        }

# Definimos la clase Character
class People(db.Model):
    __tablename__ = 'people'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False)
    gender = db.Column(db.String(25), nullable=False)
    species = db.Column(db.String(25), nullable=False)

    favorite = db.relationship('Favorites', backref = 'people')

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "species": self.species,
        }

    def __repr__(self):
            return f'<People {self.name}>'



# Definimos la clase Planet
class Planet(db.Model):
    __tablename__ = 'planet'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False)
    climate = db.Column(db.String(25), nullable=False)
    terrain = db.Column(db.String(30), nullable=False)

    favorite = db.relationship('Favorites', backref = 'planet')

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "terrain": self.terrain,
        }
    
    def __repr__(self):
        return f'<Planet {self.name}>'

# Definimos la clase Favorites, que relaciona a los usuarios con sus personajes y planetas favoritos
class Favorites(db.Model):
    __tablename__ = 'favorites'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    people_id = db.Column(db.Integer, db.ForeignKey('people.id'))
    planet_id = db.Column(db.Integer, db.ForeignKey('planet.id'))


    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "people_id": self.people_id,
            "planet_id": self.planet_id,
        }
    
    def __repr__(self):
        return f'<Favorites {self.id}>'

