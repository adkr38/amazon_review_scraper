import requests
from bs4 import BeautifulSoup

def get_proxy_dict_for_requests_module():
    proxies = []
    response = requests.get("https://sslproxies.org/")
    soup = BeautifulSoup(response.content, "lxml")
    table = soup.find("table",{"class":"table table-striped table-bordered"})
    for row in table.tbody.find_all('tr'):
        proxies.append({
            'ip':   row.find_all('td')[0].string,
            'port': row.find_all('td')[1].string
        })

    output = [{'http':'http://'+proxy['ip']+':'+proxy['port']} for proxy in proxies]
    # output = ['http://'+proxy['ip']+':'+proxy['port'] for proxy in proxies]
    return output

def get_amazon_countries_dict():

    return {
        'Base': 'amazon.com',
        'Australia' : 'amazon.com.au',
        'Austria' : 'amazon.at',
        'Brazil': 'amazon.com.br',
        'Canada':	'amazon.ca',
        'China':'amazon.cn',
        'Czech Republic': 'amazon.cz',
        'Egypt':	'amazon.eg',
        'France':	'amazon.fr',
        'Germany':'amazon.de',
        'India'	: 'amazon.in',
        'Italy':	'amazon.it',
        'Japan':	'amazon.co.jp',
        'Mexico':	'amazon.com.mx',
        'Netherlands':	'amazon.nl',
        'Poland':	'amazon.pl',
        'Singapore'	:'amazon.com.sg',
        'Spain':	'amazon.es',
        'United Arab Emirates':	'amazon.ae',
        'United Kingdom / Ireland':	'amazon.co.uk'}