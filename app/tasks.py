from geopy.distance import geodesic


def calculate_distance(customer_1, customer_2):
    point_1 = customer_1.lat, customer_1.lon
    point_2 = customer_2.lat, customer_2.lon
    return geodesic(point_1, point_2).miles
