# *******************************************
# APP: EO-RIPPER.py                       ***
# AUTHOR: Jorge Websec                    ***
# TWITTER: @JorgeWebsec                   ***
# Email: jorge@quantika14.com             ***
# License: GNU v3                         ***
# *******************************************

import json
import re
from typing import Dict, Generator, List, Optional

import bs4
import duckduckgo
import mechanize
import requests
import urllib3
from validate_email import validate_email

EMAILS_LIST = "emails.txt"


colores: Dict[str, str] = dict(
    header="\033[95m",
    blue="\033[94m",
    green="\033[92m",
    alert="\033[93m",
    fail="\033[91m",
    normal="\033[0m",
    bold="\033[1m",
    underline="\033[4m",
)

BROWSER = mechanize.Browser()
BROWSER.set_handle_equiv(True)
BROWSER.set_handle_gzip(True)
BROWSER.set_handle_redirect(True)
BROWSER.set_handle_referer(True)
BROWSER.set_handle_robots(False)
BROWSER.set_handle_refresh(mechanize.HTTPRefreshProcessor(), max_time=1)
BROWSER.addheaders = [
    (
        "User-agent",
        "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1",
    )
]


def get_username_email(email: str) -> str:
    email_as_list: List[str] = email.split("@")
    username: str = email_as_list[0]
    return username.replace(".", "")


def check_wordpress(email: str) -> None:
    try:
        BROWSER.open("http://wordpress.com/wp-login.php")
        BROWSER.select_form("loginform")
        BROWSER.form["log"] = email
        BROWSER.form["pwd"] = "123456"
        BROWSER.submit()

        html: bytes = BROWSER.response().read()
        soup = bs4.BeautifulSoup(html, "html.parser")
        error_divs: List[bs4.Tag] = soup.find_all("div", {"id": "login_error"})
        text_of_divs: str = "".join([element.text for element in error_divs])
        if "incorrect" in text_of_divs:
            print("|--[INFO][WordPress][CHECK][>] The account exist...")

        else:
            print("|--[INFO][WordPress][CHECK][>] Account doesn't exist...")
    except mechanize.FormNotFoundError:
        print(
            f"{colores['alert']}|--[WARNING][LinkedIn][>] Error... {colores['normal']}"
        )


def check_pastebin(email: str) -> None:
    URL = f"http://pastebin.com/search?q={email.replace(' ', '+')}"
    print(f"|--[INFO][PASTEBIN][SEARCH][>] {URL} ...")
    html: bytes = BROWSER.open(URL).read()
    soup = bs4.BeautifulSoup(html, "html.parser")
    for div in soup.find_all("div", {"class", "gsc-thumbnail-inside"}):
        print(f"|--[INFO][PASTEBIN][URL][>]{div}")


def check_duckduckgo_info(email: str) -> None:
    try:
        links: Generator = duckduckgo.search(email, max_results=10)
        for link in links:
            if "delsexo.com" not in str(link):
                print(f"|--[INFO][DuckDuckGO][SEARCH][>] {link}")
    except Exception:
        print(
            f"{colores['alert']}|--[WARNING][DUCKDUCKGO][>] Error...{colores['normal']}"
        )


def check_duckduckgo_smart_info(email: str) -> None:
    no_company = ("gmail", " hotmail", " yahoo", " protonmail", " mail")
    split1: List[str] = email.split("@")
    name: str = split1[0].replace(".", " ")
    split2: List[str] = split1[1].split(".")
    company: str = split2[0].replace(".", "")

    data: str
    if company in no_company:
        data = name
    else:
        data = f"{name} {company}"

    links: Generator = duckduckgo.search(data, max_results=10)
    for link in links:
        link_as_str = str(link)
        print(f"|--[INFO][DuckDuckGO][SMART SEARCH][>] {link_as_str}")
        if "linkedin.com/in/" in link_as_str:
            print(
                f"{colores['green']}|----[>][POSSIBLE LINKEDIN DETECT] ----{colores['normal']}"
            )
        if "twitter.com" in link_as_str:
            print(
                f"{colores['green']}|----[>][POSSIBLE TWITTER DETECT] ----{colores['normal']}"
            )
        if "facebook.com" in link_as_str:
            print(
                f"{colores['green']}|----[>][POSSIBLE FACEBOOK DETECT] ----{colores['normal']}"
            )
        if "soundcloud.com/" in link_as_str:
            print(
                f"{colores['green']}|----[>][POSSIBLE SOUNDCLOUD DETECT] ----{colores['normal']}"
            )


def check_account_twitter(email: str) -> None:
    username: str = get_username_email(email)
    URL = f"https://twitter.com/{username}"
    try:
        html: str = requests.get(URL).text
        soup = bs4.BeautifulSoup(html, "html.parser")
        for element in soup.find_all("h1"):
            text: str = element.text
            if "Sorry" in text or "Lo sentimos," in text:
                print(
                    f"|--[INFO][Twitter][{colores['blue']}"
                    f"{username}{colores['normal']}][>] Account doesn't exist..."
                )
            else:
                print(
                    f"{colores['green']}|--[INFO][Twitter][{colores['blue']}"
                    f"{username}{colores['green']}][>] The account exist. {colores['normal']}"
                )
    except urllib3.exceptions.HTTPError:
        print(
            f"{colores['alert']}|--[404 HTTP RESPONSE][Check_AccountTwitter][>] 404 HTTP Twitter error...{colores['normal']}"
        )


def check_netflix(email: str) -> None:
    try:
        BROWSER.open("https://www.netflix.com/es/login")
        BROWSER.select_form(nr=0)
        BROWSER.form["userLoginId"] = email
        BROWSER.form["password"] = "123456"
        BROWSER.submit()

        html: bytes = BROWSER.response().read()
        soup = bs4.BeautifulSoup(html, "html.parser")
        div: Optional[bs4.Tag] = soup.find("div", {"class": "ui-message-contents"})
        if div and "ninguna" in div.text:
            print("|--[INFO][NETFLIX][ES][CHECK][>] Account doesn't exist...")
        else:
            print("|--[INFO][NETFLIX][ES][CHECK][>] The account exist...")

    except Exception:
        print(
            f"{colores['alert']}|--[ERROR][Check_Netflix][>] Netflix error...{colores['normal']}"
        )


def check_amazon(email: str) -> None:
    BROWSER.open(
        "https://www.amazon.es/ap/register?showRememberMe=true&openid.pape.max_auth_age=0&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&pageId=esflex&openid.return_to=https%3A%2F%2Fwww.amazon.es%2Fgp%2Fyourstore%2Fhome%3Fie%3DUTF8%26action%3Dsign-out%26path%3D%252Fgp%252Fyourstore%252Fhome%26ref_%3Dnav_youraccount_signout%26signIn%3D1%26useRedirectOnSuccess%3D1&prevRID=8JDMFMXKWNZQKE8EYVTH&openid.assoc_handle=esflex&openid.mode=checkid_setup&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&prepopulatedLoginId=&failedSignInCount=0&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&ubid=259-8895990-3455759"
    )
    BROWSER.select_form(nr=0)
    BROWSER.form["customerName"] = "Gustavo Becquer"
    BROWSER.form["email"] = email
    BROWSER.form["password"] = "123456//eoripper"
    BROWSER.form["passwordCheck"] = "123456//eoripper"
    BROWSER.submit()

    html: bytes = BROWSER.response().read()

    soup = bs4.BeautifulSoup(html, "html.parser")
    div: Optional[bs4.Tag] = soup.find("div", {"class": "a-alert-content"})

    if div and "ya existe una cuenta" in div.text:
        print(
            f"{colores['green']}|--[INFO][AMAZON][ES][CHECK][>] Account doesn't exist...{colores['normal']}"
        )
    else:
        print("|--[INFO][AMAZON][ES][CHECK][>] The account exist...")


def check_haveibeenpwned(email: str) -> None:
    URL = f"https://haveibeenpwned.com/account/{email}"
    html: mechanize.response_seek_wrapper = BROWSER.open(URL)
    soup = bs4.BeautifulSoup(html, "html.parser")
    if soup.find(
        "div",
        {"class": "pwnedSearchResult pwnTypeDefinition pwnedWebsite panel-collapse in"},
    ):
        print("|--[INFO][HAVEIBEENPWNED][>] Your email appear in leaks...")
    else:
        print("|--[INFO][HAVEIBEENPWNED][>] Your email doesn't appear in leaks...")


def check_emailrep(email: str) -> None:
    URL = f"https://emailrep.io/{email}"
    JSON: dict = json.loads(requests.get(URL).text)
    JSON_DETAILS: dict = JSON["details"]

    print(
        f"|--[INFO][REPUTATION][>] {JSON['reputation']}\n"
        f"|--[INFO][SUSPICIUS][>] {JSON['suspicious']}\n"
        f"|--[INFO][BLACK LIST][>] {JSON_DETAILS['blacklisted']}\n"
        f"|--[INFO][MALICIUS ACTIVITY][>] {JSON_DETAILS['malicious_activity']}\n"
        f"|--[INFO][SPAM][>] {JSON_DETAILS['spam']}\n"
        f"|--[INFO][MALICIUS ACTIVITY][>] {JSON_DETAILS['malicious_activity']}\n"
        f"|--[INFO][SPOOFABLE][>] {JSON_DETAILS['spoofable']}\n"
        f"|--[INFO][SPF STRICT][>] {JSON_DETAILS['spf_strict']}\n"
        f"|--[INFO][DMARC ENFORCED][>] {JSON_DETAILS['dmarc_enforced']}"
    )

    domain: List[str] = email.split("@")
    print(
        f"|--[INFO][DOMAIN][>] Analyzing the domain {domain[1]}\n"
        f"|----[INFO][CHECK DOMAIN][>] {JSON_DETAILS['domain_exists']}\n"
        f"|----[INFO][DOMAIN REPUTATION][>] {JSON_DETAILS['domain_reputation']}\n"
        f"|----[INFO][NEW DOMAIN][>] {JSON_DETAILS['new_domain']}\n"
        f"|------[INFO][DAYS SINCE DOMAIN CREATION][>] {JSON_DETAILS['days_since_domain_creation']}\n"
        f"|------[INFO][FREE PROVIDER][>] {JSON_DETAILS['free_provider']}"
    )

    # RRSS Analyzer
    print("|--[INFO][PROFILES IN SOCIAL NETWORKS][>] Analyzing...")
    for profile in JSON_DETAILS["profiles"]:
        print(f"|------[INFO][SOCIAL NETWORK][>] {profile}")


# Email spoofing generator php
def generate_php(from_: str, to: str, title: str, message: str) -> None:
    php = (
        "<?php"
        f"$from      = '{from_}';"
        f"$titulo    = '{title}';"
        f"$mensaje   = '{message}';"
        f"$cabeceras = 'From: {to}' . '\r\n' ."
        "   'Reply-To: nice@eo-ripper.py' . '\r\n' ."
        "    'X-Mailer: PHP/' . phpversion();"
        "mail($from, $titulo, $mensaje, $cabeceras);"
        "echo 'Todo OK!';"
        "?>"
    )
    with open("evilmail.php", "a") as file:
        file.write(php)

    print("[|--[EO-RIPPER][SAY][>] the evilmail.php has been created!")


def menu() -> int:
    menu = (
        "\n"
        "------------------------------------------------------------------------\n"
        "--- 1. Emails list (default: emails.txt)                             ---\n"
        "--- 2. Only one target                                               ---\n"
        "--- 3. Email spoofing generate                                       ---\n"
        "------------------------------------------------------------------------\n"
    )

    while True:
        print(menu)

        try:
            answer = int(input("Select 1/2/3: "))
        except ValueError:
            print("Expected integer input")
        else:
            break

    return answer


def attack(email: str) -> None:
    email = email.replace("\n", "")

    email_is_correct: bool
    if re.match(r"^[(a-z0-9\_\-\.)]+@[(a-z0-9\_\-\.)]+\.[(a-z)]{2,15}$", email.lower()):
        print(f"[INFO][TARGET][>] Hello, {email} is correct.")
        email_is_correct = True
    else:
        print(f"[INFO][TARGET][>] Hello, {email} doesn't a email. Try again!'")
        email_is_correct = False

    if email_is_correct:
        try:
            email_is_valid: bool = validate_email(email, verify=True)
            if email_is_valid:
                print(f"[INFO][TARGET][>] {email}")
                print("|--[INFO][EMAIL][>] Email validated...")
            else:
                print(f"[INFO][TARGET][>] {email}")
                print("|--[INFO][EMAIL][>] It's not created...")
        except Exception:
            print(f"[INFO][TARGET][>] {email}")
            print(
                f"{colores['alert']}|--[INFO][EMAIL] No verification possible... {colores['normal']}"
            )

    # CALL THE ACTION
    check_emailrep(email)
    check_account_twitter(email)
    check_wordpress(email)
    check_netflix(email)
    check_amazon(email)
    check_haveibeenpwned(email)
    check_pastebin(email)
    check_duckduckgo_info(email)
    check_duckduckgo_smart_info(email)


BANNER = """
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
    - Verify LinkedIn, WordPress, Amazon[ES], Tumblr, Netflix and DDG Hacking
    - Pastebin
-------------------------------------------------------------------------------------
Date version: 09/01/2017 | Version: 1.0
Date latest version: 21/01/2017 | Version: 1.0.1
Date latest version: 27/07/2018 | Version: 1.0.9
Date latest version: 31/07/2018 | Version: 1.2.1
Date latest version: 30/01/2019 | Version: 1.2.3
Date latest version: 30/08/2019 | Version: 1.3.0
-------------------------------------------------------------------------------------
"""

if __name__ == "__main__":
    print(BANNER)
    choice: int = menu()
    if choice == 1:
        print("[INFO][Emails list][>] By default 'emails.txt'...")
        print("[INFO][Emails list][>] If you want by default, press ENTER.")
        with open(EMAILS_LIST) as file:
            for email in file.readlines():
                attack(email.replace("\n", ""))

    elif choice == 2:
        EMAIL = input("Email: ")
        attack(EMAIL)

    elif choice == 3:
        print(
            "-----------------------------------------------------\n"
            "--               START EMAIL SPOOFING\n"
            "-----------------------------------------------------\n"
            "INSTRUCTIONS:\n"
            "1. Generate evilmail.php\n"
            "2. Upload to hosting with email server\n"
            "3. Run the evilmail.php from the browser\n"
            "4. Enjoy!\n"
            "-----------------------------------------------------\n"
        )

        FROM = input("From:")
        TO = input("To: ")
        TITLE = input("Title: ")
        MESSAGE = input("Message: ")
        generate_php(FROM, TO, TITLE, MESSAGE)

    else:
        print(
            "|--[EO-RIPPER][SAY][>] Are you stupid?",
            "|--[EO-RIPPER][SAY][>] 1, 2 or 3.",
            sep="\n",
        )
