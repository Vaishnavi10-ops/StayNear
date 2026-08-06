from flask import Flask
from config import Config
from database.db import db
from routes.auth_routes import auth
from routes.main_routes import main
from models.user import User
from models.owner import Owner
from routes.user_routes import user
from routes.owner_routes import owner
from models.property import Property
from models.property_image import PropertyImage
from routes.admin_routes import admin


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# Register Blueprints
app.register_blueprint(main)
app.register_blueprint(auth)
app.register_blueprint(user)
app.register_blueprint(owner)
app.register_blueprint(admin)

if __name__ == "__main__":
    app.run(debug=True)