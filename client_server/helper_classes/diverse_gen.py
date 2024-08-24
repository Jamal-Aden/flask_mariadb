



#/client_server/helper_classes/diverse_gen.py


import random
import datetime
from .constants import DATE_RANGE_START, DATE_RANGE_END, BOYS_FILE, GIRLS_FILE, SURNAMES_FILE
from .file_utility import FileUtility
from ..database_handler import DatabaseHandler

db_handler = DatabaseHandler()

class DiverseGen:
    def __init__(self, boys_list, girls_list, surnames_list, cs_list):
        self.boys_list = boys_list
        self.girls_list = girls_list
        self.surnames_list = surnames_list
        self.cs_list = cs_list
        self.subcounty_codes_list = []


    def gen_random_date(self):
        random_days = random.randint(0, (DATE_RANGE_END - DATE_RANGE_START).days)
        return DATE_RANGE_START + datetime.timedelta(days=random_days)

    def generate_random_string(self, size, text="0123456789"):
        if not text or size <= 0:
            return ""
        return ''.join(random.choices(text, k=size))

    def gen_boy_name(self):
        return random.choice(self.boys_list)

    def gen_girl_name(self):
        return random.choice(self.girls_list)

    def gen_last_name(self):
        return random.choice(self.surnames_list)

    def gen_gender(self):
        return random.choice(("M", "F"))
        
    def set_subcounty_codes_list(self, county_code):
        self.subcounty_codes_list = db_handler.get_subcounty_codes(str(county_code))
        return self.subcounty_codes_list
    

    def gen_subcounty_code(self):
        return random.choice(self.subcounty_codes_list)
    
    def gen_subcounty_code2(self,county_code):
        sclist=self.set_subcounty_codes_list(county_code)
        return random.choice(sclist)
           
    

    def get_data(self, county_code):
        gender = self.gen_gender()
        first_name = self.gen_boy_name() if gender == "M" else self.gen_girl_name()
        last_name = self.gen_last_name()
        dob = self.gen_random_date()
        #subcounty = self.gen_subcounty_code()
        subcounty = self.gen_subcounty_code2(county_code)
        return {
            "first_name": first_name,
            "last_name": last_name,
            "dob": dob.strftime('%Y-%m-%d'),
            "gender": gender,
            "county": county_code,
            "subcounty": subcounty
        }

def get_gen():
    cs_list = FileUtility.read_sub_counties()
    boys_names = FileUtility.extract_column_from_csv(BOYS_FILE, "Name")
    girls_names = FileUtility.extract_column_from_csv(GIRLS_FILE, "Name")
    surnames_list = FileUtility.extract_column_from_csv(SURNAMES_FILE, "Surname")
    return DiverseGen(boys_names, girls_names, surnames_list, cs_list)



