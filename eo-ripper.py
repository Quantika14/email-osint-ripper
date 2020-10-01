#*******************************************
#APP: Email OSINT Ripper                 ***
#AUTHOR: Jorge Websec                    ***
#TWITTER: @JorgeWebsec                   ***
#Email: jorge@quantika14.com             ***
#License: GNU v3                         ***
#*******************************************

import re, mechanize, json, urllib.request, urllib.error, urllib.parse, requests
from bs4 import BeautifulSoup
from validate_email import validate_email
import csv, operator

import modules.config as C
import modules.regex as R

br = mechanize.Browser()
br.set_handle_equiv( True ) 
br.set_handle_gzip( True ) 
br.set_handle_redirect( True ) 
br.set_handle_referer( True ) 
br.set_handle_robots( False ) 
br.set_handle_refresh( mechanize._http.HTTPRefreshProcessor(), max_time = 1 ) 
br.addheaders = [ ( 'User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1' ) ] 


def get_usernameEmail(email):
	email = email.split("@")
	username = email[0]
	return username.replace(".","")

def check_wordpress(email):
	try:
		r = br.open('http://wordpress.com/wp-login.php')
		br.select_form("loginform")
		br.form["log"] = email
		br.form["pwd"] = "123456"
		br.submit()
		respuestaWP = br.response().geturl()
		html =  br.response().read()
		soup = BeautifulSoup(html, "html.parser")
		divError = soup.findAll("div", {"id": "login_error"})
		div = R.remove_tags(str(divError))
		if "incorrect" in div:
			print("|--[INFO][WordPress][CHECK][>] The account exist...")

		if "Invalid" in div:
			print("|--[INFO][WordPress][CHECK][>] Account doesn't exist...")
	except:
		print(C.colores.alert + "|--[WARNING][LinkedIn][>] Error..." + C.colores.normal)

def check_pastebin(email):
	url = "http://pastebin.com/search?q=" + email.replace(" ", "+")
	print("|--[INFO][PASTEBIN][SEARCH][>] " + url + "...")
	try:
		html = br.open(url).read()
		soup = BeautifulSoup(html, "html.parser")
		for div in soup.findAll("div", {"class", "gsc-thumbnail-inside"}):
			print("|--[INFO][PASTEBIN][URL][>]" + str(div))
	except urllib.error.HTTPError:
		print(C.colores.alert + "|--[404 HTTP RESPONSE][check_pastebin][>] 404 HTTP Pastebin error..." + C.colores.normal)

def check_AccountTwitter(email):
	username = get_usernameEmail(email)
	url = "https://twitter.com/" + username
	try:
		html = requests.get(url).text
		soup = BeautifulSoup(html, "html.parser")
		for text in soup.findAll("h1"):
			text = R.remove_tags(str(text))
			if "Sorry" in text or "Lo sentimos," in text:
				print("|--[INFO][Twitter][" + C.colores.blue+ username + C.colores.normal + "][>] Account doesn't exist...")
			else:
				print(C.colores.green + "|--[INFO][Twitter][" + C.colores.blue+ username + C.colores.green + "][>] The account exist." + C.colores.normal)
	except urllib.error.HTTPError:
		print(C.colores.alert + "|--[404 HTTP RESPONSE][Check_AccountTwitter][>] 404 HTTP Twitter error..." + C.colores.normal)

def check_netflix(email):
	try:
		r = br.open('https://www.netflix.com/es/login')
		br.select_form(nr=0)
		br.form["userLoginId"] = email
		br.form["password"] = "123456"
		br.submit()
		respuestaURL = br.response().geturl()
		html =  br.response().read()
		soup = BeautifulSoup(html, "html.parser")
		div = soup.find("div",{"class":"ui-message-contents"})
		if "ninguna" in R.remove_tags(str(div)):
			print("|--[INFO][NETFLIX][ES][CHECK][>] Account doesn't exist...")
		else:
			print("|--[INFO][NETFLIX][ES][CHECK][>] The account exist...")
	except:
		print(C.colores.alert + "|--[ERROR][Check_Netflix][>] Netflix error..." + C.colores.normal)

def check_haveibeenpwned(email):
	url = "https://haveibeenpwned.com/account/" + email
	html = br.open(url)
	soup = BeautifulSoup(html, "html.parser")
	if soup.find("div", {"class": "pwnedSearchResult pwnTypeDefinition pwnedWebsite panel-collapse in"}):
		print("|--[INFO][HAVEIBEENPWNED][>] Your email appear in leaks...")
	else:
		print("|--[INFO][HAVEIBEENPWNED][>] Your email doesn't appear in leaks...")

def check_facebook(email):

	r = br.open('https://mbasic.facebook.com/')
	br.select_form(nr=0)
	br.form["email"] = email
	br.form["pass"] = "123456"
	br.submit()
	respuestaURL = br.response().geturl()

	html =  br.response().read()
	soup = BeautifulSoup(html, "html.parser")
	div = soup.find("div",{"id":"login_error"})
	if "ninguna" in R.remove_tags(str(div)):
		print("|--[INFO][FACEBOOK][CHECK][>] Account doesn't exist...")
	else:
		print("|--[INFO][FACEBOOK][CHECK][>] The account exist...")


def check_emailrep(email):
	url = "https://emailrep.io/" + email
	JSON = json.loads(requests.get(url).text)
	try:
		print("|--[INFO][REPUTATION][>] " + JSON["reputation"])
		print("|--[INFO][SUSPICIUS][>] " + str(JSON["suspicious"]))
		print("|--[INFO][BLACK LIST][>] " + str(JSON["details"]["blacklisted"]))
		print("|--[INFO][MALICIUS ACTIVITY][>] " + str(JSON["details"]["malicious_activity"]))
		print("|--[INFO][SPAM][>] " + str(JSON["details"]["spam"]))
		print("|--[INFO][MALICIUS ACTIVITY][>] " + str(JSON["details"]["malicious_activity"]))
		print("|--[INFO][SPOOFABLE][>] " + str(JSON["details"]["spoofable"]))
		print("|--[INFO][SPF STRICT][>] " + str(JSON["details"]["spf_strict"]))
		print("|--[INFO][DMARC ENFORCED][>] " + str(JSON["details"]["dmarc_enforced"]))

		DOMAIN = email.split("@")
		print("|--[INFO][DOMAIN][>] Analyzing the domain " + DOMAIN[1])
		print("|----[INFO][CHECK DOMAIN][>] " + str(JSON["details"]["domain_exists"]))
		print("|----[INFO][DOMAIN REPUTATION][>] " + str(JSON["details"]["domain_reputation"]))
		print("|----[INFO][NEW DOMAIN][>] " + str(JSON["details"]["new_domain"]))
		print("|------[INFO][DAYS SINCE DOMAIN CREATION][>] " + str(JSON["details"]["days_since_domain_creation"]))
		print("|------[INFO][FREE PROVIDER][>] " + str(JSON["details"]["free_provider"]))

		#RRSS Analyzer
		print("|--[INFO][PROFILES IN SOCIAL NETWORKS][>] Analyzing...")
		for profile in JSON["details"]["profiles"]:

			print("|------[INFO][SOCIAL NETWORK][>] " + profile)

		if JSON["details"]["credentials_leaked"]:
			C.count_leaked += 1
		if "Spotify" in JSON["details"]["profiles"]:
			C.count_spotify += 1
	
	except:
		print("Exceeded daily limit. You can continue using the application with Dante's Gates Mobile here: https://play.google.com/store/apps/details?id=com.quantika14.dantes_gates_mobile&gl=ES")


# Email spoofing generator php
def generate_php(fromm, to, title, messaje):
	php = """<?php
$from      = '""" + fromm + """';
$titulo    = '""" + title + """';
$mensaje   = '""" + messaje + """';
$cabeceras = 'From: """ + to + """' . "\r\n" .
    'Reply-To: nice@eo-ripper.py' . "\r\n" .
    'X-Mailer: PHP/' . phpversion();

mail($from, $titulo, $mensaje, $cabeceras);
echo "Todo OK!";
?>"""
	f = open("evilmail.php", "a");
	f.write(php)
	f.close()
	print("[|--[EO-RIPPER][SAY][>] the evilmail.php has been created!")

def banner():
	print("""
███████╗ ██████╗       ██████╗ ██╗██████╗ ██████╗ ███████╗██████╗    ██████╗ ██╗   ██╗
██╔════╝██╔═══██╗      ██╔══██╗██║██╔══██╗██╔══██╗██╔════╝██╔══██╗   ██╔══██╗╚██╗ ██╔╝
█████╗  ██║   ██║█████╗██████╔╝██║██████╔╝██████╔╝█████╗  ██████╔╝   ██████╔╝ ╚████╔╝ 
██╔══╝  ██║   ██║╚════╝██╔══██╗██║██╔═══╝ ██╔═══╝ ██╔══╝  ██╔══██╗   ██╔═══╝   ╚██╔╝  
███████╗╚██████╔╝      ██║  ██║██║██║     ██║     ███████╗██║  ██║██╗██║        ██║   
╚══════╝ ╚═════╝       ╚═╝  ╚═╝╚═╝╚═╝     ╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝╚═╝        ╚═╝
      Author: Jorge Websec | Twitter: @JorgeWebsec | jorge.coronado@quantika14.com
-------------------------------------------------------------------------------------
[!]What can I know with your email?
    - Only 1 email or emails list
    - Verify emails
    - Verify LinkedIn, WordPress, Spotify, Tumblr, Netflix, Pinterest, 
    - Pastebin
-------------------------------------------------------------------------------------
Date version: 09/01/2017 | Version: 1.0
Date latest version: 21/01/2017 | Version: 1.0.1
Date latest version: 27/07/2018 | Version: 1.0.9
Date latest version: 31/07/2018 | Version: 1.2.1
Date latest version: 30/01/2019 | Version: 1.2.3
Date latest version: 30/08/2019 | Version: 1.3.0
Date latest version: 30/09/2019 | Version: 1.4.1
Date latest version: 09/03/2020 | Version: 1.5.1
-------------------------------------------------------------------------------------
""")

def menu():
	print("")
	print("------------------------------------------------------------------------")
	print("--- 1. Emails list (default: emails.txt)                             ---")
	print("--- 2. Only one target                                               ---")
	print("--- 3. Email spoofing generate                                       ---")
	print("------------------------------------------------------------------------")
	print("")
	x = int(input("Select 1/2/3: "))
	if type(x) != int:
		print("[Warning][Menu][>] Error...")
		menu()
	else:
		return x

def attack(email):
	email = email.replace("\n", "")

	if R.check_email(email):
		print("[INFO][TARGET][>] Hello, " + email + " is correct.")
		
		print("[INFO][TARGET][>] " + email)
		print("|--[INFO][EMAIL][>] Email validated...")

		#CALL THE ACTION
		check_emailrep(email)
		check_AccountTwitter(email)
		check_wordpress(email)
		check_netflix(email)
		check_haveibeenpwned(email)
		check_pastebin(email)
		check_facebook(email)

	else:
		print("[INFO][TARGET][>] Hello, " + email + " doesn't a email. Try again!'")

def main():
	global emails_list
	banner()
	m = menu()
	if m == 1:
		print("[INFO][Emails list][>] By default 'emails.txt'...")
		print("[INFO][Emails list][>] If you want by default, press ENTER.")
		file = open(C.dir_listEmails, 'r')
		for email in file.readlines():
			attack(email.replace("\n", ""))

	if m == 2:
		email = str(input("Email: "))
		attack(email)
	if m == 3:
		print("-----------------------------------------------------")
		print("--               START EMAIL SPOOFING                ")
		print("-----------------------------------------------------")
		print("INSTRUCTIONS: ")
		print("1. Generate evilmail.php")
		print("2. Upload to hosting with email server")
		print("3. Run the evilmail.php from the browser")
		print("4. Enjoy!")
		print("-----------------------------------------------------")
		print(" ")

		fromm = str(input("From:"))
		to = str(input("To: "))
		title = str(input("Title: "))
		messaje = str(input("Messaje: "))
		generate_php(fromm, to, title, messaje)

	if m <0 or m > 3:
		print("|--[EO-RIPPER][SAY][>] Are you stupid?")
		print("|--[EO-RIPPER][SAY][>] 1 or 2 or 3.")
	if type(m) == str:
		print("|--[EO-RIPPER][SAY][>] Are you stupid?")
		print("|--[EO-RIPPER][SAY][>] 1 or 2 or 3.")

if __name__ == "__main__":
	main()
