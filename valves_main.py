import RPi.GPIO as GPIO
import time
import requests
import sqlite3

all_chan = (1,2,3,4,5,6,7,8)

"""seconds to turn on zones""" 
stdtime = 1200
aftime = 900

manT = 0

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(all_chan, GPIO.OUT)
GPIO.output(all_chan, 1)

#on = input('Ready (Y/N)? ')
conn = sqlite3.connect('/var/www/html/webapp/sprinklers.db')
c = conn.cursor()

vlvst = [0,0,0,0,0,0,0,0]

def morn():
    global manT
    print("Running main...")
    #on = int(input("On time: "))
    #off = int(input("Off time: "))
    while True:
        #GPIO.output(all_chan, 1)
        query = c.execute("SELECT * FROM main;")
        stat = query.fetchone()
        #print(stat[0])
        qman = c.execute("SELECT * FROM man;")
        man = qman.fetchone()
        #f (man[0] == 2):
            #print("man = ", man[0])
        for x in range(1, 9):
            vlvst[x-1] = GPIO.input(x)
        #print(vlvst)
        yr = time.localtime().tm_year
        mon = time.localtime().tm_mon
        dy = time.localtime().tm_mday
        mn = time.localtime().tm_min
        sc = time.localtime().tm_sec   
        hr = time.localtime().tm_hour 
        dt = [yr, mon, dy, hr, mn, sc]
        for i, j in enumerate(dt):
            if (j < 10):
                dt[i] = "0" + str(j)
        dt = {'yr':dt[0], 'mon':dt[1], 'dy':dt[2], 'hr':dt[3], 'mn':dt[4], 'sc':dt[5]}
        updt = str(dt['mon'])+"/"+str(dt['dy'])+"/"+str(dt['yr'])+" " + str(dt['hr'])+":"+str(dt['mn'])+":"+str(dt['sc'])
        c.execute("UPDATE upd SET time=(?);", (updt,))
        conn.commit()
        conn.close
        c.execute ("SELECT * FROM upd;")
        upd = c.fetchall()
        updte = 'Update time: {0[0]}'.format(*upd)
        #print(updte)
        if (man[0] == 0):
            GPIO.output(all_chan, 1)
            manT = 0
        else:
            for x in range (1, 9):
                if man[0] != x or manT >= 540:
                    GPIO.output(x, 1)
                    
                elif man[0] == x and manT < 540:
                    GPIO.output(x, 0)
                    manT +=1
                    print("man", x, updt, manT)
                    
        #response = requests.get("https://api.weather.gov/stations/KPNC/observations/latest").json()
        #precip1 = response['properties']['precipitationLastHour']['value']
        ##print ("...")
        
        if (hr == 4 and mn == 0 and stat[0] == 1):
            response = requests.get("https://api.synopticdata.com/v2/stations/latest?token=f1cdeb192f27430aa8544323e319df84&stid=KPNC").json()
            precip = response['STATION'][0]['OBSERVATIONS']['precip_accum_24_hour_value_1']['value']
            preciptime = response['STATION'][0]['OBSERVATIONS']['precip_accum_24_hour_value_1']['date_time']
            temp = response['STATION'][0]['OBSERVATIONS']['air_temp_value_1']['value']
            temptime = response['STATION'][0]['OBSERVATIONS']['air_temp_value_1']['date_time']
            print(str(mon)+"/"+str(dy)+"/"+str(yr)+" - "+str(hr)+":"+str(mn)+ "  Initiating morning sequence...")
            time.sleep(1)
            print("Precip(mm):", precip, preciptime)
            print("Temp(degC):", temp, temptime)
            if (precip > 1000):
                print("Rain! ...not running morning")
                time.sleep(60)
            else:
                print(" ...running morning  "+str(mon)+"/"+str(dy)+"/"+str(yr))
                for x in range (1, 9):
                    mn = time.localtime().tm_min
                    sc = time.localtime().tm_sec   
                    hr = time.localtime().tm_hour 
                    GPIO.output(x, 0)
                    print("Zone", x, "on - "+" "+str(hr)+":"+str(mn)+":"+str(sc))
                    time.sleep(stdtime)
                    mn = time.localtime().tm_min
                    hr = time.localtime().tm_hour 
                    GPIO.output(x, 1)
                    print("Zone", x, "off - "+str(hr)+":"+str(mn))
                    time.sleep(10)
                print("fin")
                time.sleep(10)
        elif (hr == 18 and mn == 0 and stat[0] == 1):
            response = requests.get("https://api.synopticdata.com/v2/stations/latest?token=f1cdeb192f27430aa8544323e319df84&stid=KPNC").json()
            precip = response['STATION'][0]['OBSERVATIONS']['precip_accum_24_hour_value_1']['value']
            preciptime = response['STATION'][0]['OBSERVATIONS']['precip_accum_24_hour_value_1']['date_time']
            temp = response['STATION'][0]['OBSERVATIONS']['air_temp_value_1']['value']
            temptime = response['STATION'][0]['OBSERVATIONS']['air_temp_value_1']['date_time']
            print(str(mon)+"/"+str(dy)+"/"+str(yr)+" - "+str(hr)+":"+str(mn)+ "  Initiating afternoon sequence...")
            time.sleep(1)
            print("Precip(mm):", precip, preciptime)
            print("Temp(degC):", temp, temptime)
            if (temp > 320):
                print("HOT!...running afternoon  "+str(mon)+"/"+str(dy)+"/"+str(yr))
                GPIO.output(8, 0)
                print("Zone 8 on")
                time.sleep(aftime)
                mn = time.localtime().tm_min
                sc = time.localtime().tm_sec   
                hr = time.localtime().tm_hour 
                GPIO.output(8, 1)
                print("Zone 8 off - "+str(hr)+":"+str(mn))
                time.sleep(10)
                GPIO.output(7, 0)
                print("Zone 7 on")
                time.sleep(aftime)
                mn = time.localtime().tm_min
                sc = time.localtime().tm_sec   
                hr = time.localtime().tm_hour 
                GPIO.output(7, 1)
                print("Zone 7 off - "+str(hr)+":"+str(mn))
                time.sleep(10)
            else:
                print("...afternoon skipped "+str(mon)+"/"+str(dy)+"/"+str(yr))
                time.sleep(60)
        elif (stat[0] == 1 and man[0] == 0):
            GPIO.output(all_chan, 1)
            time.sleep(5)
        else:
            time.sleep(5)

#if (on == "Y"):
morn()
