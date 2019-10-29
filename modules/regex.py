import re

def emailParser(source):
    email_regex = r'([A-Za-z0-9\.\-\_]+@[A-Za-z0-9\.\-\_]+\.[A-Za-z]+)'
    return re.findall(email_regex, source)

def check_email(email):
    if re.match('^[(a-z0-9\_\-\.)]+@[(a-z0-9\_\-\.)]+\.[(a-z)]{2,15}$', email.lower()):
        return True
    else:
        return False
    
TAG_RE = re.compile(r'<[^>]+>')
def remove_tags(text):
	return TAG_RE.sub('', text)