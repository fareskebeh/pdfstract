from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
load_dotenv()

user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
port = int(os.getenv("DB_PORT"))
database = os.getenv("DB_NAME")

def get_connection():
    engine = create_engine(
        f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
    )
    return engine

if __name__ == "__main__":

    try:
        engine = get_connection()
        print(f"Connection to the {host} for user {user} created successfully.")

    except Exception as ex:
        print("Connection could not be made due to the following error:\n", ex)