#!/usr/bin/env python
#-*- coding:utf-8 -*-
#*******************************************
#APP: VerifyEmail-Social.py              ***
#AUTHOR: Jorge Websec                    ***
#TWITTER: @JorgeWebsec                   ***
#Email: jorge@quantika14.com             ***
#*******************************************

#Comprueba si un email existe.

import random, re, string, urllib, urllib2, mechanize, cookielib, requests, json
from urllib2 import urlopen
from bs4 import BeautifulSoup
from pygoogle import pygoogle

class colores:
    header = '\033[95m'
    blue = '\033[94m'
    green = '\033[92m'
    alert = '\033[93m'
    fail = '\033[91m'
    normal = '\033[0m'
    bold = '\033[1m'
    underline = '\033[4m'

br = mechanize.Browser()
#cj = cookielib.LWPCookieJar() 
#br.set_cookiejar(cj) 
br.set_handle_equiv( True ) 
br.set_handle_gzip( True ) 
br.set_handle_redirect( True ) 
br.set_handle_referer( True ) 
br.set_handle_robots( False ) 
br.set_handle_refresh( mechanize._http.HTTPRefreshProcessor(), max_time = 1 ) 
br.addheaders = [ ( 'User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1' ) ] 
#FUNCIONES
TAG_RE = re.compile(r'<[^>]+>')
def remove_tags(text):
    return TAG_RE.sub('', text)

def check_fb(email):
	#FACEBOOK-----------------------------------------------------
	r = br.open('https://www.facebook.com/login.php')
	br.select_form(nr=0)
	br.form["email"] = email
	br.form["pass"] = "123412341234"
	br.submit()
	respuestaFB = br.response().geturl()
	html = br.response().read()
	print "[INFO][FB][URL] " + respuestaFB
	soup = BeautifulSoup(html, "html.parser")
	for img in soup.findAll("img"):
		print img

def check_linkedin(email, state):
	#LINKEDIN-------------------------------------------------
	r = br.open('https://www.linkedin.com/')
	br.select_form(nr=0)
	br.form["session_key"] = email
	br.form["session_password"] = "123456"
	br.submit()
	respuestaLI = br.response().geturl()
	if "captcha" in respuestaLI:
		print "[INFO][LinkedIn][Captcha][>] Captcha detect!"
	html = br.response().read()
	print "[INFO][LinkedIn][URL][>] " + respuestaLI
	soup = BeautifulSoup(html, "html.parser")
	for span in soup.findAll("span", {"class", "error"}):
		data = remove_tags(str(span))
		data = data.split()
		#if data.find("Hmm, that's not the right password. Please try again or request a new one.") > 0:
		if "password" in data and state == 1:
			print "|--[INFO][LinkedIn][CHECK][>] it's possible to hack it !!!"
		else:
			print "|--[INFO][LinkedIn][CHECK][>] The Account exists..."

def check_wordpress(email, state):
	r = br.open('http://wordpress.com/wp-login.php')
	br.select_form("loginform")
	br.form["log"] = email
	br.form["pwd"] = "123456"
	br.submit()
	respuestaWP = br.response().geturl()
	html =  br.response().read()
	if "Invalid" in html and state == 1:
		print "|--[INFO][WordPress][CHECK][>] it's possible to hack it !!!"
	else:
		print "|--[INFO][WordPress][CHECK][>] The Account exists..."

def check_hesidohackeado(email):
	url = "https://hesidohackeado.com/api?q=" + email
	html = br.open(url).read()
	data = json.loads(html)
	print "[INFO][HESIDOHACKEADO][>] Results: " + str(data["results"])
	for i in range(0,data["results"]):
		print "[INFO][HESIDOHACKEADO][URL[>] " + str(data["data"][i]["source_url"])

def check_pastebin(email):
	url = "http://pastebin.com/search?q=" + email.replace(" ", "+")
	print "[INFO][PASTEBIN][SEARCH][>] " + url + "..."
	html = br.open(url).read()
	soup = BeautifulSoup(html, "html.parser")
	for div in soup.findAll("div", {"class", "gsc-thumbnail-inside"}):
		print "[INFO][PASTEBIN][URL][>]" + str(div)

def banner():
	print """
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
    - Verify LinkedIn
    - Hesidohackeado.com
    - Pastebin
-------------------------------------------------------------------------------------
Date latest version: 09/01/2017 | Version: 1.0
-------------------------------------------------------------------------------------
"""

def menu():
	print ""
	print "------------------------------------------------------------------------"
	print "--- 1. Emails list (default: emails.txt)                             ---"
	print "--- 2. Only one target                                               ---"
	print "------------------------------------------------------------------------"
	print ""
	x = int(raw_input("Select 1/2: "))
	return x

def attack(email):
	email = email.replace("\n", "")
	url = "http://www.verifyemailaddress.org/es/"
	html = br.open(url)
	br.select_form(nr=0)
	br.form['email'] = email
	br.submit()
	resp = br.response().read()
	soup = BeautifulSoup(resp, "html.parser")
	state = 0
	for li in soup.find_all('li', {'class':"success valid"}):
		verif = remove_tags(str(li))
		#print verif
		state = 1
		if state == 1:
			print "[INFO][TARGET][>] " + email
			print "|--[INFO][EMAIL][>] Email validated..."
		else:
			print "[INFO][TARGET][>] " + email
			print "|--[INFO][EMAIL][>] It's not created..."

	check_linkedin(email, state)
	check_wordpress(email, state)
	check_hesidohackeado(email)
	check_pastebin(email)

#Hilo Principal
def main():
	banner()
	m = menu()
	if m == 1:
		file = "emails.txt"
		f = open(file, "r")
		emails = f.readlines()
		for email in emails:
			attack(email)
	if m == 2:
		email = str(raw_input("Email: "))
		attack(email)


if __name__ == "__main__":
	main()
