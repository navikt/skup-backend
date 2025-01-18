import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.config.logger import logger

# Last inn miljøvariabler fra .env filen
load_dotenv()

# Hent database URL fra miljøvariabler
if os.getenv("DOCKER") == "1":
    DATABASE_URL = os.getenv("DATABASE_URL_DOCKER")
else:
    DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    logger.error("DATABASE_URL er ikke satt. Vennligst sjekk miljøvariablene dine.")

# Sjekk om SSL skal tvinges
FORCE_SSL = os.getenv("FORCE_SSL", "false").lower() == "true"

connect_args = {}
if FORCE_SSL:
    connect_args = {
        "sslmode": "verify-ca",
        "sslrootcert": os.getenv("SSL_ROOT_CERT"),
        "sslcert": os.getenv("SSL_CERT"),
        "sslkey": os.getenv("SSL_KEY")
    }

# Opprett database motor
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    pool_recycle=300,
    connect_args=connect_args
)

# Opprett en sesjonsfabrikk
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Opprett en baseklasse for modeller
Base = declarative_base()

# Generator for å hente en database sesjon
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()