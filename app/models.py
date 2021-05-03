import flask_sqlalchemy

db = flask_sqlalchemy.SQLAlchemy()


class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120))
    middle_name = db.Column(db.String(120), nullable=True)
    last_name = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True)
    zip_code = db.Column(db.String(5))
    city = db.Column(db.String(70), nullable=True)
    county = db.Column(db.String(70), nullable=True)
    state = db.Column(db.String(70), nullable=True)
    lat = db.Column(db.Float, nullable=True)
    lon = db.Column(db.Float, nullable=True)


class Data(db.Model):
    __tablename__ = 'data'
    id = db.Column(db.Integer, primary_key=True)
    county = db.Column(db.String(70))
    frequency = db.Column(db.Integer)
    zip_codes = db.Column(db.JSON)
