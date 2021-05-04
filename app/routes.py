import csv

from models import Customer, db, Data
from flask import Flask
from flask import request
from flask_marshmallow import Marshmallow
from config import filename
from flask_rq2 import RQ
from flask_cors import CORS

from serializers import PostCustomerSerializer, PatchCustomerSerializer
from tasks import calculate_distance
import pandas as pd

app = Flask(__name__)
CORS(app)
app.config['RQ_REDIS_URL'] = 'redis://redis:6379'
rq = RQ(app)
ma = Marshmallow(app)
flag = True


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
                customer.lat = row['Latitude']
                customer.lon = row['Longitude']
    db.session.commit()


@rq.job
def most_common():
    df = pd.read_csv(filename)
    df_top_freq = df.groupby('County')['Zip Code'].agg(
        County_count=len).sort_values(
        "County_count", ascending=False)
    general_data = {}
    for index, row in df_top_freq.iterrows():
        zip_codes = {
            'data': []
        }
        with open(filename, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for _row in csv_reader:
                if _row['County'] == index:
                    zip_codes['data'].append(
                        _row['Zip Code']
                    )
        data = Data(
            county=index,
            frequency=row['County_count'].item(),
            zip_codes=zip_codes
        )
        db.session.add(data)
        db.session.commit()
        general_data[index] = zip_codes
    return general_data


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
                  "state",
                  "lat",
                  "lon"
                  )
        model = Customer


post_schema = CustomerPostSchema()
posts_schema = CustomerPostSchema(many=True)


class DataGetSchema(ma.Schema):
    class Meta:
        fields = ("id",
                  "county",
                  "frequency",
                  "zip_codes")
        model = Data


data_schema = DataGetSchema()
data_schemas = DataGetSchema(many=True)


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
    serializer = PostCustomerSerializer(**data)
    if serializer.is_valid():
        email = data['email']
        zip_code = data['zip_code']

        customer = Customer.query.filter_by(email=email)
        if customer.scalar() is None:
            customer = Customer(
                **data
            )
            db.session.add(customer)
            db.session.commit()
            response = post_schema.dump(customer)
            get_related_info.queue(zip_code, response['id'])
            return {'response': response}
        return {'response': {'status': 'email already exists'}}, 400
    return {'response': {'status': 'invalid request'}}, 400


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
        serializer = PatchCustomerSerializer(**data)
        if serializer.is_valid():
            customer_to_update.update(**data)
            db.session.commit()
            return {'response': post_schema.dump(customer_to_update)}
        return {'response': {'status': 'invalid request'}}, 400
    return {'response': {'status': 'object not found'}}, 404


@app.route('/customers/distance/', methods=['POST'])
def calc_distance():
    data = request.get_json()
    customer_1 = Customer.query.filter_by(id=data['id_customer_1']).first()
    customer_2 = Customer.query.filter_by(id=data['id_customer_2']).first()
    distance = calculate_distance(customer_1, customer_2)
    return {'response': {'distance_in_miles': distance}}


@app.route('/customers/common/process/', methods=['GET'])
def common():
    global flag
    if flag:
        most_common.queue()
        flag = False
        return {'response': {'status': 'processing'}}
    return {'response': {'status': 'processing was already executed'}}, 400


@app.route('/customers/common/all/', methods=['GET'])
def get_all():
    data = Data.query.all()
    return {'response': data_schemas.dump(data)}


@app.route('/customers/reset/', methods=['DELETE'])
def reset():
    global flag
    Customer.query.delete()
    Data.query.delete()
    db.session.commit()
    flag = True
    return {'response': {'status': 'database reset ok'}}
