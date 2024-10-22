import json
from flask import Flask#載入 flask
from flask import request
from flask import redirect 
from flask import render_template 
from flask import session

#建立application物件,可以設定靜態檔案的路徑處理
app = Flask(__name__)

app.secret_key = "any string" #設定密鑰

#用來回應路徑 / 的處理函式
@app.route('/',methods=['GET', 'POST'])
def index():
    return render_template("index.html")

app.run()