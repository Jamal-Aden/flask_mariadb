
# /flask_mariadb/test_database_handler.py

import sys
import asyncio
import random

from client_server.database_handler import DatabaseHandler

from client_server.models import IDCard, Person, SubCounty, BirthPlace, Address, AddressHistory

from client_server.dbase_handler import DatabaseHandler_Util

from pprint import pp



import inspect


"""
def print_object_variables(obj):
    for name, value in inspect.getmembers(obj):
        if not name.startswith('__') and not inspect.ismethod(value):
            print(f"{name}: {value}")
"""

def print_object_variables(obj):
    if obj is None:
        print("Object is None")
        return

    # Use try-except to handle any potential errors when accessing attributes
    try:
        for name, value in inspect.getmembers(obj):
            if not name.startswith('__') and not inspect.ismethod(value):
                print(f"{name}: {value}")
    except Exception as e:
        print(f"Error printing object variables: {e}")


"""
def change_mass_addresses(dbhandler,nr_persons):
    c=dbhandler.get_random_person_id_nums(nr_persons)
    print(c)
    for i in c:
        o=dbhandler.get_current_address(i)
        slist=dbhandler.get_subcounty_codes(o.county_code)
        print(o.id,o.county_code,o.subcounty_code,slist)
        
        slist.remove(o.subcounty_code)
        
        new_subcounty_code=random.choice(slist)
        #print(new_subcounty_code)
        
        #dbhandler.register_new_address((  dbhandleri,o.county_code,new_subcounty_code)
        
        newaddress=dbhandler.register_new_address_random(i,o.county_code,new_subcounty_code)
        print_object_variables(newaddress)
"""  


def change_mass_addresses(dbhandler, nr_persons):
    c = dbhandler.get_random_person_id_nums(nr_persons)
    if not c:
        print("No person IDs found or error occurred.")
        return

    print(c)
    for i in c:
        o = dbhandler.get_current_address(i)
        if o is None:
            print(f"No current address found for person ID {i}")
            continue

        slist = dbhandler.get_subcounty_codes(o.county_code)
        if not slist:
            print(f"No subcounty codes found for county {o.county_code}")
            continue

        print(o.id, o.county_code, o.subcounty_code, slist)

        slist.remove(o.subcounty_code)
        new_subcounty_code = random.choice(slist)

        newaddress = dbhandler.register_new_address_random(i, o.county_code, new_subcounty_code)
        if newaddress:
            print_object_variables(newaddress)
        else:
            print(f"Failed to update address for person ID {i}")
      

def print_person_info(dbhandler):
    result = dbhandler.fetch_person_info()

    for row in result:
        #print(row.keys())
        print(row)
    print(result.keys())
    
def region_print(db_util):
    """
    regions_info = db_util.get_regions_with_counties_and_subcounties()
    for region in regions_info:
        print(region)
    """
    db_util.print_regions_tree()



def test_DatabaseHandler():
    nr_persons=40
    dbhandler=DatabaseHandler()
    change_mass_addresses(dbhandler,nr_persons)
    
    #print_person_info(dbhandler)
    #dbhandler.get_all_table_counts()

 

def test_DatabaseHandler_Util():
    
    #
    db_util = DatabaseHandler_Util()
    #region_print(db_util
    #db_util.print_subcounties_and_constituencies()
    #db_util.print_query_sub_counties()
    #db_util.print_query_constituencies()
    
    r=db_util.get_number_of_adults_and_percentage()
    pp(r)
    s=db_util.get_age_groups_count()
    pp(s)

   
    



#-------------------------------------------------------------


class AsyncPoller:
    def __init__(self, db_handler):
        self.db_handler = db_handler

    async def poll_age_groups_count(self):
        while True:
            age_groups = self.db_handler.get_age_groups_count()
            output = f"\rAge Groups Count: {age_groups}"
            sys.stdout.write(output)
            sys.stdout.flush()  # Ensure the output is printed immediately
            await asyncio.sleep(2)  # Asynchronous sleep for 2 seconds before the next query

# Example usage
async def main():
    db_handler = DatabaseHandler_Util()
    poller = AsyncPoller(db_handler)
    await poller.poll_age_groups_count()



#-------------------------------------------------------------



    
    
    
    

if __name__ == "__main__":

    #test_DatabaseHandler()
    #test_DatabaseHandler_Util()
    asyncio.run(main())






