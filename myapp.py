from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import join


import random
from datetime import datetime, timedelta

"""
from .models import Person, Location, SubCounty
from .database import db,init_db

"""




app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'your_database_uri_here'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my_database.db'

db = SQLAlchemy(app)


class Country(db.Model):
    __tablename__ = 'countries'
    name = db.Column(db.String(255), primary_key=True)
    alpha_2 = db.Column(db.String(2))
    alpha_3 = db.Column(db.String(3))
    numeric = db.Column(db.String(5))
    
    def __init__(self,name,alpha_2,alpha_3,numeric):
        self.name=name
        self.alpha_2=alpha_2
        self.alpha_3=alpha_3
        self.numeric=numeric

class Region(db.Model):
    __tablename__ = 'regions'
    code = db.Column(db.String(2), primary_key=True)
    name = db.Column(db.String(255))
    hasc = db.Column(db.String(255))
    capital = db.Column(db.String(255))
    area = db.Column(db.Float)
    
    def __init__(self, code, name, hasc, capital, area):
        self.code = code
        self.name = name
        self.hasc = hasc
        self.capital = capital
        self.area = area


class County(db.Model):
    __tablename__ = 'counties'
    region_code = db.Column(db.String(2), db.ForeignKey('regions.code'))
    code = db.Column(db.String(2), primary_key=True)
    name = db.Column(db.String(255))
    capital_city = db.Column(db.String(255))
    hasc = db.Column(db.String(255))
    kbs = db.Column(db.String(255))
    area = db.Column(db.Float)
    
    def __init__(self, region_code, code, name, capital_city, hasc, kbs, area):
        self.region_code = region_code
        self.code = code
        self.name = name
        self.capital_city = capital_city
        self.hasc = hasc
        self.kbs = kbs
        self.area = area

class SubCounty(db.Model):
    __tablename__ = 'subcounties'
    code = db.Column(db.String(2), primary_key=True)
    county_code = db.Column(db.String(2), db.ForeignKey('counties.code'))
    name = db.Column(db.String(255))
    
    def __init__(self, code, county_code, name):
        self.code = code
        self.county_code = county_code
        self.name = name




class IDCard(db.Model):
    __tablename__ = 'idcards'
    
    id = db.Column(db.Integer, primary_key=True)
    id_num = db.Column(db.Integer,nullable=False,unique=True)
    serial_number= db.Column(db.String, nullable=False,unique=True)
    issue_date = db.Column(db.Date, nullable=False)
    issue_officer=db.Column(db.Integer, db.ForeignKey('employee.id'))
    def __init__(self, id_num, serial_number,issue_date,issue_officer):
        self.id_num = id_num
        self.serial_number=serial_number
        self.issue_date = issue_date
        self.issue_officer=issue_officer
        
    @staticmethod
    def generate_unique_id_num():
        while True:
            id_num = random.randint(10000000, 99999999)  # Generate a random 8-digit number
            # Check if the generated id_num is unique
            if not IDCard.query.filter_by(id_num=id_num).first():
                return id_num

    @staticmethod
    def generate_unique_serial_number():
        while True:
            serial_number = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890', k=6))  # Generate a random 6-character alphanumeric string
            # Check if the generated serial_number is unique
            if not IDCard.query.filter_by(serial_number=serial_number).first():
                return serial_number
    
    @staticmethod
    def create_new_id_card(issue_officer):
        issue_date = datetime.now().date()  # Example issue date, change as needed
        id_num = IDCard.generate_unique_id_num()
        serial_number = IDCard.generate_unique_serial_number()
        id_card = IDCard(id_num=id_num, serial_number=serial_number, issue_date=issue_date, issue_officer=issue_officer)
        db.session.add(id_card)
        db.session.commit()
        return id_card
        


class Employee(db.Model):
    __tablename__ = 'employee'
    
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date,nullable=True)
    
    def __init__(self,start_date, end_date=None):
        self.start_date = start_date
        self.end_date = end_date


class Person(db.Model):
    __tablename__ = 'people'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String, nullable=False)
    id_num = db.Column(db.Integer, db.ForeignKey('idcards.id_num'),unique=True, nullable=False)

    
    def __init__(self, first_name, last_name, dob, gender, id_num):
        self.first_name = first_name
        self.last_name = last_name
        self.dob = dob
        self.gender = gender
        self.id_num = id_num
    

    def serialize(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'dob': self.dob.strftime('%Y-%m-%d'),  # Format date as string
            'gender': self.gender,
            'id_num': self.id_num,
            
        }


    def __str__(self):
        return f"{self.first_name:<12} {self.last_name:<12} {self.dob.strftime('%d%m%Y')} {self.gender:>2} {self.id_num:08}"

    def __repr__(self):
        return f"Person('{self.first_name}', '{self.last_name}', '{self.dob}', '{self.gender}', '{self.id_num}')"





class Address(db.Model):
   __tablename__ = 'address'
   address_id = db.Column(db.Integer,primary_key=True)
   county = db.Column(db.String,db.ForeignKey('counties.code'),nullable=False)
   subcounty = db.Column(db.String,db.ForeignKey('subcounties.code'),nullable=False)
   street_address = db.Column(db.String(100))

   def __init__(self,county,subcounty,street_address):
       self.county = county
       self.subcounty = subcounty
       self.street_address = street_address





class PersonAddressHistory(db.Model):
    __tablename__ = 'person_address_history'
    person_address_history_id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer,db.ForeignKey('people.id'))
    address_id = db.Column(db.Integer,db.ForeignKey('address.address_id'))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date,nullable=True)
    # NULL for current address

    def __init__(self, person_id, address_id, start_date, end_date=None):
        self.person_id = person_id
        self.address_id = address_id
        self.start_date = start_date
        self.end_date = end_date



class Location(db.Model):
    __tablename__ = 'location'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey('people.id'))
    county_code = db.Column(db.String(2), db.ForeignKey('counties.code'))
    subcounty_code = db.Column(db.String(2), db.ForeignKey('subcounties.code'))
    
    def __init__(self, person_id, county_code, subcounty_code):
        self.person_id = person_id
        self.county_code = county_code
        self.subcounty_code = subcounty_code




#-----------------------------------------------




    
    
        
def get_counties_with_subcounties():
    counties_with_subcounties = db.session.query(County, SubCounty).join(SubCounty, County.code == SubCounty.county_code).all()
    
    county_subcounty_dict = {}
    for county, subcounty in counties_with_subcounties:
        if county in county_subcounty_dict:
            county_subcounty_dict[county].append(subcounty)
        else:
            county_subcounty_dict[county] = [subcounty]
    
    return county_subcounty_dict

def print_counties_with_subcounties():
    county_subcounty_dict = get_counties_with_subcounties()

    for county, subcounties in county_subcounty_dict.items():
        print(f"County: {county.name}")
        print("Subcounties:")
        for subcounty in subcounties:
            print(f"- {subcounty.name}")
        print()



def save_id_nums_to_file(file_path):
    # Query all id_num values from the Person table
    id_nums = db.session.query(Person.id_num).all()

    # Extract the id_nums from the query result
    id_nums = [id_num for (id_num,) in id_nums]

    # Write id_nums to file
    with open(file_path, 'w') as file:
        for id_num in id_nums:
            file.write(f"{id_num}\n")

# Usage example
save_id_nums_to_file('id_nums.txt')



def get_county_name(code):
    return County.query.filter_by(code=code).first().name

def get_subcounty_name(code):
    return SubCounty.query.filter_by(code=code).first().name


def get_county_code_by_name(county_name):
    county = County.query.filter_by(name=county_name).first()
    if county:
        return county.code
    else:
        return None

def get_subcounty_code_by_name(subcounty_name):
    subcounty = SubCounty.query.filter_by(name=subcounty_name).first()
    if subcounty:
        return subcounty.code
    else:
        return None

def usage():
    county_name = "Nairobi"
    county_code = get_county_code_by_name(county_name)
    if county_code:
        print("County Code:", county_code)
    else:
        print("County not found.")
            
            
    subcounty_name = "Kamukunji"
    subcounty_code = get_subcounty_code_by_name(subcounty_name)
    if subcounty_code:
        print("Subcounty Code:", subcounty_code)
    else:
        print("Subcounty not found.")




def get_persons_born_in_county(county_code):
    query = db.session.query(Person).join(Location, Person.id == Location.person_id).filter(Location.county_code == county_code).all()
    return query

def display_single(county_code):
    persons_in_county = get_persons_born_in_county(county_code)
    for person in persons_in_county:
        print(person)
    
    
def display_all():
    county_codes = [str(i) for i in range(1, 48)]
    for c in county_codes:
        
        persons_in_county = get_persons_born_in_county(c)
        if persons_in_county:
            print("\t",c,get_county_name(c))
            for person in persons_in_county:
                print(person)
            print('-'*20)


def get_persons_with_current_address_in_county(county_code):
    # Join tables to get the required data
    query_result = db.session.query(Person, Address)\
        .join(PersonAddressHistory, Person.id == PersonAddressHistory.person_id)\
        .join(Address, PersonAddressHistory.address_id == Address.address_id)\
        .filter(Address.county == county_code)\
        .filter(PersonAddressHistory.end_date == None)\
        .all()

    # Extract relevant information from the query result
    persons_with_address = [(person.serialize(), address.street_address) for person, address in query_result]
    
    return persons_with_address

def display_person_residing_in_county(county_code):
    result = get_persons_with_current_address_in_county(county_code)
    for r in result:
        print(r)



def generate_random_string(size,text="0123456789"):
  if not text or size <= 0:
    return ""
  chars = list(text)
  random.shuffle(chars)
  return ''.join(chars[:size])



def create_persons_and_assign_birthplace(num_persons):
    subcounties = SubCounty.query.all()
    for _ in range(num_persons):
        # Generate random person details
        first_name = "Person" + str(_)
        last_name = "Lastname" + str(_)
        dob = datetime.now().date() - timedelta(days=random.randint(365 * 18, 365 * 80))  # Random dob between 18 and 80 years ago
        gender = random.choice(["Male", "Female"])
        
        # Create a new person
        id_num=generate_random_string(8)
        person = Person(first_name=first_name, last_name=last_name, dob=dob, gender=gender,id_num=id_num)
        db.session.add(person)
        db.session.commit()
        
        # Assign a random sublocation as birthplace
        subcounty = random.choice(subcounties)
        location = Location(person_id=person.id, county_code=subcounty.county_code, subcounty_code=subcounty.code)
        db.session.add(location)
        db.session.commit()






if __name__ == "__main__":
    from pathlib import Path
    cwd=Path.cwd()
    file=cwd/ "id_numbers.txt"
    
    
    #print_counties_with_subcounties()
    #print_counties_with_subcounties()
    
    #save_id_nums_to_file(file)
    #usage()
    
    
    
    display_all()
    
    county_code = '47'
    display_person_residing_in_county(county_code)
    
    # Call the function to create 20,000 persons and assign birthplaces
    
    create_persons_and_assign_birthplace(20000)
    
    