


#/client_server/helper_classes/file_utility.py




import csv
from .constants import SUB_COUNTIES_FILE

class FileUtility:
    @staticmethod
    def read_sub_counties(filename=SUB_COUNTIES_FILE):
        with open(filename, mode='r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader, None)  # Skip the header
            return [tuple(row[:2]) for row in csv_reader]

    @staticmethod
    def extract_column_from_csv(file_path, column_name):
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            return [row[column_name] for row in reader]

    @staticmethod
    def read_county_data(file_path):
        county_data = []
        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                county_data.append({
                    'County_Code': int(row['County_Code']),
                    'Name': row['Name'],
                    'Population_2023': int(row['Population_2023']),
                    'Percentage_of_Total': float(row['Percentage_of_Total'])
                })
        return county_data
