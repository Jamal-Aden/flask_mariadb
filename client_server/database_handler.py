

# /flask_mariadb/client_server/database_handler.py

        
from sqlalchemy.orm import joinedload



import random
import string
from sqlalchemy.orm import scoped_session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import func
from sqlalchemy import text
from .db import get_session
from .models import IDCard, Person, SubCounty, BirthPlace, Address, AddressHistory
from datetime import datetime, timedelta, date




def get_random_day():
    lower_bound = 55
    upper_bound = 254
    random_number = random.randint(lower_bound, upper_bound)
    return random_number





class DatabaseHandler:
    def __init__(self):
        pass

    def save_person_data(self, client_id, first_name, last_name, dob, gender, county, subcounty):
        session = get_session()

        try:
            if isinstance(dob, str):
                dob = datetime.strptime(dob, '%Y-%m-%d').date()
            id_card = self.generate_unique_id_card(session)
            id_num = id_card.id_num
            
            birth_place = self.create_birth_place(session, county, subcounty)
            address = self.add_initial_address(session, county, subcounty)
            
            person = Person(
                first_name=first_name,
                last_name=last_name,
                dob=dob,
                gender=gender,
                id_num=id_num,
                birth_place_id=birth_place.id,
                current_address_id=address.id
            )
            
            session.add(id_card)
            session.add(person)
            session.commit()
            self.add_address_history(person.id, address.id, dob)
            
            return id_num
        except Exception as e:
            session.rollback()
            print(f"Error saving data: {e}")
        finally:
            session.close()

    def generate_unique_id_card(self,session,id_num=None):
        while True:
            try:
                if id_num is None:
                    id_num = random.randint(10000000, 99999999)
                    
                serial_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
                issue_date = datetime.now().date()
                
                existing_id_card = session.query(IDCard).filter(
                    (IDCard.id_num == id_num) | (IDCard.serial_number == serial_number)
                ).first()
                
                if existing_id_card is None:
                    id_card = IDCard(id_num=id_num, serial_number=serial_number, issue_date=issue_date)
                    session.add(id_card)
                    session.commit()  # Save the IDCard object to the database
                    return id_card
            except Exception as e:
                session.rollback()
                print(f"Error generating unique ID card: {e}")

    def get_subcounty_codes(self, county_code):
        session = get_session()
        try:
            subcounties = session.query(SubCounty).filter(SubCounty.county_code == county_code).all()
            return [subcounty.code for subcounty in subcounties]
        finally:
            session.close()

    def create_birth_place(self, session, county, subcounty):
        birth_place = BirthPlace(county_code=county, subcounty_code=subcounty)
        session.add(birth_place)
        session.commit()
        return birth_place

    def add_initial_address(self, session, county_code, subcounty_code):
        address = Address(county_code=county_code, subcounty_code=subcounty_code)
        session.add(address)
        session.commit()
        return address

    def add_address_history(self, person_id, address_id, start_date):
        session = get_session()
        try:
            address_history = AddressHistory(person_id=person_id, address_id=address_id, start_date=start_date)
            session.add(address_history)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error adding address history: {e}")
        finally:
            session.close()

    def register_new_address(self, id_num, new_county_code, new_subcounty_code):
        session = get_session()

        try:
            person = session.query(Person).join(IDCard).filter(IDCard.id_num == id_num).first()
            if not person:
                print("Person not found")
                return

            current_address_history = session.query(AddressHistory).filter(
                AddressHistory.person_id == person.id,
                AddressHistory.end_date == None
            ).first()
            
            if current_address_history:
                current_address_history.end_date = datetime.now()
                session.commit()

            new_address = Address(county_code=new_county_code, subcounty_code=new_subcounty_code)
            session.add(new_address)
            session.commit()

            person.current_address_id = new_address.id
            session.commit()

            new_address_history = AddressHistory(
                person_id=person.id,
                address_id=new_address.id,
                start_date=datetime.now()
            )
            session.add(new_address_history)
            session.commit()

            print(f"Address updated successfully for person {id_num}")

        except Exception as e:
            session.rollback()
            print(f"Error updating address: {e}")
        finally:
            session.close()
            

    def register_new_address_random(self, id_num, new_county_code, new_subcounty_code):
        session = get_session()

        try:
            # Use joinedload to eagerly load related attributes
            person = session.query(Person).options(joinedload(Person.current_address)).join(IDCard).filter(IDCard.id_num == id_num).first()
            if not person:
                print("Person not found")
                return None

            # Get the current address history and end it if it exists
            current_address_history = session.query(AddressHistory).filter(
                AddressHistory.person_id == person.id,
                AddressHistory.end_date == None
            ).first()
            
            if current_address_history:
                current_address_history.end_date = datetime.now()
                session.commit()

            # Create and add the new address
            new_address = Address(county_code=new_county_code, subcounty_code=new_subcounty_code)
            session.add(new_address)
            session.commit()

            # Update the person's current address
            person.current_address_id = new_address.id
            session.commit()

            # Set a new start date for the address history
            new_start_date = datetime.now() + timedelta(days=self.get_random_day())
            
            # Add the new address history
            new_address_history = AddressHistory(
                person_id=person.id,
                address_id=new_address.id,
                start_date=new_start_date
            )
            session.add(new_address_history)
            session.commit()

            # Eagerly load any required relationships or attributes here
            session.refresh(new_address)

            print(f"Address updated successfully for person {id_num}")
            return new_address

        except Exception as e:
            session.rollback()
            print(f"Error updating address: {e}")
            return None
        finally:
            session.close()

    def get_random_day(self):
        # You can customize this function according to your logic
        return random.randint(1, 30)


    








    def get_random_person_id_nums(self, number):
        session = get_session()
        try:
            id_nums = session.query(Person.id_num).order_by(func.random()).limit(number).all()
            return [id_num[0] for id_num in id_nums]
        except Exception as e:
            print(f"Error fetching person id_nums: {e}")
        finally:
            session.close()

    def get_current_address(self, id_num):
        session = get_session()
        try:
            current_address = (
                session.query(Address)
                .join(AddressHistory, Address.id == AddressHistory.address_id)
                .join(Person, Person.id == AddressHistory.person_id)
                .filter(
                    Person.id_num == id_num,
                    AddressHistory.end_date.is_(None)
                )
                .first()
            )
            return current_address
        except Exception as e:
            print(f"Error retrieving current address: {e}")
        finally:
            session.close()

    def fetch_person_info(self):
        session = get_session()
        try:
            query = text("SELECT * FROM person_info")
            result = session.execute(query)
            return result
        except Exception as e:
            print(f"Error fetching person info: {e}")
        finally:
            session.close()

    def get_person_id_by_id_num(self, id_num):
        session = get_session()
        try:
            person = session.query(Person).filter_by(id_num=id_num).first()
            if person:
                return person.id
            else:
                return None
        finally:
            session.close()

    def get_all_table_counts(self):
        session = get_session()
        print("Person", session.query(Person).count())
        print("BirthPlace", session.query(BirthPlace).count())
        print("Address", session.query(Address).count())
        print("AddressHistory", session.query(AddressHistory).count())



    def add_jama(self, first_name='Jama', last_name='Aden', dob=date(1972, 2, 28), gender='M', id_num='11101195', county_code='47', subcounty_code='320'):
        session = get_session()
        
        idcard=self.generate_unique_id_card(session,id_num)
        
        bp = self.create_birth_place(session, county_code, subcounty_code)
        address = self.add_initial_address(session, county_code, subcounty_code)
        
        person = Person(
            first_name=first_name,
            last_name=last_name,
            dob=dob,
            gender=gender,
            id_num=idcard.id_num,
            birth_place_id=bp.id,
            current_address_id=address.id
        )
        
        session.add(person)
        session.commit()
        
        self.add_address_history(person.id, address.id, start_date=dob)
        
    
    def set_new_address(self, id_num, county_code, subcounty_code):
        session = get_session()
        try:
            # Step 1: Retrieve the person by id_num
            person = session.query(Person).join(IDCard).filter(IDCard.id_num == id_num).first()
            if not person:
                raise ValueError("Person not found")

            # Step 2: Retrieve or create the new address
            address = session.query(Address).filter_by(county_code=county_code, subcounty_code=subcounty_code).one_or_none()
            if not address:
                address = Address(county_code=county_code, subcounty_code=subcounty_code)
                session.add(address)
                session.flush()  # Ensure address ID is generated

            # Step 3: Add the current address to address history
            if person.current_address_id:
                current_address_history = AddressHistory(
                    person_id=person.id,
                    address_id=person.current_address_id,
                    start_date=session.query(func.min(AddressHistory.start_date)).filter_by(address_id=person.current_address_id, person_id=person.id).scalar(),
                    end_date=date.today()
                )
                session.add(current_address_history)

            # Step 4: Update the person's current address
            person.current_address_id = address.id
            session.commit()

            print(f"Address updated successfully for person {id_num}")

        except Exception as e:
            session.rollback()
            print(f"Error updating address: {e}")
        finally:
            session.close()


    def register_voter(self, id_num, ward_code, reg_center_code, polling_station_code, start_date=None):
        session = get_session()

        try:
            # Step 1: Retrieve the Person associated with the given ID number
            person = session.query(Person).join(IDCard).filter(IDCard.id_num == id_num).first()
            if not person:
                print("Person not found")
                return
            
            # Step 2: Verify if the RegistrationCentre exists
            registration_centre = session.query(RegistrationCentre).filter(
                RegistrationCentre.ward_code == ward_code,
                RegistrationCentre.reg_center_code == reg_center_code
            ).first()
            if not registration_centre:
                print("Registration Centre not found")
                return

            # Step 3: Verify if the PollingStation exists under the RegistrationCentre
            polling_station = session.query(PollingStation).filter(
                PollingStation.polling_station_code == polling_station_code,
                PollingStation.ward_code == ward_code,
                PollingStation.reg_center_code == reg_center_code
            ).first()
            if not polling_station:
                print("Polling Station not found")
                return

            # Step 4: Create a VoterCard entry for the person
            electors_no = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
            start_date = start_date or datetime.now().date()

            voter_card = VoterCard(
                electors_no=electors_no,
                id_num=person.id_num,
                polling_station_code=polling_station_code,
                start_date=start_date
            )
            session.add(voter_card)
            session.commit()

            print(f"Voter registered successfully with electors_no: {electors_no}")

        except Exception as e:
            session.rollback()
            print(f"Error registering voter: {e}")
        finally:
            session.close()
            
    
    
    
    def get_subcounties_and_constituencies_by_county(self):
        session = get_session()

        try:
            query = (
                session.query(
                    County.name.label('county_name'),
                    SubCounty.name.label('subcounty_name'),
                    Constituency.constituency_name.label('constituency_name')
                )
                .join(SubCounty, County.code == SubCounty.county_code)
                .join(Constituency, County.code == Constituency.county_code)
                .order_by(County.name, SubCounty.name, Constituency.constituency_name)
            )

            results = query.all()

            return [
                {
                    "county_name": result.county_name,
                    "subcounty_name": result.subcounty_name,
                    "constituency_name": result.constituency_name
                }
                for result in results
            ]

        except Exception as e:
            print(f"Error fetching data: {e}")
        finally:
            session.close()





    
    

    """

    def register_new_address_random(self, id_num, new_county_code, new_subcounty_code):
        session = get_session()

        try:
            person = session.query(Person).join(IDCard).filter(IDCard.id_num == id_num).first()
            if not person:
                print("Person not found")
                return

            current_address_history = session.query(AddressHistory).filter(
                AddressHistory.person_id == person.id,
                AddressHistory.end_date == None
            ).first()
            
            if current_address_history:
                current_address_history.end_date = datetime.now()
                session.commit()

            new_address = Address(county_code=new_county_code, subcounty_code=new_subcounty_code)
            session.add(new_address)
            session.commit()

            person.current_address_id = new_address.id
            session.commit()

            new_start_date = datetime.now() + timedelta(days=get_random_day())
            
            new_address_history = AddressHistory(
                person_id=person.id,
                address_id=new_address.id,
                start_date=new_start_date
            )
            session.add(new_address_history)
            session.commit()

            print(f"Address updated successfully for person {id_num}")
            return new_address

        except Exception as e:
            session.rollback()
            print(f"Error updating address: {e}")
        finally:
            session.close()
    

    
    
    def register_new_address_random(self, id_num, new_county_code, new_subcounty_code):
        session = get_session()

        try:
            # Retrieve the person based on their ID number
            person = session.query(Person).options(joinedload(Person.current_address)).join(IDCard).filter(IDCard.id_num == id_num).first()
            if not person:
                print("Person not found")
                return

            # Get the current address history and end it if it exists
            current_address_history = session.query(AddressHistory).filter(
                AddressHistory.person_id == person.id,
                AddressHistory.end_date == None
            ).first()
            
            if current_address_history:
                current_address_history.end_date = datetime.now()
                session.commit()

            # Create and add the new address
            new_address = Address(county_code=new_county_code, subcounty_code=new_subcounty_code)
            session.add(new_address)
            session.commit()

            # Update the person's current address
            person.current_address_id = new_address.id
            session.commit()

            # Set a new start date for the address history
            new_start_date = datetime.now() + timedelta(days=get_random_day())
            
            # Add the new address history
            new_address_history = AddressHistory(
                person_id=person.id,
                address_id=new_address.id,
                start_date=new_start_date
            )
            session.add(new_address_history)
            session.commit()

            # Eagerly load any required relationships or attributes here
            session.refresh(new_address)

            print(f"Address updated successfully for person {id_num}")
            return new_address

        except Exception as e:
            session.rollback()
            print(f"Error updating address: {e}")
        finally:
            session.close()
    
    """
    
