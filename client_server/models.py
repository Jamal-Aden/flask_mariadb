
#/flask_mariadb/client_server/models.py

from sqlalchemy import UniqueConstraint
from sqlalchemy import Column, String, Integer, Date, Float, ForeignKey, ForeignKeyConstraint, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base

from .db import Base, engine

class Country(Base):
    __tablename__ = 'countries'
    name = Column(String(255), primary_key=True)
    alpha_2 = Column(String(2), nullable=False, unique=True)
    alpha_3 = Column(String(3), nullable=False, unique=True)
    numeric = Column(String(5), nullable=False, unique=True)

class Region(Base):
    __tablename__ = 'regions'
    code = Column(String(2), primary_key=True)
    name = Column(String(255), nullable=False)
    hasc = Column(String(255), nullable=False, unique=True)
    capital = Column(String(255), nullable=False)
    area = Column(Float)

    counties = relationship('County', order_by='County.code', back_populates='region')

class County(Base):
    __tablename__ = 'counties'
    region_code = Column(String(2), ForeignKey('regions.code', ondelete='CASCADE'), nullable=False)
    code = Column(String(2), primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    capital_city = Column(String(255), nullable=False)
    hasc = Column(String(255), nullable=False, unique=True)
    kbs = Column(String(255), nullable=False, unique=True)
    area = Column(Float)

    region = relationship('Region', back_populates='counties')
    subcounties = relationship('SubCounty', order_by='SubCounty.code', back_populates='county')
    constituencies = relationship('Constituency', order_by='Constituency.constituency_code', back_populates='county')
    birth_places = relationship('BirthPlace', back_populates='county')
    addresses = relationship('Address', back_populates='county')

class SubCounty(Base):
    __tablename__ = 'subcounties'
    code = Column(String(5), primary_key=True)
    county_code = Column(String(2), ForeignKey('counties.code', ondelete='CASCADE'), nullable=False)
    name = Column(String(255), nullable=False)

    county = relationship('County', back_populates='subcounties')
    locations = relationship('Location', back_populates='subcounty')
    birth_places = relationship('BirthPlace', back_populates='subcounty')
    addresses = relationship('Address', back_populates='subcounty')
    
    
    # Relationships to Correspondence and Encompass
    correspondence = relationship('Correspondence', back_populates='subcounty', uselist=False)  # One-to-one
    encompass = relationship('Encompass', back_populates='subcounty')  # One-to-many

    
class Constituency(Base):
    __tablename__ = 'constituencies'
    constituency_code = Column(String(5), primary_key=True)
    constituency_name = Column(String(100), nullable=False, unique=True)
    county_code = Column(String(2), ForeignKey('counties.code', ondelete='CASCADE'), nullable=False)

    county = relationship('County', back_populates='constituencies')
    wards = relationship('Ward', back_populates='constituency')
    
    
    # Relationships to Correspondence and Encompass
    correspondence = relationship('Correspondence', back_populates='constituency', uselist=False)  # One-to-one
    encompass = relationship('Encompass', back_populates='constituency')
    
    
    
class Ward(Base):
    __tablename__ = 'wards'
    
    ward_code = Column(String(5), primary_key=True)
    ward_name = Column(String(100), nullable=False)
    constituency_code = Column(String(5), ForeignKey('constituencies.constituency_code', ondelete='CASCADE'), nullable=False)

    constituency = relationship('Constituency', back_populates='wards')
    registration_centres = relationship('RegistrationCentre', back_populates='ward')

class RegistrationCentre(Base):
    __tablename__ = 'registration_centres'
    
    ward_code = Column(String(5), ForeignKey('wards.ward_code', ondelete='CASCADE'), primary_key=True)
    reg_center_code = Column(String(3), primary_key=True)
    reg_center_name = Column(String(255))

    ward = relationship('Ward', back_populates='registration_centres')
    polling_stations = relationship('PollingStation', back_populates='registration_centre')

    __table_args__ = (
        PrimaryKeyConstraint('ward_code', 'reg_center_code'),
    )

class PollingStation(Base):
    __tablename__ = 'polling_stations'
    
    polling_station_code = Column(String(15), primary_key=True)
    polling_station_name = Column(String(255), nullable=False)
    registered_voters = Column(Integer)
    reg_center_code = Column(String(3), nullable=False)
    ward_code = Column(String(5), nullable=False)

    registration_centre = relationship(
        'RegistrationCentre', 
        back_populates='polling_stations',
        foreign_keys=[reg_center_code, ward_code]
    )
    voter_cards = relationship('VoterCard', back_populates='polling_station')

    __table_args__ = (
        ForeignKeyConstraint(
            ['ward_code', 'reg_center_code'],
            ['registration_centres.ward_code', 'registration_centres.reg_center_code'],
            ondelete='CASCADE'
        ),
    )

class Location(Base):
    __tablename__ = 'locations'
    location_code = Column(String(5), primary_key=True)
    name = Column(String(100), nullable=False)
    subcounty_code = Column(String(5), ForeignKey('subcounties.code', ondelete='CASCADE'), nullable=False)

    subcounty = relationship('SubCounty', back_populates='locations')
    sublocations = relationship('SubLocation', back_populates='location')

class SubLocation(Base):
    __tablename__ = 'sub_locations'
    sub_location_code = Column(String(6), primary_key=True)
    name = Column(String(100), nullable=False)
    location_code = Column(String(5), ForeignKey('locations.location_code', ondelete='CASCADE'), nullable=False)

    location = relationship('Location', back_populates='sublocations')



class Correspondence(Base):
    __tablename__ = 'correspondence'
    subcounty_code = Column(String(5), ForeignKey('subcounties.code'))
    constituency_code = Column(String(5), ForeignKey('constituencies.constituency_code'))
    
    __table_args__ = (
        PrimaryKeyConstraint('subcounty_code', 'constituency_code'),
    )

    # Relationships
    subcounty = relationship('SubCounty', back_populates='correspondence')
    constituency = relationship('Constituency', back_populates='correspondence')


class Encompass(Base):
    __tablename__ = 'encompass'
    
    constituency_code = Column(String(5), ForeignKey('constituencies.constituency_code'))
    subcounty_code = Column(String(5), ForeignKey('subcounties.code'))
    

    __table_args__ = (
        PrimaryKeyConstraint('constituency_code','subcounty_code'),
    )

    # Relationships
    subcounty = relationship('SubCounty', back_populates='encompass')
    constituency = relationship('Constituency', back_populates='encompass')





class IDCard(Base):
    __tablename__ = 'idcards'
    id = Column(Integer, primary_key=True, index=True)
    id_num = Column(String(8), nullable=False, unique=True)
    serial_number = Column(String(12), nullable=False, unique=True)
    issue_date = Column(Date, nullable=False)

    person = relationship('Person', back_populates='id_card')
    voter_card = relationship('VoterCard', uselist=False, back_populates='id_card')

class VoterCard(Base):
    __tablename__ = 'voter_cards'
    electors_no = Column(String(12), primary_key=True, index=True)
    id_num = Column(String(8), ForeignKey('idcards.id_num', ondelete='CASCADE'))
    gpk_no = Column(String(12))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    
    polling_station_code = Column(String(15), ForeignKey('polling_stations.polling_station_code', ondelete='CASCADE'))

    id_card = relationship('IDCard', back_populates='voter_card')
    polling_station = relationship('PollingStation', back_populates='voter_cards')

class Person(Base):
    __tablename__ = 'persons'
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(20), nullable=False)
    last_name = Column(String(20), nullable=False)
    dob = Column(Date, nullable=False)
    gender = Column(String(2), nullable=False)
    id_num = Column(String(8), ForeignKey('idcards.id_num', ondelete='CASCADE'), nullable=False)
    birth_place_id = Column(Integer, ForeignKey('birth_places.id'))
    current_address_id = Column(Integer, ForeignKey('addresses.id', ondelete='SET NULL'))
    
    birthplace = relationship("BirthPlace", back_populates="person")
    id_card = relationship('IDCard', back_populates='person')
    current_address = relationship('Address', back_populates='persons')
    address_histories = relationship('AddressHistory', back_populates='person')

class BirthPlace(Base):
    __tablename__ = 'birth_places'
    id = Column(Integer, primary_key=True, index=True)
    county_code = Column(String(2), ForeignKey('counties.code', ondelete='CASCADE'))
    subcounty_code = Column(String(5), ForeignKey('subcounties.code', ondelete='CASCADE'))
    person = relationship("Person", back_populates="birthplace", uselist=False)

    county = relationship('County', back_populates='birth_places')
    subcounty = relationship('SubCounty', back_populates='birth_places')

class Address(Base):
    __tablename__ = 'addresses'
    id = Column(Integer, primary_key=True, index=True)
    county_code = Column(String(2), ForeignKey('counties.code', ondelete='CASCADE'))
    subcounty_code = Column(String(5), ForeignKey('subcounties.code', ondelete='CASCADE'))
    street_address=Column(String(255),nullable=True)

    county = relationship('County', back_populates='addresses')
    subcounty = relationship('SubCounty', back_populates='addresses')
    persons = relationship('Person', back_populates='current_address')

class AddressHistory(Base):
    __tablename__ = 'address_histories'
    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey('persons.id', ondelete='CASCADE'))
    address_id = Column(Integer, ForeignKey('addresses.id', ondelete='CASCADE'))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)

    person = relationship('Person', back_populates='address_histories')
    address = relationship('Address')




