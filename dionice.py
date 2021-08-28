import time
import requests #nisam siguran, ali vjerojatno treba preuzeti
import datetime as dt
from fpdf import FPDF #potrebno preuzeti


#matplotlib potrebno preuzeti
import matplotlib.pyplot as plt
import matplotlib.style as mplstyle
import matplotlib as mpl

def datumivrijeme():
	""" Funkcija vraća datum i vrijeme koje se stavlja u zaglavlje PDF stranice"""

	sada = dt.datetime.now() #dohvaća trenutni dan i vrijeme
	trenutak = f"{sada.day}.{sada.month}.{sada.year} - {sada.hour}:{sada.minute}:{sada.second}"
	return trenutak

class PDF(FPDF):
	#velicina a4 papira u mm
	SIRINA = 210
	VISINA = 297
	SLIKA_SIRINA = 160
	SLIKA_VISINA = 120

	PRORED = 8
	SIRINA_CELIJA = 40

	def header(self):
		""" Definiramo svojstva i što će sve biti u zaglavlju stranice."""

		self.set_font("Arial","B",12)
		self.cell(0,10,datumivrijeme(),0,0,'L')
		#self.cell(0,10,"Izvjestaj",0,0,'C')
		self.cell(0,10,"Generirao: Patrik Horvatic",0,0,'R')
		self.ln(20)


	def footer(self):
		""" Definiramo svojstva i što će sve biti u podnožju stranice."""

		self.set_y(-15)
		self.set_font("Arial", "I", 10)
		self.cell(0,10,f"Strana {self.page_no()}",0,0,'C')	


	def naslov(self, simbol):
		""" Dodaje naslov na stranicu."""
		self.set_font("Arial", 'B', 16)
		self.cell(0,16,txt=f"{simbol} - stanje dionica", align='C')
		self.ln(12)


	def dodajtekst(self, tekst):
		""" Dodaje tekst na stranicu, odnosno opis poduzeća"""
		#self.set_xy(10.0,80.0)
		self.set_text_color(0,0,0)
		self.set_font("Arial", '', 12)
		self.multi_cell(w=0,h=10,txt=tekst,border=0,align='J',fill=False)


	def dodajtablicu(self, datumi, vrijednosti):
		""" Dodaje tablicu u kojoj se nalazi podaci u opsegu kojeg je korisnik definirao.
		Ti podaci su, logično, i na grafu ispod."""

		self.datumi = datumi
		self.vrijednosti = vrijednosti
		# print(datumi)
		# print(vrijednosti)
		
		self.set_font("Arial", '', 10)
		self.cell(w=self.SIRINA_CELIJA,h=self.PRORED,txt="Datum",align='C',border=1)
		self.cell(w=self.SIRINA_CELIJA,h=self.PRORED, txt="Vrijednost dionice",align='C',border=1)
		self.ln(self.PRORED)

		for i in range(0,len(self.datumi)):
			self.cell(self.SIRINA_CELIJA,self.PRORED,txt=self.datumi[i],align='C',border=1)
			self.cell(self.SIRINA_CELIJA,self.PRORED,txt=str(self.vrijednosti[i]),align='C',border=1)
			self.ln(self.PRORED)
		
		self.ln(self.PRORED*2)
		self.set_font("Arial", '', 12)

	def dodajsliku(self, slika):
		""" Dodaje sliku, odnosno grafikon vrijednosti dionica."""
		self.image(name=slika,w=self.SLIKA_SIRINA,h = self.SLIKA_VISINA,type="PNG")

class Dionica:

	ALPHA_STRANA = "https://www.alphavantage.co/query" #u dokumentaciji
	KLJUC_ALPHA = "RQMMKH99D6UVQVJA" #staviti svoj kljuc dobiven prilikom registracije
	
	def __init__(self, simbol, opseg):
		"""Kod inicijalizacije objekta spremamo simbol, odnosno dionicu čije podatke trebamo.
		Opseg predstavlja broj prethodnih mjeseci koje želimo obuhvatiti u našem izvještaju."""
	
		self.simbol = simbol
		self.opseg = opseg
		
		#parametri za dohvaćanja podataka vrijednosti dionica 
		self.parametriBurza = {
			"function": "TIME_SERIES_MONTHLY_ADJUSTED",
			"symbol": self.simbol,
			"datatype": "json",
			"apikey": self.KLJUC_ALPHA
		}
		#parametri za dohvaćanja podataka o kompaniji
		self.paramteriKompanija = {
			"function": "OVERVIEW",
			"symbol": self.simbol,
			"apikey": self.KLJUC_ALPHA
		}


	def dohvatipodatke(self):
		"""Metoda za dohvaćanje podataka i uspostave veze."""

		#dohvati podatke s burze
		self.odgovorBurza = requests.get(url=self.ALPHA_STRANA, params=self.parametriBurza)
		self.odgovorBurza.raise_for_status()
		print(f"[{self.simbol}] - odgovor servera za burzu: {self.odgovorBurza.status_code}") #dohvati status kod, ako je 200 je dobro
		
		#dohvati podatke o poduzeću
		self.odgovorKompanija = requests.get(url=self.ALPHA_STRANA, params=self.paramteriKompanija)
		self.odgovorBurza.raise_for_status()
		print(f"[{self.simbol}] - odgovor servera za kompaniju: {self.odgovorKompanija.status_code}")


	def spremipodatke(self):
		""" Sprema podatke u JSON datoteku."""

		#varijablu tekst koristimo u PDF. Ovaj string sadrži osnovne informacije o poduzeću
		self.tekst = ""

		#spremi podatke kao json i spremi ih u datoteku
		self.podaciBurza = self.odgovorBurza.json()
		self.podaciKompanija = self.odgovorKompanija.json()
		
		#U strukturi podataka koja nam je poslana, dolazimo do broja zaposlenih.
		#Kada dođemo do broja zaposlenih, petlja se prekida.
		#https://www.alphavantage.co/query?function=OVERVIEW&symbol=IBM&apikey=demo

		for kljuc,vrijednost in self.podaciKompanija.items():
			if kljuc != "FullTimeEmployees":
				self.tekst += f"{kljuc}: {vrijednost}"
				self.tekst += "\n"
			else:
				break

		#spremi podatke s burze u datoteku
		with open("podaci.json", "w", encoding="utf8") as datoteka:
			datoteka.write(str(self.podaciBurza))
			datoteka.close()


	def obradipodatke(self):
		""" Obrađuje podatke. Dohvaća specifičan podatak --> 4. close <--
		Ovaj podatak predstavlja vrijednost dionice prilikom zatvaranja burze zadnjeg radnog dana u mjesecu.
		"""

		self.datumi = []
		self.vrijednosti_dionice = []

		#dohvati sve vrijednosti dionice prilikom zatvaranja burze, odnosno tradea
		for k1,v1 in self.podaciBurza["Monthly Adjusted Time Series"].items():
			self.datumi.append(k1)
			self.vrijednosti_dionice.append(float(v1.get("4. close")))
		
		#radimo reverse
		self.datumi.reverse()
		self.vrijednosti_dionice.reverse()


	def nacrtajispremigraf(self):
		"""Crta graf i sprema njegovu sliku. Na slici se nalazi opseg podataka koji
		je korisnik definirao."""

		#crtamo graf
		fig = plt.gcf()
		plt.xlabel("Datum") 							#dodaj naziv x osi
		plt.ylabel("Vrijednost dionice u tisucama $")   #dodaj naziv y osi
		plt.title(f"Vrijednosti dionica {self.simbol}") #daj ime grafu

		plt.plot_date(self.datumi[-self.opseg:-1:1],
		self.vrijednosti_dionice[-self.opseg:-1:1],
		linestyle="solid") 				 #nacrtaj graf
		
		plt.grid(True)					 #dodaj mrežu
		plt.xticks(rotation=90) 		 #rotiraj datume za 90 stupnjeva
		plt.margins(0.03) 				 #dodaj margine grafu, potrebno jer inače reže datume i naziv x osi
		plt.subplots_adjust(bottom=0.25) #dodaj više prostora na dnu kako se nebi izrezali datumi i ime x osi
		fig.set_size_inches(8,6) 		 #definiraj veličinu, potrebno radi dimenzija i veličine slike u px
		
		plt.savefig(f"Grafovi/{self.simbol} vrijednosti dionica.png",format="png", orientation="landscape", dpi=300) #spremi sliku u PNG
		self.slika = f"Grafovi/{self.simbol} vrijednosti dionica.png" #putanja gdje je slika spremljena, potrebna za unos slike u PDF
		plt.clf() #ocisti graf


	def generirajizvjesce(self):
		pdf = PDF(orientation="P",
		unit="mm",
		format="A4")  							#stvori PDF objekt
		
		pdf.set_margins(25,25,25) 				#margine 25mm sa svih strana, defaultno u wordu
		pdf.set_author("Patrik Horvatic") 		#postavi autora
		pdf.alias_nb_pages()
		pdf.add_page()							#potrebno dodati barem jednu stranicu da radi. dalje automatski dodaje
		pdf.naslov(self.simbol)					#dodajemo naslov
		pdf.dodajtekst(self.tekst)				#dodajemo tekst, odnosno podatke o poduzeću
		
		pdf.dodajtablicu(self.datumi[-self.opseg:-1:1], 
		self.vrijednosti_dionice[-self.opseg:-1:1]) #dodajemo tablicu, prosljeđujemo samo podatke u opsegu
		
		pdf.dodajsliku(self.slika) 				#dodajemo graf
		pdf.output(f"Izvjestaji/{self.simbol} - izvjestaj.pdf","F") #spremamo PDF u mapu Izvjestaji


#--------------GLAVNI DIO PROGRAMA--------------------------

#Unos korisnika mora bii pravilan prema NASDAQ-u
#https://datahub.io/core/nasdaq-listings#resource-nasdaq-listed-symbols

#korisnik unosi simbole, 0 prekida petlju
unos = False
simboli = []
while True:
	inp = input("Unesi simbol koji zelis dodati: ").upper() #simbol mora biti u velikim slovima
	if inp == "0":
		break
	else:
		simboli.append(inp)
print(simboli)
opseg = int(input("Unesi opseg (broj zadnjih mjeseci): "))


#stvori objekte
dionice = []
for simbol in simboli:
	dionice.append(Dionica(simbol,opseg))

for i in range(0,len(dionice)):
	dionice[i].dohvatipodatke()
	dionice[i].spremipodatke()
	dionice[i].obradipodatke()
	dionice[i].nacrtajispremigraf()
	dionice[i].generirajizvjesce()
	sekundi = 10
	for _ in range(0,sekundi):
		print(f"Cekam radi API... {sekundi} sekundi do novog poziva.")
		sekundi -= 1
		time.sleep(1)
