

#/flask_mariadb/client_server/dbase_handler.py

import json
from datetime import date

from .db import get_session
#from sqlalchemy import func

from sqlalchemy import case, func

from .models import Region, County, SubCounty, Constituency,Person


class DatabaseHandler_Util:
    def __init__(self):
        pass

    def get_regions_with_counties_and_subcounties(self):
        session = get_session()
        regions = session.query(Region).all()
        result = []
        
        for region in regions:
            region_data = {
                'region_name': region.name,
                'region_code': region.code,
                'counties': []
            }
            
            for county in region.counties:
                county_data = {
                    'county_name': county.name,
                    'county_code': county.code,
                    'subcounties': []
                }
                
                for subcounty in county.subcounties:
                    subcounty_data = {
                        'subcounty_name': subcounty.name,
                        'subcounty_code': subcounty.code
                    }
                    
                    county_data['subcounties'].append(subcounty_data)
                
                region_data['counties'].append(county_data)
            
            result.append(region_data)
        
        return result

    def print_regions_tree(self):
        regions = self.get_regions_with_counties_and_subcounties()
        for region in regions:
            print(f"Region: {region['region_name']} (Code: {region['region_code']})")
            for county in region['counties']:
                print(f"  County: {county['county_name']} (Code: {county['county_code']})")
                for subcounty in county['subcounties']:
                    print(f"    SubCounty: {subcounty['subcounty_name']} (Code: {subcounty['subcounty_code']})")
                    
    def get_regions_hierarchy_markdown(self):
        regions = self.get_regions_with_counties_and_subcounties()
        markdown = ""
        for region in regions:
            markdown += f"# Region: {region['region_name']} (Code: {region['region_code']})\n"
            for county in region['counties']:
                markdown += f"## County: {county['county_name']} (Code: {county['county_code']})\n"
                for subcounty in county['subcounties']:
                    markdown += f"### SubCounty: {subcounty['subcounty_name']} (Code: {subcounty['subcounty_code']})\n"
        return markdown

    def get_regions_hierarchy_json(self):
        regions = self.get_regions_with_counties_and_subcounties()
        return json.dumps(regions, indent=4)

    def list_subcounties_and_constituencies(self):
        session = get_session()
        results = session.query(
            County.name.label('county_name'),
            SubCounty.name.label('subcounty_name'),
            Constituency.constituency_name.label('constituency_name')
        ).outerjoin(
            SubCounty, County.code == SubCounty.county_code
        ).outerjoin(
            Constituency, County.code == Constituency.county_code
        ).all()

        county_dict = {}
        for row in results:
            county_name = row.county_name
            subcounty_name = row.subcounty_name
            constituency_name = row.constituency_name

            if county_name not in county_dict:
                county_dict[county_name] = {'subcounties': [], 'constituencies': []}
            
            if subcounty_name:
                county_dict[county_name]['subcounties'].append(subcounty_name)
            if constituency_name:
                county_dict[county_name]['constituencies'].append(constituency_name)
        
        return county_dict
        
    
    
    def list_subcounties_and_constituencies2(self):
        from sqlalchemy.orm import joinedload
        session = get_session()
        counties = session.query(County).options(
            joinedload(County.subcounties),
            joinedload(County.constituencies)
        ).all()

        county_dict = {}
        for county in counties:
            county_name = county.name
            if county_name not in county_dict:
                county_dict[county_name] = {'subcounties': [], 'constituencies': []}
            
            for subcounty in county.subcounties:
                county_dict[county_name]['subcounties'].append(subcounty.name)
            
            for constituency in county.constituencies:
                county_dict[county_name]['constituencies'].append(constituency.constituency_name)
        
        return county_dict

    def print_subcounties_and_constituencies(self):
        county_dict = self.list_subcounties_and_constituencies()
        for county, data in county_dict.items():
            print(f"County: {county}")
            print(f"  Subcounties: {', '.join(data['subcounties'])}")
            print(f"  Constituencies: {', '.join(data['constituencies'])}")
    
    def query_constituencies(self):
        session = get_session()
        try:
            constituencies = session.query(Constituency.constituency_name, Constituency.constituency_code).all()
            return [{'name': c.constituency_name, 'code': c.constituency_code} for c in constituencies]
        finally:
            session.close()
            
            
    def query_sub_counties(self):
        session = get_session()
        try:
            sub_counties = session.query(SubCounty.name, SubCounty.code).all()
            return [{'name': sc.name, 'code': sc.code} for sc in sub_counties]
            
        finally:
            session.close()
    
    def print_query_sub_counties(self):
        print("\tSub-Counties Data")
        sub_counties = self.query_sub_counties()
        
        for sub_county in sub_counties:
            print(f"{sub_county['name']},{sub_county['code']}")
            
    def print_query_constituencies(self):
        print("\tConstituencies Data")
        constituencies = self.query_constituencies()
        for constituency in constituencies:
            print(f"{constituency['name']},{constituency['code']}")


    
    def get_number_of_adults(self):
        session = get_session()
        today = date.today()
        eighteen_years_ago = today.replace(year=today.year - 18)

        # Query the number of persons who are 18 or older
        adult_count = session.query(func.count(Person.id)).filter(Person.dob <= eighteen_years_ago).scalar()

        return adult_count


    def get_number_of_adults_and_percentage(self):
        session = get_session()
        today = date.today()
        eighteen_years_ago = today.replace(year=today.year - 18)

        # Query the number of persons who are 18 or older
        adult_count = session.query(func.count(Person.id)).filter(Person.dob <= eighteen_years_ago).scalar()

        # Query the total number of persons
        total_person_count = session.query(func.count(Person.id)).scalar()

        # Calculate the percentage of adults
        if total_person_count > 0:
            adult_percentage = (adult_count / total_person_count) * 100
        else:
            adult_percentage = 0

        return {
            'adult_count': adult_count,
            'total_person_count': total_person_count,
            'adult_percentage': adult_percentage
        }




    def get_age_groups_count(self):
        session = get_session()
        try:
            today = date.today()
            current_year = today.year

            # Query to get counts of persons within each age group using CASE statements
            age_groups_query = session.query(
                func.count(case(
                    [(current_year - func.extract('year', Person.dob) <= 12, 1)]
                )).label("Childhood"),
                func.count(case(
                    [(current_year - func.extract('year', Person.dob).between(13, 19), 1)]
                )).label("Adolescence"),
                func.count(case(
                    [(current_year - func.extract('year', Person.dob).between(20, 34), 1)]
                )).label("Young_Adulthood"),  # Ensured consistent label
                func.count(case(
                    [(current_year - func.extract('year', Person.dob).between(35, 54), 1)]
                )).label("Middle_Adulthood"),  # Ensured consistent label
                func.count(case(
                    [(current_year - func.extract('year', Person.dob).between(55, 64), 1)]
                )).label("Late_Adulthood"),  # Ensured consistent label
                func.count(case(
                    [(current_year - func.extract('year', Person.dob) >= 65, 1)]
                )).label("Older_Adulthood")  # Ensured consistent label
            ).one()

            # Format the results into a dictionary
            age_groups = {
                "Childhood (0-12)": age_groups_query.Childhood,
                "Adolescence (13-19)": age_groups_query.Adolescence,
                "Young Adulthood (20-34)": age_groups_query.Young_Adulthood,
                "Middle Adulthood (35-54)": age_groups_query.Middle_Adulthood,
                "Late Adulthood (55-64)": age_groups_query.Late_Adulthood,
                "Older Adulthood (65+)": age_groups_query.Older_Adulthood
            }

            return age_groups
        finally:
            session.close()

