from sqlalchemy.orm import scoped_session
from .db import get_session
from .models import Country, Region, County, SubCounty, Constituency, Ward, RegistrationCentre, PollingStation, Correspondence, Encompass
from pathlib import Path
import csv
from sqlalchemy.exc import DataError, IntegrityError

# File paths
BASE_DIR = Path.cwd() / "client_server" / "data_files"
BASE_DIR_R = Path.cwd() / "client_server" / "data_files_r"

CSV_FILES = {
    "countries": BASE_DIR / "countries.csv",
    "regions": BASE_DIR / "regions.csv",
    "counties": BASE_DIR / "counties.csv",
    "subcounties": BASE_DIR / "subcounties.csv",
    "constituencies": BASE_DIR / "constituencies.csv",
    "wards": BASE_DIR / "wards.csv",
    "registration_centers": BASE_DIR / "registration_centers.csv",
    "polling_stations": BASE_DIR / "polling_stations.csv",
    "correspondence": BASE_DIR_R / "correspondence.csv",
    "encompass": BASE_DIR_R / "encompass.csv"
}

# Column mappings for CSV files
COLUMN_MAPPINGS = {
    "countries": {
        'alpha-2': 'alpha_2',
        'alpha-3': 'alpha_3'
    }
}

class CSVLoader:
    def __init__(self, session):
        self.session = session

    def load_csv(self, file_path, model_class, column_mapping=None):
        if not file_path.exists():
            print(f"File {file_path} does not exist.")
            return

        try:
            with open(file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    data = {column_mapping.get(k, k): v for k, v in row.items()} if column_mapping else row
                    instance = model_class(**data)
                    self._add_instance(instance, data)
            self.session.commit()
            print(f"{model_class.__name__} data loaded successfully.")
        except Exception as e:
            self.session.rollback()
            print(f"Error loading {model_class.__name__} data: {e}")

    def _add_instance(self, instance, data):
        try:
            self.session.add(instance)
        except IntegrityError as e:
            print(f"Failed to insert: {data}")
            print(str(e))

class PollingStationLoader:
    def __init__(self, session):
        self.session = session

    def load_polling_stations(self):
        file_path = CSV_FILES["polling_stations"]
        if not file_path.exists():
            print(f"File {file_path} does not exist.")
            return

        try:
            valid_keys = self._get_valid_registration_centres()

            with open(file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if self._is_valid_registration_centre(row, valid_keys):
                        self._process_polling_station_row(row)
            self.session.commit()
            print("PollingStation data loaded successfully.")
        except Exception as e:
            self.session.rollback()
            print(f"Error loading PollingStation data: {e}")

    def _get_valid_registration_centres(self):
        centres = self.session.query(
            RegistrationCentre.ward_code, RegistrationCentre.reg_center_code
        ).all()
        return set((rc.ward_code, rc.reg_center_code) for rc in centres)

    def _is_valid_registration_centre(self, row, valid_keys):
        ward_code, reg_center_code = row['ward_code'], row['reg_center_code']
        if (ward_code, reg_center_code) not in valid_keys:
            print(f"{ward_code},{reg_center_code},xxxxx")
            return False
        return True

    def _process_polling_station_row(self, row):
        try:
            registered_voters = int(row['registered_voters']) if row['registered_voters'] else None
            if not (1 <= len(row['polling_station_code']) <= 15):
                self._print_row(row)
        except ValueError:
            self._print_row(row)
            return

        data = {
            'ward_code': row['ward_code'],
            'reg_center_code': row['reg_center_code'],
            'polling_station_code': row['polling_station_code'],
            'polling_station_name': row['polling_station_name'],
            'registered_voters': registered_voters
        }

        instance = PollingStation(**data)
        self._add_instance(instance, data)

    def _add_instance(self, instance, data):
        try:
            self.session.add(instance)
        except (DataError, IntegrityError) as e:
            print(f"Error with data: {data}")
            print(str(e))
            self.session.rollback()

    def _print_row(self, row):
        print(','.join(map(str, row.values())))

class DataInserter:
    def __init__(self, session):
        self.session = session

    def insert_correspondence_data(self):
        self._bulk_insert(CSV_FILES["correspondence"], Correspondence, ['subcounty_code', 'constituency_code'])
        print(f"{Correspondence.__name__} data loaded successfully.")

    def insert_encompass_data(self):
        self._bulk_insert(CSV_FILES["encompass"], Encompass, ['constituency_code', 'subcounty_code'])
        print(f"{Encompass.__name__} data loaded successfully.")

    def _bulk_insert(self, file_path, model_class, fields):
        if not file_path.exists():
            print(f"File {file_path} does not exist.")
            return

        with open(file_path, mode='r') as file:
            reader = csv.DictReader(file)
            entries = [
                model_class(**{field: row[field] for field in fields})
                for row in reader
            ]
            self.session.bulk_save_objects(entries)
            self.session.commit()

def load_all_data():
    session = get_session()
    try:
        csv_loader = CSVLoader(session)
        polling_loader = PollingStationLoader(session)
        inserter = DataInserter(session)

        csv_loader.load_csv(CSV_FILES["countries"], Country, COLUMN_MAPPINGS.get("countries"))
        csv_loader.load_csv(CSV_FILES["regions"], Region)
        csv_loader.load_csv(CSV_FILES["counties"], County)
        csv_loader.load_csv(CSV_FILES["subcounties"], SubCounty)
        csv_loader.load_csv(CSV_FILES["constituencies"], Constituency)
        csv_loader.load_csv(CSV_FILES["wards"], Ward)
        csv_loader.load_csv(CSV_FILES["registration_centers"], RegistrationCentre)
        polling_loader.load_polling_stations()
        inserter.insert_correspondence_data()
        inserter.insert_encompass_data()

    finally:
        session.close()

if __name__ == "__main__":
    load_all_data()
