#!/usr/bin/env python
# coding: utf-8
# Import modules
import logging
#!pip install wikipedia-api
import wikipediaapi
#import databasesaver as dbs
import requests
import pandas as pd
import wikitextparser as wtp

# # Exportera&ladda en Pandas `DataFrame` till SQL
# 
# Import modules
import sqlite3

# Create connection to database file, no matter load or save
con = sqlite3.connect('Uppland.db')

class DatabaseSave:
    "Class to save data to SQL table."

    def __init__(self,data, connection=con) -> None:
        self.logger = logging.getLogger(__name__)
        self.data = data
        self.connection = connection
    def save_data(self):
        self.logger.info('Saving data...')
        # Save DataFrame data into table Upplands runeinscriptions in database file
        self.data.to_sql('Upplands_runeinscriptions', self.connection, if_exists='replace')
        
class DatabaseLoader:
    "Class to load data from SQL table."

    def __init__(self, connection=con) -> None:
        self.logger = logging.getLogger(__name__)
        self.connection = connection
    def load_data(self):
        self.logger.info('Loading data...')
        if pd.read_sql('SELECT name FROM sqlite_master', self.connection).empty:
            self.logger.error('Making new database due to error ...')
            # define raw columns
            return pd.DataFrame(columns=["signum", "revisionID", "translitterering", "normalisering", "translation", "Latitude", "Longitude", "Stil", "Inscriber", "Material", "Period", "edition" ]) #, "EndPeriod", "Date"
        else:
            self.logger.info('Load data: success.')
            return pd.read_sql('SELECT signum, revisionID, translitterering, normalisering, translation, Latitude, Longitude, Stil, Inscriber, Material, Period, edition FROM Upplands_runeinscriptions', self.connection)

#=========== end of Exportera&ladda en Pandas `DataFrame` till SQL ==========

def get_rev(inskrift):
    #get revision ID
    params = {'action': 'parse','page': inskrift,'format': 'json'}
    response = requests.get(URL, headers=headers, params=params)
    page_data = response.json()
    return page_data['parse']['revid']
    
def read_page(inskrift):
    # allow empty data for reading
    lat = 0
    lon = 0
    runstil = '' 
    ristare = '' 
    material = '' 
    tillkomsttid = ''
    #get plain text of a page
    p_wiki = wiki_wiki.page(inskrift)
    tmp = p_wiki.text
    #extract inskription from the text
    if tmp.find('Translitterering av runraden:') == -1:
        logger.warning('no transliteration in ', inskrift)
        #lit = ' '
    else:
        #len('Translitterering av runraden:') = 29
        lit = tmp[tmp.find('Translitterering av runraden:')+29:tmp.rfind('Normalisering till runsvenska:')].strip()
    if tmp.find('Normalisering till runsvenska:') == -1:
        logger.warning('no normalization in ', inskrift)
        norm = ' '
    else:
        norm = tmp[tmp.find('Normalisering till runsvenska:')+30:tmp.rfind('Översättning till nusvenska:')].strip()
    # now get html of a page
    p_wiki_html = wiki_wiki_html.page(inskrift)
    p_wiki_html = wiki_wiki_html.page(inskrift)
    tmp = p_wiki_html.text
    if tmp.find('<p>Översättning\xa0till nusvenska:\n</p>\n<dl><dd>') == -1:
        logger.warning('no translation in ', inskrift)
        #trans = ' '
    else:
        trans = tmp[tmp.find('<p>Översättning\xa0till nusvenska:\n</p>\n<dl><dd>')+45:tmp.rfind('</dd></dl>')].strip()
    # now get wikitext of a page
    r = requests.get('https://sv.wikipedia.org/w/api.php',
        params = {
            'action': 'parse',
            'page': inskrift,
            'contentmodel': 'wikitext',
            'prop': 'wikitext',
            'format': 'json'
            })
    data = wtp.parse(r.json()['parse']['wikitext']['*'])
    for template in data.templates:
        if template.name == 'coord':
            lat = template.arguments[0].value
            lon = template.arguments[1].value
        elif template.name[0:17] == 'Infobox fornminne':
            for arg in data.templates[0].arguments:
                if arg.name[0:9] == ' undertyp':
                    material = arg.value
                elif arg.name[0:8] == ' ristare':
                    ristare = arg.value
                elif arg.name[0:8] == ' runstil':
                    runstil = arg.value
                elif arg.name[0:13] == ' tillkomsttid':
                    tillkomsttid = arg.value
    print([inskrift, get_rev(inskrift), lit, norm, trans, lat, lon, runstil, ristare, material, tillkomsttid] )
    return [inskrift, get_rev(inskrift), lit, norm, trans, lat, lon, runstil, ristare, material, tillkomsttid]               
    #return [inskrift, get_rev(inskrift), norm, trans, lat, lon, runstil, ristare, material, begin_date, end_date, NaN]


logger = logging.getLogger(__name__)
logging.basicConfig(
    filename='pipeline.log', 
    format='[%(asctime)s][%(name)s] %(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S', 
    level=logging.WARNING) #INFO
    
# some constants
URL = f'https://sv.wikipedia.org/w/api.php'
headers = {'user-agent': 'runstenar (schizoakustik@schizoakustik.se)'}

# get the data from the previous run
logger.info('Starting data pipeline...')
data = DatabaseLoader()
df = data.load_data()

# read the category
wiki_wiki = wikipediaapi.Wikipedia('runstenar (schizoakustik@schizoakustik.se)', 'sv')
wiki_wiki_html = wikipediaapi.Wikipedia('runstenar (schizoakustik@schizoakustik.se)', 'sv', extract_format=wikipediaapi.ExtractFormat.HTML)
cat = wiki_wiki.page("Category:Upplands runinskrifter")



count=0
for c in cat.categorymembers.values():
    count = count + 1
    #limit number of pages for exercise purpose 
    if count > 20 : break
    print(c.title)
    inskrift = c.title
    #if the page is new read and save it
    if not (inskrift in df['signum'].values):
        #save the page as v = 0
        try: 
            rad = read_page(inskrift)
            rad.append(0)
            df.loc[len(df)]  = rad
        except:
            logger.warning('skipping ', inskrift)
    else:
        #if the page is newly edited check the changes
        #get revision ID
        page_rev_id = get_rev(inskrift)
        #check revisionID
        if df.loc[df['signum'] == inskrift, 'revisionID'].item() < page_rev_id:
            # we keep track of both wiki revisions and our own editions.
            try: 
                rad = read_page(inskrift)
                rad.append(df.loc[df['signum'] == inskrift,'edition'].item() + 1 )
                df.loc[df['signum'] == inskrift] = rad
            except:
                logger.warning('skipping ', inskrift)
        
# save result
output = DatabaseSave(df)
output.save_data()
