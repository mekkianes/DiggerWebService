from flask import Flask, render_template, jsonify
import json
import requests
import yfinance as yf
import sqlite3




app = Flask(__name__)


conn = sqlite3.connect('alerts.db')
c = conn.cursor()

# Create table
c.execute('''CREATE TABLE IF NOT EXISTS alerts 
             (name text, value real, more INTEGER)''')
c.execute('DELETE FROM alerts')
conn.commit()
conn.close()


@app.route("/")        
def landing():                           
    return 'Welcome to Stock Price API',200

@app.route('/market',methods=["GET"])
def market():
    """ recupération crypto"""
    response = requests.get("https://api-pub.bitfinex.com/v2/tickers?symbols=tBTCUSD,tLTCBTC,tETHBTC,tXRPUSD,tBSVBTC,tEOSUSD,tZECUSD,tXMRUSD")
    bit = response.json()
    crypto=[{"id": p[0][1:],"BID":p[1],"ASK":p[3],"DAILY_CHANGE":p[5],"DAILY_CHANGE_RELATIVE":p[6],"LAST_PRICE":p[7],"HIGH":p[9],"LOW":p[10]} for p in bit ]
    
    """indices boursiers"""    
    ind=[]
    for c in ["^FCHI","^DJI","^IXIC","^N225","^FTSE","^GSPC","^RUT","MSFT","FB","AAPL"]:
        msft = yf.Ticker(c)
        ind.append({"id":msft.info["shortName"],"previousClose":msft.info["previousClose"],"marketOpen":msft.info["regularMarketOpen"],"regularMarketDayHigh":msft.info["regularMarketDayHigh"]})


    """matieres premieres"""
    mp=[]
    for c in ["GC=F","SI=F","HG=F","CL=F","BZ=F","NG=F","C=F","O=F","RR=F","CC=F","SB=F","OJ=F"]:
        msft = yf.Ticker(c)
        mp.append({"id":msft.info["shortName"],"previousClose":msft.info["previousClose"],"marketOpen":msft.info["regularMarketOpen"],"regularMarketDayHigh":msft.info["regularMarketDayHigh"]})
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


@app.route('/alert/<name>/<value>/<more>',methods=["GET","POST"])
def alert(name,value,more):
    conn = sqlite3.connect('alerts.db')
    c = conn.cursor()
    c.execute("INSERT INTO alerts VALUES (?,?,?)",(name,value,more))
    conn.commit()
    conn.close()

    
if __name__ == "__main__":        # on running python app.py
    app.run(debug=True, port=5000)  




