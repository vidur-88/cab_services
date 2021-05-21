from contextlib import contextmanager

from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DB_HOST = 'sqlite:///'
DB_NAME = 'cab_service.sqlite'

Base = declarative_base()


@contextmanager
def session_scope():
    session_obj = DBSession(DB_HOST, DB_NAME)
    try:
        yield session_obj.session
        session_obj.session.commit()
    except:
        session_obj.session.rollback()
        raise
    finally:
        session_obj.session.expunge_all()
        session_obj.session.close()


class DBSession(object):
    def __init__(self, db_host=DB_HOST, db_name=DB_NAME):
        self.engine = create_engine(db_host + db_name)
        self.session = sessionmaker(bind=self.engine)()

    def close(self):
        self.session.close()


def create_schema():
    session_obj = DBSession(DB_HOST, DB_NAME)
    Base.metadata.create_all(session_obj.engine)
    session_obj.close()


class Cab(Base):
    __tablename__ = "cab"

    id = Column(INT, primary_key=True, autoincrement=True)
    driver_name = Column(VARCHAR(50))
    company_name = Column(VARCHAR(50))
    model_name = Column(VARCHAR(50))
    type = Column(Enum('HatchBack', 'SUV', 'Sedan', 'MPV'))
    rc_number = Column(VARCHAR(20))
    city_id = Column(INT)
    update_time = Column(DateTime)


class Booking(Base):
    __tablename__ = "booking"

    id = Column(INT, primary_key=True, autoincrement=True)
    cab_id = Column(INT)
    start_city_id = Column(INT)
    end_city_id = Column(INT)
    client_id = Column(INT)
    start_time = Column(DateTime)
    end_time = Column(DateTime)


class City(Base):
    __tablename__ = "city"

    id = Column(INT, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(50))
    state_name = Column(VARCHAR(10))


class CabState(Base):
    __tablename__ = "cab_state"

    id = Column(INT, primary_key=True, autoincrement=True)
    cab_id = Column(INT)
    state = Column(Enum('ON_TRIP', 'IDLE'))
    city_id = Column(INT)


if __name__ == '__main__':
    """
    This is for creating schema for the system.
    """
    create_schema()
