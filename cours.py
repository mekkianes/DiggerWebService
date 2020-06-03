from flask import Flask, render_template, jsonify
import json
import requests
import yfinance as yf
import sqlite3
from threading import Thread
import sys, time




app = Flask(__name__)


conn = sqlite3.connect('alerts.db')
c = conn.cursor()

# Create table
c.execute('''CREATE TABLE IF NOT EXISTS alerts 
             (symbol text, value real, more INTEGER,treated INTEGER)''')
c.execute('DELETE FROM alerts')
conn.commit()
conn.close()


@app.route("/")        
def landing():                           
    return 'Welcome to Stock Price API',200


@app.route('/market',methods=["GET"])
def market():
    """ recupération crypto"""
    response = requests.get("https://query1.finance.yahoo.com/v7/finance/quote?symbols=BTC-USD,ETH-USD,LTC-USD,USDT-USD,XRP-USD,BCH-USD,BNB-USD,EOS-USD,ADA-USD,TRX-USD,XLM-USD")
    bit = response.json()
    crypto=[{"id":p["shortName"],"symbol":p["symbol"],"previousClose":p["regularMarketPreviousClose"],"marketOpen":p["regularMarketOpen"],"regularMarketPrice":p["regularMarketPrice"],"regularMarketChangePercent":p["regularMarketChangePercent"]} for p in  bit['quoteResponse']["result"] ]
    
    
    
    """indices boursiers"""    
    response = requests.get("https://query1.finance.yahoo.com/v7/finance/quote?symbols=^FCHI,^DJI,^IXIC,^N225,^FTSE,^GSPC,^RUT,MSFT,FB,AAPL")
    p=response.json()
    ind=[]
    for inf in p['quoteResponse']["result"] :
        ind.append({"id":inf["shortName"],"symbol":inf["symbol"],"previousClose":inf["regularMarketPreviousClose"],"marketOpen":inf["regularMarketOpen"],"regularMarketPrice":inf["regularMarketPrice"],"regularMarketChangePercent":inf["regularMarketChangePercent"]})
        
    """matieres premieres"""
    
    response = requests.get("https://query1.finance.yahoo.com/v7/finance/quote?symbols=GC=F,SI=F,HG=F,CL=F,BZ=F,NG=F,C=F,O=F,RR=F,CC=F,SB=F,OJ=F")
    p=response.json()
    mp=[]
    for inf in p['quoteResponse']["result"] :
        mp.append({"id":inf["shortName"],"symbol":inf["symbol"],"previousClose":inf["regularMarketPreviousClose"],"marketOpen":inf["regularMarketOpen"],"regularMarketPrice":inf["regularMarketPrice"],"regularMarketChangePercent":inf["regularMarketChangePercent"]})
    
    cours ={"crypto":crypto,"indice":ind,"matieres premieres":mp}
    return jsonify(cours)


@app.route("/test/")        
def test():                           
    conn = sqlite3.connect('alerts.db')
    c = conn.cursor()
    c.execute('SELECT * FROM alerts')
    records=c.fetchall()
    l=[]
    for row in records:
        l.append({"i":row})
    conn.close()
    return jsonify(l)


@app.route('/alert/<symbol>/<value>/<more>',methods=["GET","POST"])
def alert(symbol,value,more):
    conn = sqlite3.connect('alerts.db')
    c = conn.cursor()
    c.execute("INSERT INTO alerts VALUES (?,?,?,?)",(symbol,value,more,0))
    conn.commit()
    conn.close()


def get_ticker(symbol):
    response = requests.get("https://query1.finance.yahoo.com/v7/finance/quote?symbols="+symbol)
    p=response.json()
    inf=p['quoteResponse']["result"][0]
    return {"id":inf["shortName"],"previousClose":inf["regularMarketPreviousClose"],"marketOpen":inf["regularMarketOpen"],"regularMarketPrice":inf["regularMarketPrice"],"regularMarketChangePercent":inf["regularMarketChangePercent"]}
    
def get_price(symbol):
    response = requests.get("https://query1.finance.yahoo.com/v7/finance/quote?symbols="+symbol)
    p=response.json()
    inf=p['quoteResponse']["result"][0]
    return inf["regularMarketPrice"]


def send_notification(msg):
    header = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": "Basic my-rest-api-key "}
    data = {    "app_id": "my-app-id",    "included_segments": ["All"],    "contents": {"msg": msg}}
    requests.post(    "https://onesignal.com/api/v1/notifications",    headers=header,    json=data)



def handle_alert():
    """client_socket.send('Welcome to server'.encode())
    size = 1024"""
    while True:
        conn = sqlite3.connect('alerts.db')
        c = conn.cursor()
        c.execute('SELECT * FROM alerts')
        records=c.fetchall()
        l=[]
        for row in records:
            if(row[3]==0):
                value=row[1]
                symbol=row[0]
                more=row[2]
                price=get_price(symbol)
                if (price > value):
                    print("alert >= valeur precedente "+symbol+str(price==value))
                    send_notification(symbol+" price > "+value +" current price: "+price)
        conn.close()
        time.sleep(10)

ThreadAlrt=Thread(target=handle_alert, args=())
ThreadAlrt.start()


    




if __name__ == "__main__":        # on running python app.py
    app.run(debug=True, port=5000,threaded=True)






