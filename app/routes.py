import csv

from models import Customer, db
from flask import Flask, jsonify, request
from flask import request
from flask_marshmallow import Marshmallow
from config import filename
from flask_rq2 import RQ
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
app.config['RQ_REDIS_URL'] = 'redis://redis:6379'
rq = RQ(app)
ma = Marshmallow(app)


@rq.job
def get_related_info(zip_code_customer, customer_id):
    customer = Customer.query.filter_by(id=customer_id).first()
    with open(filename, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            zip_code_row = row["Zip Code"]
            if int(zip_code_row) == int(zip_code_customer):
                customer.city = row["Place Name"]
                customer.state = row["State"]
                customer.county = row["County"]
    db.session.commit()


class CustomerPostSchema(ma.Schema):
    class Meta:
        fields = ("id",
                  "first_name",
                  "middle_name",
                  "last_name",
                  "email",
                  "zip_code",
                  "city",
                  "county",
                  "state"
                  )
        model = Customer


post_schema = CustomerPostSchema()
posts_schema = CustomerPostSchema(many=True)


@app.route('/customers/all/', methods=['GET'])
def fetch_all():
    customers = Customer.query.all()
    return {'response': posts_schema.dump(customers)}


@app.route('/customers/<customer_id>', methods=['GET'])
def fetch(customer_id):
    customer = Customer.query.filter_by(id=customer_id)
    if customer.scalar() is not None:
        customer = customer.first()
        return {'response': post_schema.dump(customer)}
    return {'response': {'status': 'object not found'}}, 404


@app.route('/customers/add/', methods=['POST'])
def add():
    data = request.get_json()
    first_name = data['first_name']
    middle_name = data['middle_name']
    last_name = data['last_name']
    email = data['email']
    zip_code = data['zip_code']

    customer = Customer.query.filter_by(email=email)
    if customer.scalar() is None:
        customer = Customer(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            email=email,
            zip_code=zip_code
        )
        db.session.add(customer)
        db.session.commit()
        response = post_schema.dump(customer)
        get_related_info.queue(zip_code, response['id'])
        return {'response': response}
    return {'response': {'status': 'email already exists'}}


@app.route('/customers/remove/<customer_id>', methods=['DELETE'])
def remove(customer_id):
    customer = Customer.query.filter_by(id=customer_id)
    if customer.scalar() is not None:
        customer.delete()
        db.session.commit()
        response = {'response': {'status': 'deleted'}}
        return response, 200
    return {'response': {'status': 'object not found'}}, 404


@app.route('/customers/edit/<customer_id>', methods=['PATCH'])
def edit(customer_id):
    customer_to_update = Customer.query.filter_by(id=customer_id)
    if customer_to_update.scalar() is not None:
        customer_to_update = customer_to_update.first()
        data = request.get_json()
        city = data['city']
        county = data['county']
        state = data['state']

        customer_to_update.city = city
        customer_to_update.county = county
        customer_to_update.state = state
        db.session.commit()
        return {'response': post_schema.dump(customer_to_update)}
    return {'response': {'status': 'object not found'}}, 404
