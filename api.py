import json

from flask import Flask, jsonify, request

from services import *


app = Flask(__name__)


@app.route('/cab_register', methods=['POST'])
def cab_register():
    try:
        params = json.loads(request.data)
        cab_id = CabHandler(params).create_cab()
        return jsonify({
            'message': 'cab registered successfully, id: {}'.format(cab_id)
        })
    except Exception as e:
        return jsonify(e), 500


@app.route('/cab_list', methods=['GET'])
def get_cab_list():
    try:
        params = json.loads(request.data)
        cab_list = CabHandler(params).get_cab_lists()
        return jsonify(cab_list)
    except Exception as e:
        return jsonify(e), 500


@app.route('/booking', methods=['POST'])
def booking():
    try:
        params = json.loads(request.data)
        booking_id = BookingHandler(params).booking_req()
        return jsonify({
            'booking_id': booking_id,
            'message': 'Booking successfully'
        })
    except Exception as e:
        return jsonify(e), 500


@app.route('/end_trip', methods=['POST'])
def end_trip():
    try:
        params = json.loads(request.data)
        booking_id = BookingHandler(params).end_trip()
        return jsonify({
            'booking_id': booking_id,
            'message': 'End trip, thanks!'
        })
    except Exception as e:
        return jsonify(e), 500


@app.route('/all_bookings', methods=['GET'])
def get_all_bookings():
    try:
        params = None
        cities = BookingHandler(params).get_all_bookings()
        return jsonify(cities)
    except Exception as e:
        return jsonify(e), 500


@app.route('/add_city', methods=['POST'])
def add_city():
    try:
        params = json.loads(request.data)
        city_id = CityHandler(params).add_city()
        return jsonify({
            'city_id': city_id,
            'message': 'city added successfully'
        })
    except Exception as e:
        return jsonify(e), 500


@app.route('/cities', methods=['GET'])
def get_cities():
    try:
        params = None
        cities = CityHandler(params).get_cities()
        return jsonify(cities)
    except Exception as e:
        return jsonify(e), 500


@app.route('/cab_state_history', methods=['GET'])
def get_cab_state_history():
    try:
        params = json.loads(request.data)
        cab_lists = CabHandler(params).cab_state_history(params['duration'])
        return jsonify(cab_lists)
    except Exception as e:
        return jsonify(e), 500


@app.route('/', methods=['GET'])
def welcome():
    try:
        return jsonify({'message': 'Welcome to the Cab service'})
    except Exception as e:
        return jsonify(e), 500


if __name__ == '__main__':
    app.run()
