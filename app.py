from flask import Flask
from config import Config
from database.db import db

from routes.main_routes import main

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# Register Blueprints
app.register_blueprint(main)

if __name__ == "__main__":
    app.run(debug=True)