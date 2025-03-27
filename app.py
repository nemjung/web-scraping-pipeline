import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
from models import Scrapping
from database import get_db
from sqlalchemy.orm import Session
from models import Scrapping, init_db

init_db()
load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

def extract(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text ,"html.parser")
    findTable = soup.find('table')
    rawTable = findTable.text
    res = rawTable.split('\n')
    cleanRes = [i for i in res if i]
    return cleanRes

def tranform(rawData):
    products = []
    for i in range(3, len(rawData), 4):
        item = {
            'ลำดับ' : rawData[i],
            'ประเภท' : rawData[i+1],
            'ราคารับซื้อ' : rawData[i+2],
            'การปรับตัว' : rawData[i+3]
        }
        products.append(item)

    newProducts = []
    category = 'ทองแดง / ทองเหลือง'
    for j in range(0, len(products)):
        if float(products[j]['ราคารับซื้อ']) == 0 and products[j]['การปรับตัว'] == 'คงที่':
            category = products[j]['ประเภท']
            category = category.split("***")[1].strip() if "***" in category else ""
            continue
        
        checkAdaptation = products[j]['การปรับตัว']
        if checkAdaptation[0] == '▲':
            adaptation = 'สูงขึ้น'
        elif checkAdaptation[0] == '▼':
            adaptation = 'ลดลง'
        else:
            adaptation = 'คงที่'

        item = {
            'category': category,
            'type' : products[j]['ประเภท'],
            'price' : products[j]['ราคารับซื้อ'],
            'adaptation' : adaptation
        }
        newProducts.append(item)
    return newProducts

def load(cleanedData):
    db: Session = next(get_db())
    try:
        for data in cleanedData:
            db_scraps_price = Scrapping(
                scraps_category=data['category'],
                scraps_type=data['type'],
                scraps_price=float(data['price']),
                scraps_adaptation=data['adaptation']
            )
            db.add(db_scraps_price)
        db.commit()
        print(cleanedData)
        print(f"{len(cleanedData)} rows inserted successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

url = 'https://www.xn--12c7bzakgbj6bza1cbe6b3jwh.com/price'
rawData = extract(url)
cleanedData = tranform(rawData)
load(cleanedData)
