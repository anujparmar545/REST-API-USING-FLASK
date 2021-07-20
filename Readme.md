##In order to do live reload of server, create env variables
```
    FLASK_DEBUG=true 
    FLASK_ENV= development
```
##For DB, we are using SQLAlchemy
```
    pip install flask-SQLAlchemy
```
##Following command should be run through venv    
```
    create db: flask db_create
    seed db: flask db_seed
    drop db: flask db_drop
``` 
##For Serialization/Deserialization od db data in flask:
```
    pip install flask-marshmallow
```
##For JWT based authentication:
```
     pip install flask-jwt-extended
```
##To support Email send
```
    pip install Flask-Mail
    Login to mailtrap.io, copy the config code and paste in app.py
```    
##Generate dependency file:
```
     pip freeze
     pip freeze > requirements.txt
```
   
