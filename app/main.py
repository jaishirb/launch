from routes import app
from models import db
from config import DATABASE_CONNECTION_URI
from flask_migrate import Migrate


application = app
db.init_app(app)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_CONNECTION_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
migrate = Migrate(app, db)

if __name__ == "__main__":
    application.run(host='0.0.0.0', debug=True, port=80)
