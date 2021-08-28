import smtplib
import datetime as dt
from os.path import basename
from email.message import EmailMessage
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import errors

#Unos podataka
mojmail = input("Unesite svog gmail: ") #Unesite gmail adresu
#mojpass = input("Unesite lozinku: ") #Unesite lozinku računa
mojpass = "PF7RUCF9"
primatelj = input("Unesite primatelja: ") #unesite primatelja
poruka = input("Unesite sadrzaj poruke: ")

veza = smtplib.SMTP("smtp.gmail.com","587") #službeni smtp server gmail-a, ovaj port jedino radi
veza.starttls() #stvori tls vezu s gmailom
veza.login(user=mojmail,password=mojpass) #login