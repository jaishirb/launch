import flask_sqlalchemy


db = flask_sqlalchemy.SQLAlchemy()


class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120))
    middle_name = db.Column(db.String(120))
    last_name = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True)
    zip_code = db.Column(db.String(100))
    city = db.Column(db.String(70), nullable=True)
    county = db.Column(db.String(70), nullable=True)
    state = db.Column(db.String(70), nullable=True)