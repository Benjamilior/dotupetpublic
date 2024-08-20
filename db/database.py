import os 
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


sqliteName = "pets.sqlite"
basedir = os.path.dirname(os.path.realpath(__file__))
databaseurl = f"sqlite:///{os.path.join(basedir, sqliteName)}"

engine = create_engine(databaseurl, echo=True)

Sessionlocal = sessionmaker(bind=engine)

Base = declarative_base()