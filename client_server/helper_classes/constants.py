


#/client_server/helper_classes/constants.py



import datetime
from pathlib import Path

DATE_RANGE_START = datetime.date(1934, 1, 1)
DATE_RANGE_END = datetime.date.today()

BASE_DIR = Path.cwd() / "client_server" / "data"
SUB_COUNTIES_FILE = BASE_DIR / "sub_counties.csv"
BOYS_FILE = BASE_DIR / "names_db" / "boys.csv"
GIRLS_FILE = BASE_DIR / "names_db" / "girls.csv"
SURNAMES_FILE = BASE_DIR / "names_db" / "surnames.csv"
