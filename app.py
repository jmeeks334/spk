from flask import Flask, render_template, request
import time
import sqlite3
import RPi.GPIO as GPIO
#import valves_man


app = Flask(__name__)


#main page
@app.route('/')
def index():
    conn = sqlite3.connect('/var/www/html/webapp/sprinklers.db')
    c = conn.cursor()
    query = c.execute("SELECT * FROM main;")
    mainst = query.fetchone()
    c.execute ("SELECT * FROM upd;")
    upd = c.fetchall()
    updt = ' {0[0]}'.format(*upd)
    if (mainst[0] == 1):
        mainst = " On"
    else:
        mainst = " Off"
    return render_template('index.html', mainst=mainst, updt=updt)
    
@app.route('/update', methods=['POST'])
def updt():
    conn = sqlite3.connect('/var/www/html/webapp/sprinklers.db')
    c = conn.cursor()
    stat = request.form.get("james")
    print(stat)
    c.execute("UPDATE main SET state=(?);", (stat))
    conn.commit()
    conn.close
    query = c.execute("SELECT * FROM main;")
    mainst = query.fetchone()
    c.execute ("SELECT * FROM upd;")
    upd = c.fetchall()
    updt = ' {0[0]}'.format(*upd)
    if (mainst[0] == 1):
        mainst = "On"
    else:
        mainst = "Off"
    return render_template('index.html', mainst=mainst, updt=updt)
    
#manual control of single zone
@app.route('/man', methods=['POST', 'GET'])
def indx():
    conn = sqlite3.connect('/var/www/html/webapp/sprinklers.db')
    c = conn.cursor()
    man = request.form.get("ON")
    c.execute("UPDATE man SET Z=(?);", (man))
    conn.commit()
    conn.close
    query = c.execute("SELECT * FROM main;")
    mainst = query.fetchone()
    c.execute ("SELECT * FROM upd;")
    upd = c.fetchall()
    updt = ' {0[0]}'.format(*upd)
    if (mainst[0] == 1):
        mainst = "On"
    else:
        mainst = "Off"
    return render_template('index.html', mainst=mainst, updt=updt)

@app.route('/time')
def times():
    t = time.strftime("%x %X",time.localtime())
    templateData = {
        'time': t
        }
    return render_template('time.html', **templateData)
    
@app.route('/cakes')
def cakes():
    return render_template('cakes.html')

if __name__ == '__main__':
    app.run()
