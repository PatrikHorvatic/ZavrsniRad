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
mojpass = input("Unesite lozinku: ") #Unesite lozinku računa
primatelj = input("Unesite primatelja: ") #unesite primatelja
poruka = input("Unesite sadrzaj poruke: ")

#testiraj vezu. ako se javi greška, izbaci prikladnu poruku.
try:
    veza = smtplib.SMTP("smtp.gmail.com","587") #službeni smtp server gmail-a, ovaj port jedino radi
    veza.starttls() #stvori tls vezu s gmailom
    veza.login(user=mojmail,password=mojpass) #login

except smtplib.SMTPAuthenticationError:#javi grešku ako su uneseni podaci krivi, odnosno ne postoje na serveru
    print("Krivi username ili password!")
except smtplib.SMTPConnectError: #javi grešku ako se nije moguće povezati sa serverom
	print("Server je ugašen! Povezivanje neuspješno.")

#ako nema grešaka kod spajanja i logina, nastavi s procesom slanja sadržaja
else:
	try:
		#Ovdje stvaramo podnožje pošte
		vrijeme = dt.datetime.now() #dohvati trenutni datum i vrijeme
		podnozje = f"\n\nPoslano s Python3 skripte:\n{vrijeme.day}.{vrijeme.month}.{vrijeme.year}\n{vrijeme.hour}:{vrijeme.minute}"
		tekst = poruka + podnozje

		#stvori objekt poruka
		poruka = MIMEMultipart()
		poruka["From"] = mojmail #pošiljatelj
		poruka["To"] = primatelj #primatelj
		poruka["Subject"] = "Testiranje s attachmentom" #tema
		poruka.attach(MIMEText(tekst))

		#stvaramo listu datoteka koje želimo poslati
		#za datoteke izvan direktorija u kojem se skripta nalazi, potrebno je navesti apsolutnu putanju
		#datotke ne bi smijele imati razmak ili razmake u imenu.  Primjerice,  Pa trik.docx nije dobro.

		lista_datoteka = ["tekstualniformat.txt"]
		for element in lista_datoteka:

			#otvori datoteku iz liste
			with open(element, "rb") as datoteka:

				#stvori objekt prilog
				prilog = MIMEApplication(datoteka.read(), Name=basename(element))

			#priloži datoteku
			prilog["Content-Disposition"] = f"attachment; filename={basename(element)}"
			poruka.attach(prilog)
		
		#pošalji poruku
		veza.sendmail(from_addr=mojmail, to_addrs=primatelj, msg=poruka.as_string())

	except smtplib.SMTPRecipientsRefused: #ako ne postoji primatelj javi grešku
		print("Mail nije poslan. Ovaj primatelj ne postoji.")
	
	except smtplib.SMTPDataError: #javi grešku ako postoji problem s podacima
		print("Neočekivani kod greške od maila. Sadržaj maila nije dobar.")
	
	except errors.MessageError: #javi grešku ako postoji problem s porukom
		print("Greška kod poruke")
	except:
		print("Nepoznata greška")
	else:
		print("Mail uspješno poslan.", end="\n\n")
	finally:
		pass

#u bilo kojem slučaju, prekini vezu.
finally:
    veza.quit()
