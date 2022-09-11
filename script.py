#Libraries
import RPi.GPIO as GPIO
import time
import matplotlib.pyplot as plt
from datetime import datetime
import smtplib
import psycopg2
import os
import sys
from dotenv import load_dotenv
load_dotenv()

conn = psycopg2.connect("dbname=sic user=pi")

#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER = 18
GPIO_ECHO = 15
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
 

def mailer():
    message = """
    Bumbu anda akan habis!
    """
    try:
        email = os.getenv("MAIL")
        password = os.getenv("PASS")
        recp = os.getenv("RECEPIENT")
        smtpObj = smtplib.SMTP("smtp.gmail.com", 587)
        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.login(email, password)
        smtpObj.sendmail(email, recp, message)
        print("Mail sent")
        smtpObj.quit()
    except Exception as e:
        print("Failed to send mail: ", e)

def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
    print("Starting...") 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance
 
if __name__ == '__main__':
    a = []
    x = 0
    try:
        while True:
            t = datetime.now()
            dist = distance()
            print("Distance: ", dist)

            cur = conn.cursor()
            cur.execute("SELECT time FROM data ORDER BY time DESC;")
            if dist > 4.0:
                try: 
                    tstamp = cur.fetchone()
                    dif = t - tstamp[0]
                    if (dif.total_seconds() // 3600) > 2:
                     mailer()
                    cur.execute("INSERT INTO data VALUES(%s, %s)", (t, dist))
                except Exception as e:
                    print("Error:" + str(e))
                    cur.execute("INSERT INTO data VALUES(%s, %s)", (t, dist))
                    conn.commit()
            cur.close()


            time.sleep(1)
 
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")

        GPIO.cleanup()

    plt.plot([1,2,3,4,5], a)
    plt.show()
