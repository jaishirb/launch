from routes import app as flask_app
from config import DATABASE_CONNECTION_URI
from models import db
import random

import os
import tempfile

import pytest
import json

n = random.randint(0, 100)


@pytest.fixture
def client():
    db_fd, flask_app.config['DATABASE'] = tempfile.mkstemp()
    flask_app.config['TESTING'] = True

    with flask_app.test_client() as client:
        with flask_app.app_context():
            db.init_app(flask_app)
            flask_app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_CONNECTION_URI
            flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
        yield client

    os.close(db_fd)
    os.unlink(flask_app.config['DATABASE'])


def test_post_customer(client):
    data = {
        "first_name": "jaisir",
        "middle_name": "alex",
        "last_name": "bayuelo",
        "email": f"jaisirtest_{n}@gmail.com",
        "zip_code": 12184
    }
    send_data = json.dumps(data)
    response = client.post('/customers/add/',
                           data=send_data,
                           headers={"Content-Type": "application/json"})
    assert response.status_code == 200


def test_get_all_customers(client):
    response = client.get('/customers/all/')
    assert response.status_code == 200
    assert "response" in response.json
    assert len(response.json['response']) > 0


def test_background_zip_code_func(client):
    response = client.get('customers/all/')
    assert response.json['response'][0]['city'] is not None
    assert response.json['response'][0]['county'] is not None
    assert response.json['response'][0]['state'] is not None
