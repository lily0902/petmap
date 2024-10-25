import mysql.connector
from mysql.connector import errorcode
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd

# MySQL 連接設置
DB_USER = 'root'
DB_PASSWORD = '1234'
DB_HOST = 'localhost'
DB_NAME = 'pet_database'

# 建立連線來檢查資料庫是否存在
try:
    # 連接到 MySQL 伺服器（不指定資料庫）
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST)
    cursor = cnx.cursor()
    
    # 檢查是否存在資料庫
    cursor.execute(f"SHOW DATABASES LIKE '{DB_NAME}'")
    database_exists = cursor.fetchone()

    if not database_exists:
        # 如果資料庫不存在，建立資料庫
        cursor.execute(f"CREATE DATABASE {DB_NAME} DEFAULT CHARACTER SET 'utf8'")
        print(f"資料庫 '{DB_NAME}' 已建立。")
    else:
        print(f"資料庫 '{DB_NAME}' 已存在。")

    cursor.close()
    cnx.close()

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("使用者名稱或密碼錯誤")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("資料庫不存在，並無法建立")
    else:
        print(err)

# 使用 SQLAlchemy 引擎連接新資料庫並創建表格
engine = create_engine(f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')
Base = declarative_base()

class PetLost(Base):
    __tablename__ = 'pet_lost'
    
    # 定義表格的欄位
    # ... 與前面提供的 PetLost 類別相同

# 如果資料庫是新建的，則創建表格並匯入資料
Base.metadata.create_all(engine)

# 建立會話並匯入資料
Session = sessionmaker(bind=engine)
session = Session()

# 讀取 Excel 檔案
file_path = 'static/tables/pet_lost.xlsx'
excel_data = pd.read_excel(file_path)

# 清理和格式化數據
excel_data.columns = ['chip_number', 'pet_name', 'pet_type', 'gender', 'breed', 'color', 'appearance', 
                      'features', 'lost_date', 'lost_location', 'latitude', 'longitude', 
                      'owner_name', 'contact_phone', 'email', 'photo_url']

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

# 提交數據並關閉會話
session.commit()
session.close()
print("資料已成功匯入到資料庫。")
