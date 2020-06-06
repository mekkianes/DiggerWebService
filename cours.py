from flask import Flask, render_template, jsonify,request
import json
import requests
import yfinance as yf
import sqlite3
from threading import Thread
import sys, time


appId="7b5b7317-d2c6-4df7-8708-4256a7f306a0"
apiKey="MWI3ZjE3NGItYmRiMi00NDg5LWEwMDYtMjczOTQwMGU4MTNl"


app = Flask(__name__)


conn = sqlite3.connect('alerts.db')
c = conn.cursor()

# Create table for saving alerts 
c.execute('''CREATE TABLE IF NOT EXISTS alerts 
             ( id INTEGER PRIMARY KEY AUTOINCREMENT,symbol text, value real, more INTEGER,deviceId text,treated INTEGER)''')
#c.execute('DELETE FROM alerts')
conn.commit()
conn.close()


@app.route("/")        
def landing():                           
    return 'Welcome to Market Stock Price API',200

"""marlet stock price """
@app.route('/market',methods=["GET"])
def market():
    """ recupération crypto"""
    crpm="BTC-USD,ETH-USD,LTC-USD,USDT-USD,XRP-USD,BCH-USD,BNB-USD,EOS-USD,ADA-USD,TRX-USD,XLM-USD"
    response = requests.get("https://query1.finance.yahoo.com/v7/finance/quote?symbols="+crpm)
    bit = response.json()
    crypto=[{"id":p["shortName"],"symbol":p["symbol"],"previousClose":p["regularMarketPreviousClose"],"marketOpen":p["regularMarketOpen"],"regularMarketPrice":p["regularMarketPrice"],"regularMarketChangePercent":p["regularMarketChangePercent"],"image":p["coinImageUrl"]} for p in  bit['quoteResponse']["result"] ]
    
    
    
    """indices boursiers"""    
    inb="^FCHI,^DJI,^IXIC,^N225,^FTSE,^GSPC,^RUT,MSFT,FB,AAPL"
    response = requests.get("https://query1.finance.yahoo.com/v7/finance/quote?symbols="+inb)
    p=response.json()
    ind=[]
    for inf in p['quoteResponse']["result"] :
        ind.append({"id":inf["shortName"],"symbol":inf["symbol"],"previousClose":inf["regularMarketPreviousClose"],"marketOpen":inf["regularMarketOpen"],"regularMarketPrice":inf["regularMarketPrice"],"regularMarketChangePercent":inf["regularMarketChangePercent"],"image":""})
        
    """matieres premieres"""
    mt="GC=F,SI=F,HG=F,CL=F,BZ=F,NG=F,C=F,O=F,RR=F,CC=F,SB=F,OJ=F"
    response = requests.get("https://query1.finance.yahoo.com/v7/finance/quote?symbols="+mt)
    p=response.json()
    mp=[]
    for inf in p['quoteResponse']["result"] :
        mp.append({"id":inf["shortName"],"symbol":inf["symbol"],"previousClose":inf["regularMarketPreviousClose"],"marketOpen":inf["regularMarketOpen"],"regularMarketPrice":inf["regularMarketPrice"],"regularMarketChangePercent":inf["regularMarketChangePercent"],"image":""})
    
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

@app.route("/getalerts/")        
def getalerts():                           
    conn = sqlite3.connect('alerts.db')
    c = conn.cursor()
    c.execute('SELECT * FROM alerts')
    records=c.fetchall()
    l=[]
    for row in records:
        
        l.append({"id":row[0],"stock":row[1],"value":row[2],"more":(row[3]==1),"deviceId":row[4]})
    conn.close()
    return jsonify(l)

@app.route("/deletealert/<id>")        
def deletealert(id):                           
    conn = sqlite3.connect('alerts.db')
    c = conn.cursor()
    c.execute("DELETE FROM alerts WHERE id = ? ",id)
    conn.commit()
    conn.close()
    return "alert deleted"

@app.route("/getalertsUsr/<user>")        
def getalertsUsr(user):                           
    conn = sqlite3.connect('alerts.db')
    c = conn.cursor()
    c.execute("SELECT * FROM alerts WHERE deviceId = '%s'" % user)
    records=c.fetchall()
    l=[]
    for row in records:
        
        l.append({"id":row[0],"stock":row[1],"value":row[2],"more":(row[3]==1),"deviceId":row[4]})
    conn.close()
    return jsonify(l)


@app.route("/req/",methods=["POST"])        
def req():                           
    data=request.json
    print(data["stock"])


@app.route('/saveAlert',methods=["POST"])
def saveAlert():
    data = request.json
    if (data["more"]==True):
        more=1
    else:
        more=0
    conn = sqlite3.connect('alerts.db')
    c = conn.cursor()
    c.execute("INSERT INTO alerts(symbol,value,more,deviceId,treated) VALUES (?,?,?,?,?)",(data["stock"],data["value"],more,data["deviceId"],0))
    conn.commit()
    conn.close()
    return "Alert saved"


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


def send_notification(msg,user):
    
    header = {"Content-Type": "application/json; charset=utf-8",
          "Authorization": "Basic MWI3ZjE3NGItYmRiMi00NDg5LWEwMDYtMjczOTQwMGU4MTNl"}

    payload = {"app_id": "7b5b7317-d2c6-4df7-8708-4256a7f306a0",
           "include_player_ids": [user],
           "contents": {"en": msg}}
 
    req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))
    print(req.status_code, req.reason)



def handle_alert():
    """///"""
    while True:
        conn = sqlite3.connect('alerts.db')
        c = conn.cursor()
        c.execute('SELECT * FROM alerts')
        records=c.fetchall()
        l=[]
        if (records):
            for row in records:
                if(row[5]==0):
                    id=row[0]
                    value=row[2]
                    symbol=row[1]
                    more=row[3]
                    userid=row[4]
                    try:
                        price=get_price(symbol)
                    except:
                        print("symbol not found")
                    if (more!=0):    
                        if (price > value):
                            send_notification("Alert !!! "+symbol+" price > "+str(value) +" current price: "+str(price),userid)
                            c.execute('''UPDATE alerts SET treated = ? WHERE id = ?''', (1, id))
                            conn.commit()
                    else:
                        if (price < value):
                            send_notification("Alert !!! "+symbol+" price < "+str(value) +" current price: "+str(price),userid)
                            c.execute('''UPDATE alerts SET treated = ? WHERE id = ?''', (1, id))
                            conn.commit()
                    
                    
        conn.close()
        time.sleep(10)

"""Starting background thread alert handler"""
ThreadAlrt=Thread(target=handle_alert, args=())
ThreadAlrt.start()



if __name__ == "__main__":        # on running python app.py
    app.run(debug=True, port=5002,threaded=True)






