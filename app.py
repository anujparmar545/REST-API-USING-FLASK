from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float
import os
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_mail import Message, Mail

app = Flask(__name__)
# DB config
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'planets.db')
db = SQLAlchemy(app)
# Serialization config
ma = Marshmallow(app)
# JWT config
app.config['JWT_SECRET_KEY'] = 'super-secret-key'
jwt = JWTManager(app)
# Mail config
app.config['MAIL_SERVER'] = 'smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = '2e01894b5ac7c7'  # os.environ['MAIL_USERNAME']
app.config['MAIL_PASSWORD'] = '1dec77c16bd886'  # os.environ['MAIL_PASSWORD']
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)


@app.cli.command('db_create')
def db_create():
    db.create_all()
    print('Database created !')


@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print('Database Dropped !')


@app.cli.command('db_seed')
def db_seed():
    mercury = Planet(planet_name='Mercury',
                     planet_type='Class D',
                     home_star='Sol',
                     mass=3.258e23,
                     radius=1516,
                     distance=35.98e6)

    venus = Planet(planet_name='Venus',
                   planet_type='Class K',
                   home_star='Sol',
                   mass=4.678e24,
                   radius=4321,
                   distance=44.865e2)

    earth = Planet(planet_name='Earth',
                   planet_type='Class M',
                   home_star='Sol',
                   mass=6.329e24,
                   radius=6400,
                   distance=54.334e54)

    db.session.add(mercury)
    db.session.add(venus)
    db.session.add(earth)

    test_user = User(first_name='Anuj',
                     last_name='Parmar',
                     email='anujparmar545@gmail.com',
                     password='Pass123')
    db.session.add(test_user)
    db.session.commit()
    print('Database Seeded !')


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/anuj')
def hello_anuj():
    return jsonify(message='Hello Anuj!')


@app.route('/query_string')
def query_string():
    name = request.args.get('name')
    age = int(request.args.get('age'))
    if age > 18:
        return jsonify(message='Hello ' + name + ' You are adult')
    else:
        return jsonify(message='Sorry you are teenager')


@app.route('/path_variable/<string:name>/<int:age>')
def path_variable(name: str, age: int):
    if age > 18:
        return jsonify(message='Hello ' + name + ' You are adult')
    else:
        return jsonify(message='Sorry you are teenager')


@app.route('/planet', methods=['GET'])
def planets():
    planet_list = Planet.query.all()
    result = planetsSchema.dump(planet_list)
    return jsonify(result)


@app.route('/planet_details/<int:planet_id>', methods=['GET'])
def planet_details(planet_id: int):
    planet = Planet.query.filter_by(planet_id=planet_id).first()
    if planet:
        return jsonify(planetSchema.dump(planet))
    else:
        return jsonify(message='Planet does not exist'), 404


@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    test = User.query.filter_by(email=email).first()
    if test:
        return jsonify(message='User already exists!!'), 409
    else:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']
        user = User(first_name=first_name, last_name=last_name, email=email, password=password)
        db.session.add(user)
        db.session.commit()

        return jsonify(message='User created successfully'), 201


@app.route('/login', methods=['POST'])
def login():
    if request.is_json:
        email = request.json['email']
        password = request.json['password']
    else:
        email = request.form['email']
        password = request.form['password']
    test = User.query.filter_by(email=email, password=password).first()
    if test:
        access_token = create_access_token(identity=email)
        return jsonify(message='Login Successful!!', access_token=access_token)
    else:
        return jsonify(message='Email or password is incorrect !!'), 401


@app.route('/retrieve_password/<string:email>', methods=['GET'])
def retrieve_password(email: str):
    user = User.query.filter_by(email=email).first()
    if user:
        msg = Message('Your Planetary API password is: ' + user.password,
                      sender='admin@planetary-api.com',
                      recipients=[email])
        mail.send(msg)
        return jsonify(message='Password sent to ' + email)
    else:
        return jsonify(message='This email does not exist')


@app.route('/add_planet', methods=['POST'])
@jwt_required()
def add_planet():
    planet_name = request.form['planet_name']
    planet = Planet.query.filter_by(planet_name=planet_name).first()
    if planet:
        return jsonify(message='Planet already exist by this name'), 409
    else:
        new_planet = Planet(planet_name=request.form['planet_name'],
                            planet_type=request.form['planet_type'],
                            home_star=request.form['home_star'],
                            mass=float(request.form['mass']),
                            radius=float(request.form['radius']),
                            distance=float(request.form['distance']))
        db.session.add(new_planet)
        db.session.commit()

        return jsonify(message='Planet saved successfully'), 201


@app.route('/update_planet', methods=['PUT'])
def update_planet():
    planet_id = int(request.form['planet_id'])
    planet = Planet.query.filter_by(planet_id=planet_id).first()
    if planet:
        planet.planet_name = request.form['planet_name']
        planet.planet_type = request.form['planet_type']
        planet.home_star = request.form['home_star']
        planet.mass = float(request.form['mass'])
        planet.radius = float(request.form['radius'])
        planet.distance = float(request.form['distance'])

        db.session.commit()
        return jsonify(message='Planet updated successfully'), 202
    else:
        return jsonify(message='Planet does not exist'), 404


@app.route('/remove_planet/<int:planet_id>', methods=['DELETE'])
def remove_planet(planet_id):
    planet = Planet.query.filter_by(planet_id=planet_id).first()
    if planet:
        db.session.delete(planet)
        db.session.commit()
        return jsonify(message='Planet removed successfully'), 202
    else:
        return jsonify(message='Planet does not exist'), 404


# Database Models
class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)


class Planet(db.Model):
    __tablename__ = 'planets'
    planet_id = Column(Integer, primary_key=True)
    planet_name = Column(String)
    planet_type = Column(String)
    home_star = Column(String)
    mass = Column(Float)
    radius = Column(Float)
    distance = Column(Float)


class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'first_name', 'last_name', 'email', 'password')


class PlanetSchema(ma.Schema):
    class Meta:
        fields = ('planet_id', 'planet_name', 'planet_type', 'home_star', 'mass', 'radius', 'distance')


userSchema = UserSchema()
usersSchema = UserSchema(many=True)

planetSchema = PlanetSchema()
planetsSchema = PlanetSchema(many=True)

if __name__ == '__main__':
    app.run()
