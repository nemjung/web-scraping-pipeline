from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import declarative_base
from database import engine

Base = declarative_base()

class Scrapping(Base):
    __tablename__ = 'scrap-pipeline'
    scraps_id = Column(Integer, primary_key=True, autoincrement=True)
    scraps_category = Column(String(255), nullable=False)
    scraps_type = Column(String(255), nullable=False)
    scraps_price = Column(Float, nullable=False)
    scraps_adaptation = Column(String(255), nullable=False)

def init_db():
    Base.metadata.create_all(bind=engine)

