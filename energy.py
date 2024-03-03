import sqlite3
import requests
from urllib.parse import quote
from bs4 import BeautifulSoup
import json

template='https://www.nsenergybusiness.com/projects/power/'

conn = sqlite3.connect('energyprojects.sqlite')
cur = conn.cursor()
cur.executescript('''DROP TABLE IF EXISTS EnergyData;CREATE TABLE EnergyData( id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,project_name    TEXT ,headers TEXT,description TEXT)''')

def get_url(energy_sector):
    energy_sector= quote(energy_sector)
    url= template+'?_sf_ser=&se='+energy_sector
    return url
url=get_url('nuclear')

def get_record(card):
    atag=card.a
    project_name=atag.text
    project_page=atag.get('href')
    response = requests.get(url=project_page)
    descr= BeautifulSoup(response.text, 'html.parser')
    heads=descr.find_all('div', 'cell small-12 medium-6 large-3 row-break')
    headers=[]
    for head in heads:
        x=head.text.strip()
        headers.append(x)
    headers=''.join(headers)
    descrip=descr.find('div', 'diplay_less_para')
    descrip1=descr.find('div', 'display_remaining_content')
    description=descrip.p.text+descrip1.p.text

    record=[project_name,headers,description]

    return record

while True:
    response = requests.get(url)
    soups= BeautifulSoup(response.text, 'html.parser')
    cards=soups.find_all('h3',{'class':'h3'})
    for card in cards:
        record=get_record(card)
        project_name=record[0]
        headers=record[1]
        description=record[2]
        cur.execute('''INSERT INTO EnergyData
            (project_name, headers, description)
            VALUES ( ?, ?, ? )''',
        ( project_name, headers, description))
    conn.commit()
    try:
        url=soups.find('a','page-numbers').get('href')
    except:
        False
