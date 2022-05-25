import requests
import json
from bs4 import BeautifulSoup

def get_soup(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}
    html_content = requests.get(url, headers=headers).text
    soup = BeautifulSoup(html_content,"html.parser")
    return soup

def get_company_urls(soup):
    return soup.find_all("a", class_="newsread")

def get_data(soup):
    contents =  soup.find_all("div", class_="shadow24")
    data = ""
    for item in contents:
        data += item.text
    return data

# uncomment the below line when executing and comment the other one
# insurances = ["life-insurance/term-insurance","life-insurance","health-insurance","investment","car-insurance","bike-insurance"]
insurances = ["life-insurance"]
url = "https://www.insurancedekho.com"
final_output = {}
for item in insurances:
    soup = get_soup(url+"/"+item)
    content = []
    for company in get_company_urls(soup)[:-5]:
        soup2 = get_soup(url+company.get('href'))
        content.append({"company": company.get('title'), "doc" : get_data(soup2)})
    final_output[item] = content
json_object = json.dumps(final_output, indent = 4)
with open("./output/output.json","w+") as f:
    f.write(json_object)
