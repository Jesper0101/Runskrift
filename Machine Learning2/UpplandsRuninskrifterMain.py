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
import re
import os

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
            return pd.DataFrame(columns=["signum", "revisionID", "translitterering", "normalisering", "translation", "Latitude", "Longitude", "Stil", "Inscriber", "Material", "Period_begin", "Period_end", "edition" ]) #, "EndPeriod", "Date"
        else:
            self.logger.info('Load data: success.')
            return pd.read_sql('SELECT signum, revisionID, translitterering, normalisering, translation, Latitude, Longitude, Stil, Inscriber, Material, Period_begin, Period_end, edition FROM Upplands_runeinscriptions', self.connection)

#=========== end of Exportera&ladda en Pandas `DataFrame` till SQL ==========

def get_rev(inskrift):
    #get revision ID
    params = {'action': 'parse','page': inskrift,'format': 'json'}
    response = requests.get(URL, headers=headers, params=params)
    page_data = response.json()
    return page_data['parse']['revid']
    
def read_page(inskrift, df_periods):
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
            if lon == 'N':
                lon = template.arguments[2].value
        elif 'Infobox fornminne' in template.name:
            for arg in template.arguments:
                if 'undertyp' in arg.name:
                    material = arg.value
                elif 'ristare' in arg.name:
                    ristare = arg.value
                elif 'runstil' in arg.name:
                    runstil = arg.value
                elif 'tillkomsttid' in  arg.name:
                    tillkomsttid = arg.value
        elif 'Runinskriftsfakta' in template.name:
            for arg in template.arguments:
                if 'ristare' in arg.name:
                    ristare = arg.value
                elif 'tillkomsttid' in arg.name:
                    tillkomsttid = arg.value
        elif 'Runskriftsöversättning' in template.name: #if template exists it will prevail over html
            for arg in template.arguments:
                if 'translitterering' in arg.name :
                    lit = arg.value
                elif "normalisering" in arg.name and "normaliseringsref" not in arg.name:
                    norm = arg.value
                elif 'översättning' in arg.name and 'översättningsref' not in arg.name:
                    trans = arg.value

    raw_of_data, df_periods = clean_data([inskrift, get_rev(inskrift), lit, norm, trans, lat, lon, runstil, ristare, material, tillkomsttid], df_periods )
    #print(raw_of_data)
    return raw_of_data, df_periods               
    #return [inskrift, get_rev(inskrift), norm, trans, lat, lon, runstil, ristare, material, begin_date, end_date, NaN]

def get_period(df_periods, period):
    # Check if the question exists in the DataFrame
    period = period.strip()
    if period == '':
        period = ' '
    if period in df_periods['Period'].values:
        period_begin = df_periods[df_periods['Period'] == period]['Period_begin'].values[0]
        period_end = df_periods[df_periods['Period'] == period]['Period_end'].values[0]
        return period_begin, period_end, df_periods
    else:
        # If the period is not found, prompt the user for the answer
        period_begin, period_end = input(f" '{period}' is not known. Please provide the answer (period_begin, period_end): ").split()
        
        # Validate the answer (check if it's two digits)
        while not (period_begin.isdigit() and period_end.isdigit()):
            period_begin, period_end = input(f" '{period}' is not known. Please provide the answer (period_begin, period_end): ").split()

        # Add the new question and answer to the DataFrame
        new_row = pd.DataFrame({'Period': [period], 'Period_begin': [period_begin],'Period_end': [period_end]})
        df_periods = pd.concat([df_periods, new_row], ignore_index=True)
        # Save the DataFrame vocabulary for periods back to the file
        df_periods.to_csv('periods.csv', index=False)
        return period_begin, period_end, df_periods

def clean_data(raw_of_data, df_periods):
    raw_of_data = [ele.strip() if isinstance(ele,str) else ele for ele in raw_of_data] #remove spaces around
    raw_of_data = [ele.replace('&nbsp,', ' ') if isinstance(ele,str) else ele for ele in raw_of_data] #replace hard spaces
    raw_of_data = [ele.replace('[[', '') if isinstance(ele,str) else ele for ele in raw_of_data]
    raw_of_data = [ele.replace(']]', '') if isinstance(ele,str) else ele for ele in raw_of_data]
    raw_of_data = [ele.replace('\n', '') if isinstance(ele,str) else ele for ele in raw_of_data]
    raw_of_data = [ele.replace('?', '') if isinstance(ele,str) else ele for ele in raw_of_data] #simplifiera saker
    
    if 'okänd' in raw_of_data[8]:
        raw_of_data[8] = ''
    raw_of_data[8] = re.sub('Lista över runristare#.', '', raw_of_data[8]) 
    raw_of_data[8] = re.sub('Lista_över_runristare#.', '', raw_of_data[8])               
    raw_of_data[8] = raw_of_data[8].replace('Lista över runristare|', '')

    raw_of_data[8] = raw_of_data[8].replace('[Stille 1999b:158]', '')
    raw_of_data[8] = raw_of_data[8].replace('<ref name=sri1/>', '')
    raw_of_data[8] = raw_of_data[8].replace('[Åhlén 2004]', '')
    raw_of_data[8] = raw_of_data[8].replace('[Åhlén 1997]', '')
    raw_of_data[8] = raw_of_data[8].replace('[Källström 1999:113]', '')
    raw_of_data[8] = raw_of_data[8].replace('<ref name="sri1"/>', '')
    raw_of_data[8] = raw_of_data[8].replace('&nbsp,', '')
    raw_of_data[8] = raw_of_data[8].replace('<ref name=rtdb/>', '')
    raw_of_data[8] = raw_of_data[8].replace(' (runristare)|', ',')
    raw_of_data[8] = raw_of_data[8].replace(' runristare', '')
    raw_of_data[8] = raw_of_data[8].replace('_runristare', '')
    raw_of_data[8] = raw_of_data[8].replace(';', ',')
    raw_of_data[8] = raw_of_data[8].replace('osignerad', '')
    raw_of_data[8] = raw_of_data[8].replace('|', ',')
    raw_of_data[8] = raw_of_data[8].replace('[Källström 1999:54f]', '')
    raw_of_data[8] = raw_of_data[8].replace('(A)', '') #big simplification
    raw_of_data[8] = raw_of_data[8].replace('(S)', '') #big simplification
    raw_of_data[8] = raw_of_data[8].replace('(', '')
    raw_of_data[8] = raw_of_data[8].replace(')', '')
    raw_of_data[8] = raw_of_data[8].strip(' ,')
    raw_of_data[10] = raw_of_data[10].replace('<!-- Skyddsinfo -->', '')
    raw_of_data[10] = raw_of_data[10].replace('<ref name="sri1"></ref>', '')
    period_begin, period_end, df_periods = get_period(df_periods, raw_of_data[10])
    raw_of_data[10] = raw_of_data[10] = period_begin
    raw_of_data.append(period_end) 
    
    stil_str = raw_of_data[7].lower()
    if 'pr' in stil_str:
        l = [m.start() for m in re.finditer('pr', stil_str)]
        new_stil_str = [stil_str[s:s+3] for s  in l]
        raw_of_data[7] = ','.join(new_stil_str)
    elif  'ringerik' in raw_of_data[7].lower():
        raw_of_data[7] = 'pr1,pr2'
    elif  'urnes' in raw_of_data[7].lower():
        raw_of_data[7] = 'pr3,pr4,pr5'

    return raw_of_data, df_periods

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename='pipeline.log', 
    format='[%(asctime)s][%(name)s] %(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S', 
    level=logging.WARNING) #INFO
    
# some constants
URL = f'https://sv.wikipedia.org/w/api.php'
#headers = {'user-agent': 'SchizoBot/0.1 (schizoakustik@schizoakustik.se)'}
headers = {'user-agent': 'runstenar (anton.grigoriev@alumni.chalmers.se)'}

# get the data from the previous run
logger.info('Starting data pipeline...')
data = DatabaseLoader()
df = data.load_data()

# read the category
#wiki_wiki = wikipediaapi.Wikipedia('UpplandsRunes (schizoakustik@schizoakustik.se)', 'sv')
wiki_wiki = wikipediaapi.Wikipedia('runstenar (anton.grigoriev@alumni.chalmers.se)', 'sv')
#wiki_wiki_html = wikipediaapi.Wikipedia('UpplandsRunes (schizoakustik@schizoakustik.se)', 'sv', extract_format=wikipediaapi.ExtractFormat.HTML)
wiki_wiki_html = wikipediaapi.Wikipedia('runstenar (anton.grigoriev@alumni.chalmers.se)', 'sv', extract_format=wikipediaapi.ExtractFormat.HTML)
cat = wiki_wiki.page("Category:Upplands runinskrifter")



#read vocabulary for periods as dataframe
file_name_periods = 'periods.csv'
if os.path.exists(file_name_periods):
    df_periods = pd.read_csv(file_name_periods)
else:
    df_periods = pd.DataFrame(columns=['Period', 'Period_begin','Period_end'])  # Create an empty DataFrame if file doesn't exist

count=0
for c in cat.categorymembers.values():
    count = count + 1
    #limit number of pages for exercise purpose 
    if count > 50 : break
    print(c.title)
    inskrift = c.title
    #if the page is new read and save it
    if not (inskrift in df['signum'].values):
        #save the page as v = 0
        try: 
            rad, df_periods = read_page(inskrift, df_periods)
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
                rad, df_periods = read_page(inskrift, df_periods)
                rad.append(df.loc[df['signum'] == inskrift,'edition'].item() + 1 )
                df.loc[df['signum'] == inskrift] = rad
            except:
                logger.warning('skipping ', inskrift)
        
# save result
output = DatabaseSave(df)
output.save_data()
# save result to readable format
df.to_csv('Uppland.csv', index=False)
