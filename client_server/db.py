

#/flask_mariadb/client_server/db.py





from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

DATABASE_URL = "mariadb+mariadbconnector://jama:jb@localhost/nrb_db"
engine = create_engine(DATABASE_URL)

SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()

def get_session():
    return SessionLocal()

def create_tables():
    """Create or replace tables in the database."""
    with engine.connect() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS=0;"))
        try:
            Base.metadata.create_all(bind=conn)
        finally:
            conn.execute(text("SET FOREIGN_KEY_CHECKS=1;"))

def delete_tables_sql():
    """Generate SQL statements to drop all tables."""
    sql_statement = """
    SELECT CONCAT('DROP TABLE IF EXISTS `', TABLE_SCHEMA, '`.`', TABLE_NAME, '`;')
    FROM information_schema.TABLES
    WHERE TABLE_SCHEMA = 'nrb_db';
    """
    with engine.connect() as conn:
        result = conn.execute(text(sql_statement))
        for row in result:
            print(row[0])  # Output each drop table statement

def create_or_replace_view():
    """Create or replace the 'person_info' view in the database."""
    drop_view_query = """
        DROP VIEW IF EXISTS person_info;
    """
    create_view_query = """
        CREATE OR REPLACE VIEW person_info AS
        SELECT 
            p.id AS person_id,
            p.first_name,
            p.last_name,
            p.gender,
            p.id_num,
            bpc.name AS birth_county_name,
            bps.name AS birth_subcounty_name,
            ac.name AS address_county_name,
            asub.name AS address_subcounty_name
        FROM 
            persons p
        LEFT JOIN 
            birth_places bp ON p.birth_place_id = bp.id
        LEFT JOIN 
            counties bpc ON bp.county_code = bpc.code
        LEFT JOIN 
            subcounties bps ON bp.subcounty_code = bps.code
        LEFT JOIN 
            addresses a ON p.current_address_id = a.id
        LEFT JOIN 
            counties ac ON a.county_code = ac.code
        LEFT JOIN 
            subcounties asub ON a.subcounty_code = asub.code;
    """
    with engine.connect() as conn:
        conn.execute(text(drop_view_query))
        conn.execute(text(create_view_query))

def init_db(fill_data=False):
    """Initialize the database: create tables and fill with data if specified, otherwise just connect."""
    try:
        if fill_data:
            create_tables()
            from .data_loader import load_all_data
            load_all_data()
            print("Tables created and data loaded successfully.")
        else:
            # Attempt to connect to the database without creating tables
            with engine.connect() as conn:
                print("Connected to the database successfully.")
    except Exception as e:
        print(f"Error initializing the database: {e}")
