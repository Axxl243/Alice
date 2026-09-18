import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

class config:

#Variables de entorno para conexiones y servicios 
    API_KEY = os.getenv("APP_KEY")

    BD_HOST = os.getenv("MYSQL_HOST")


