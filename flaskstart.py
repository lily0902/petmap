import json
from flask import Flask, jsonify, request, redirect, render_template, session
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
import mysql.connector
import os
from mysql.connector import connect

# 定義 MySQL 連接參數
DB_USER = 'root'          # 例如 'root'
DB_PASSWORD = '1234'      # 例如 'password'
DB_HOST = 'localhost'              # 例如 '127.0.0.1'
DB_NAME = 'pet_database'

# 1. 檢查並建立資料庫
def initialize_database():
    try:
        # 連接到 MySQL 伺服器（不指定資料庫）
        cnx = connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST)
        cursor = cnx.cursor()

        # 檢查是否存在資料庫
        cursor.execute(f"SHOW DATABASES LIKE '{DB_NAME}'")
        database_exists = cursor.fetchone()

        if not database_exists:
            # 如果資料庫不存在，建立資料庫
            cursor.execute(f"CREATE DATABASE {DB_NAME} DEFAULT CHARACTER SET 'utf8'")
            print(f"資料庫 '{DB_NAME}' 已建立。")
            import_data()
        else:
            print(f"資料庫 '{DB_NAME}' 已存在。")

        cursor.close()
        cnx.close()

    except Exception as e:
        print(f"資料庫初始化錯誤: {e}")

# 2. 定義資料表和匯入資料
def import_data():
    engine = create_engine(f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')
    Base = declarative_base()

    class PetLost(Base):
        __tablename__ = 'pet_lost'
        
        id = Column(Integer, primary_key=True, autoincrement=True)
        chip_number = Column(String(50))
        pet_name = Column(String(50))
        pet_type = Column(String(10))
        gender = Column(String(10))
        breed = Column(String(50))
        color = Column(String(50))
        appearance = Column(String(50))
        features = Column(String(255))
        lost_date = Column(DateTime)
        lost_location = Column(String(255))
        latitude = Column(Float)
        longitude = Column(Float)
        owner_name = Column(String(50))
        contact_phone = Column(String(50))
        email = Column(String(100))
        photo_url = Column(String(255))

    # 建立表格
    Base.metadata.create_all(engine)

    # 將 Excel 資料匯入 MySQL
    Session = sessionmaker(bind=engine)
    session = Session()

    # 讀取 Excel 檔案並清理資料
    file_path = 'static/tables/pet_lost.xlsx'
    excel_data = pd.read_excel(file_path)
    excel_data.columns = ['chip_number', 'pet_name', 'pet_type', 'gender', 'breed', 'color', 'appearance', 
                          'features', 'lost_date', 'lost_location', 'latitude', 'longitude', 
                          'owner_name', 'contact_phone', 'email', 'photo_url']

     # 將 NaN 值轉換為 None
    excel_data = excel_data.where(pd.notnull(excel_data), None)
    
    # 將資料插入 MySQL
    for _, row in excel_data.iterrows():
        pet = PetLost(
            chip_number=row['chip_number'],
            pet_name=row['pet_name'],
            pet_type=row['pet_type'],
            gender=row['gender'],
            breed=row['breed'],
            color=row['color'],
            appearance=row['appearance'],
            features=row['features'],
            lost_date=row['lost_date'],
            lost_location=row['lost_location'],
            latitude=row['latitude'],
            longitude=row['longitude'],
            owner_name=row['owner_name'],
            contact_phone=row['contact_phone'],
            email=row['email'],
            photo_url=row['photo_url']
        )
        session.add(pet)

    try:
        session.commit()
        print("資料已成功匯入。")
    except Exception as e:
        session.rollback()
        print(f"資料匯入錯誤: {e}")
    finally:
        session.close()

# 初始化資料庫和匯入資料
initialize_database()

# MySQL 資料庫連接配置
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="pet_database"
)



# 3. 建立 Flask 應用和 API
app = Flask(__name__)
app.secret_key = "any string"  # 設定密鑰

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("index.html")

@app.route('/ad-post')
def ad_post():
    return render_template("ad-post.html")
# API 路徑：獲取 pet_lost 表的數據

@app.route('/templates',methods=['POST', 'GET'])
def templates():

    pet_name = request.form["pet_name"]
    lost_date = request.form["lost_date"]
    lost_location = request.form["lost_location"]
    features = request.form["features"]
    contact_phone = request.form["contact_phone"]
    data = request.get_json()
    if data is None:  # 如果請求內容不是 JSON
        return jsonify({'error': 'Invalid JSON'}), 415  # 返回 415 錯誤
    latitude = float(data.get('latitude'))
    longitude = float(data.get('longitude'))

    #建立 cursor 物件，用來對資料庫下sql指令
    cursor = db.cursor()
    sql = "INSERT INTO pet_lost(pet_name, lost_date, lost_location, features,latitude ,longitude,contact_phone) VALUES (%s, %s, %s, %s,%f,%f, %s)"
    values = (pet_name, lost_date, lost_location, features,latitude ,longitude, contact_phone)
    cursor.execute(sql, values)
    db.commit()
    cursor.close()
    #css_files = [f for f in os.listdir('static') if f.endswith('.css')]
    print("資料連線成功")
    return render_template("template.html")

@app.route('/api/pet-lost', methods=['GET'])
def get_lost_pets():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM pet_lost")
    results = cursor.fetchall()
    cursor.close()
    return jsonify(results)




# 啟動應用
if __name__ == '__main__':
    app.run(debug=True)
