from datetime import datetime
from dateutil.relativedelta import relativedelta

import sqlalchemy
from sqlalchemy.sql import func

from models import session_scope, Cab, CabState, Booking, City


def seconds_calc(delta):
    """ delta is relativedelta return """
    return (delta.hours * 3600) + (delta.minutes * 60) + delta.seconds


class AddData(object):
    def __init__(self):
        pass

    @staticmethod
    def save(data_obj):
        try:
            with session_scope() as session_obj:
                session_obj.add(data_obj)
                session_obj.flush()
                session_obj.refresh(data_obj)
                return data_obj.id
        except Exception as e:
            print(e)
            raise Exception('Error while saving the data, msg: {}'.format(e))


class CabHandler(AddData):
    def __init__(self, info):
        super(CabHandler, self).__init__()
        self.info = info
        self.cab_id = None

    def create_cab(self):
        """
        After creating entry in Cab it will also add entry
        for corresponding CabState with IDLE.
        :return:
        """
        cab = Cab()
        cab.type = self.info['type']
        cab.driver_name = self.info.get('driver_name')
        cab.rc_number = self.info['rc_number']
        cab.city_id = self.info['city_id']
        cab.company_name = self.info['company_name']
        cab.model_name = self.info['model_name']
        cab.update_time = datetime.utcnow().replace(microsecond=0)
        self.cab_id = self.save(cab)

        # we can do asynchronously
        self.create_cab_state()
        return self.cab_id

    def create_cab_state(self):
        cab_state = CabState()
        cab_state.cab_id = self.cab_id
        cab_state.city_id = self.info['city_id']
        cab_state.state = 'IDLE'
        _ = self.save(cab_state)

    def get_cab_lists(self):
        city_id = self.info['city_id']
        with session_scope() as session_obj:
            cab_list = session_obj.query(
                CabState, Cab
            ).filter(
                CabState.city_id == city_id,
                CabState.cab_id == Cab.id,
                CabState.state == 'IDLE'
            ).all()
            return [{'cab_id': c.CabState.cab_id,
                     'company_name': c.Cab.company_name,
                     'model_name': c.Cab.model_name,
                     'type': c.Cab.type,
                     'state': c.CabState.state,
                     'rc_number': c.Cab.rc_number}
                    for c in cab_list]

    def cab_state_history(self, duration):
        """
        How much time Cab was idle in given duration.
        :return:
        """

        # if request for particular cab idle time count
        cab_id = self.info.get('cab_id')
        start_time, end_time = tuple(duration)
        start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        end_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
        diff = relativedelta(end_time, start_time)
        num_seconds = seconds_calc(diff)
        data = self.get_cab_trip_history(cab_id, start_time, end_time)
        res = {}
        for d in data:
            trip_seconds = seconds_calc(relativedelta(d.end_time, d.start_time))
            if d.cab_id in res:
                res[d.cab_id] += trip_seconds
            else:
                res[d.cab_id] = trip_seconds

        return [
            {
                'cab_id': cab_id,
                'idle_seconds': num_seconds - trip_seconds
            }
            for cab_id, trip_seconds in res.items()
        ]

    @staticmethod
    def get_cab_trip_history(cab_id, start_time, end_time):
        with session_scope() as session_obj:
            query = session_obj.query(
                Booking.cab_id, Booking.start_time, Booking.end_time
            )
            if cab_id is not None:
                query = query.filter(Booking.cab_id == cab_id)
            query = query.filter(
                Booking.start_time >= start_time,
                Booking.end_time <= end_time,
            )
            data = query.all()
            data = [d for d in data]
            return data


class CabStateHandler(object):
    def __init__(self, cab_id, city_id):
        self.cab_id = cab_id
        self.city_id = city_id

    def update_cab_state(self, state):
        with session_scope() as session_obj:
            session_obj.query(
                CabState
            ).filter(
                CabState.cab_id == self.cab_id
            ).update(
                {'city_id': self.city_id, 'state': state}
            )
            session_obj.flush()


class BookingHandler(AddData):
    def __init__(self, info):
        super(BookingHandler, self).__init__()
        self.info = info

    def update_cab_state(self, state, city_id):
        cab_id = self.info['cab_id']
        cab_state = CabStateHandler(cab_id=cab_id, city_id=city_id)
        cab_state.update_cab_state(state=state)

    def booking_req(self):
        # ignoring slots, future time booking
        booking = Booking()
        booking.cab_id = self.info['cab_id']
        booking.start_city_id = self.info['start_city_id']
        booking.end_city_id = self.info['end_city_id']
        booking.client_id = self.info['client_id']
        booking.start_time = datetime.utcnow().replace(microsecond=0)
        booking_id = self.save(booking)

        # we can do async
        self.update_cab_state(state='ON_TRIP', city_id=self.info['start_city_id'])

        return booking_id

    def end_trip(self):
        """
        This will update the booking end time and cab state from ON_TRIP to IDLE
        :return:
        """
        booking_id = self.info['booking_id']
        with session_scope() as session_obj:
            session_obj.query(
                Booking
            ).filter(
                Booking.id == booking_id
            ).update(
                {
                    'end_time': datetime.utcnow().replace(microsecond=0)
                }
            )
            session_obj.flush()

        # we can do async
        self.update_cab_state(state='IDLE', city_id=self.info['end_city_id'])
        return booking_id

    def get_all_bookings(self):
        # can do pagination to improve query performance
        with session_scope() as session_obj:
            all_bookings = session_obj.query(
                Booking
            ).all()
            return [
                {
                    'booking_id': b.id,
                    'client_id': b.client_id,
                    'cab_id': b.cab_id,
                    'start_city_id': b.start_city_id,
                    'end_city_id': b.end_city_id,
                    'start_time': b.start_time,
                    'end_time': b.end_time
                }
                for b in all_bookings
            ]

    def check_cab_state(self, cab_id):
        # avoiding race condition, not required if we are maintaining the cache
        pass


# Here we can maintain a cache for cab state
# and can do lazy update in DB for cab state
# when new cab getting added then we first add
# that cab in cache and will do lazy insert in DB
def cached_cab_state():
    pass


class CityHandler(AddData):
    def __init__(self, info):
        super(CityHandler, self).__init__()
        self.info = info

    def add_city(self):
        city = City()
        city.name = self.info['name']
        city.state_name = self.info['state_name']
        return self.save(city)

    @staticmethod
    def get_cities():
        with session_scope() as session_obj:
            cities = session_obj.query(City).all()
            return [{'name': c.name, 'city_id': c.id} for c in cities]


if __name__ == '__main__':
    duration = ['2021-05-20 18:00:00', '2021-05-20 19:00:00']
    cab = CabHandler({}).cab_state_history(duration)
    print(cab)