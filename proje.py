import RPi.GPIO as GPIO
import dht11
import time
import datetime
from RPLCD import CharLCD
import smtplib
veriler=open("veriler.txt","w")
veriler.close()
GPIO.setmode(GPIO.BOARD)
instance1 = dht11.DHT11(pin=11)
instance2 = dht11.DHT11(pin=13)
GPIO.setwarnings(False)
GPIO.setup(29, GPIO.IN)
GPIO.setup(31, GPIO.IN)
GPIO.setup(33, GPIO.IN)
GPIO.setup(35, GPIO.IN)
GPIO.setup(16, GPIO.OUT)
GPIO.setup(12, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)
GPIO.setup(32, GPIO.OUT)
GPIO.setup(36, GPIO.OUT)
GPIO.setup(38, GPIO.OUT)
GPIO.setup(40, GPIO.OUT)
GPIO.output(32,0)
GPIO.output(36,0)
GPIO.output(38,0)
GPIO.output(40,0)
donmesayaci=0
bekle=10
ileri= [
    [0,0,0,1],
    [0,1,0,0],
    [0,0,1,0],
    [1,0,0,0]
    ]

def setStep(w1, w2, w3, w4):
  GPIO.output(32, w1)
  GPIO.output(36, w2)
  GPIO.output(38, w3)
  GPIO.output(40, w4)
  
p1=GPIO.PWM(12,1)
p2=GPIO.PWM(12,0,9)

msg = email.message_from_string('warning')
msg['From'] = "kuluckamakinesihesabi@hotmail.com"
msg['To'] = "muharremalibayrak@ogr.iu.edu.tr"
msg['Subject'] = "kulucka makinesi"

s = smtplib.SMTP("smtp.live.com",587)
s.ehlo() # Hostname to send for this command defaults to the fully qualified domain name of the local host.
s.starttls() #Puts connection to SMTP server in TLS mode
s.ehlo()
s.login('kuluckamakinesihesabi@hotmail.com', 'Kuluckasifresi00')

while(True):
    
    zaman =datetime.datetime.now()
    dakika=zaman.minute
    saniye=zaman.second
    saat=zaman.hour
    gun=zaman.day
    ay=zaman.month
    yil=zaman.year
    kayit=dakika+saniye
    if dakika==59 or dakika==14 or dakika==29 or dakika==44:
        if donmesayaci==1:
            donmesayaci=0
    if dakika==0 or dakika==15 or dakika==30 or dakika==45:
        if donmesayaci==0:
            step_motor_calisiyor=1
    if dakika==1 or dakika==16 or dakika==31 or dakika==46:
        if donmesayaci==1:
            donmesayaci=0        
    
    result1 = instance1.read()
    if result1.is_valid():
        icsicaklik = result1.temperature
        icnem = result1.humidity
    result2 = instance2.read()
    if result2.is_valid():
        dissicaklik = result2.temperature
        disnem = result2.humidity


    sicaklık_farkı= icsicaklik - dissicaklik
    a=(50+sicaklık_farkı*1.5)/100
    b=(sicaklık_farkı*3)/100
    p3=GPIO.PWM(12,a)
    p4=GPIO.PWM(12,b)
    if icsicaklik<=20 :
       GPIO.output(16,1)
       p1.start(1)
       p2.stop()
    elif icsicaklik<=30 :
       GPIO.output(16,1)
       p2.start(1)
       p1.stop()
       p3.stop()
    elif icsicaklik<=35 :
       GPIO.output(16,1)
       p3.start(1)
       p2.stop()
       p4.stop()
    elif icsicaklik<=36.5 :
       GPIO.output(16,1)
       p4.start(1)
       p3.stop()
    elif icsicaklik<=38 :
       GPIO.output(16,1)
       a=0
       GPIO.output(12,0)
    else :
        GPIO.output(18, 1)
        GPIO.output(16, 1)
    
    while (step_motor_calisiyor==1) :
        for i in range(0, 12):
            setStep(1, 0, 1, 0)
            time.sleep(bekle)
            setStep(0, 1, 1, 0)
            time.sleep(bekle)
            setStep(0, 1, 0, 1)
            time.sleep(bekle)
            setStep(1, 0, 0, 1)
            time.sleep(bekle)
        step_motor_calisiyor=0
        donmesayaci=1
    
    
    if step_motor_calisiyor==0 :

        hareket1=GPIO.input(29)
        hareket2=GPIO.input(31)
        hareket3=GPIO.input(33)
        hareket=hareket1+hareket2+hareket3
        if hareket!=3:
            GPIO.output(22, 1)
            hareket_uyari=1
    else :
        hareket_uyari=0


    print("iç sıcaklık={0},   dış sıcaklık={1},   nem={2},".format(icsicaklik,dissicaklik,icnem))
    if kayit==0 :
        sistem_zamani=datetime.datetime.now()
        ssaat=sistem_zamani.hour
        sgun=sistem_zamani.day
        say=sistem_zamani.month
        syil=sistem_zamani.year

        veriler=open("veriler.txt","a")
        veriler.write("{0}-{1}-{2} {3}:00      iç sıcaklık={4},   dış sıcaklık={5},   nem={6},".format(sgun,say,syil,ssaat,icsicaklik,dissicaklik,icnem))
        veriler.close()
        time.sleep(1)
    #lcd
    lcd.cursor_pos = (0, 0)
    lcd.write_string("Sıcaklık: " + icsicaklik + unichr(223) + "C")
    lcd.cursor_pos = (1, 0)
    lcd.write_string("Nem: %" + icnem)
    #lcd
    if icnem<60:
        nem_uyarisi=("{0}-{1}-{2} {3}:00 tarihinde nem çok düştü makineyi kontrol et.  nem={4},".format(gun ,ay ,yil,saat ,icnem))
        s.sendmail("kuluckamakinesihesabi@hotmail.com", "muharremalibayrak@ogr.iu.edu.tr", nem_uyarisi)
    if icsicaklik>40 or icsicaklik<20:
        sicaklik_uyarisi=("{0}-{1}-{2} {3}:00 tarihinde sıcaklıkta bir sorun oluştu makineyi kontrol et.  sıcaklık={4},".format(gun ,ay ,yil,saat ,icsicaklik))
        s.sendmail("kuluckamakinesihesabi@hotmail.com", "muharremalibayrak@ogr.iu.edu.tr", sicaklik_uyarisi)
    if hareket_uyari==1:
        hareketuyarisi=("{0}-{1}-{2} {3}:00 tarihinde hareket uyarısı alındı makineyi kontrol edin.".format(gun ,ay ,yil,saat))
        s.sendmail("kuluckamakinesihesabi@hotmail.com", "muharremalibayrak@ogr.iu.edu.tr", hareketuyarisi)
