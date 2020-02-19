#!/usr/bin/env python
# coding: utf-8

# In[2]:


from gssutils import *
from databaker.framework import *
import pandas as pd
from gssutils.metadata import THEME
from gssutils.metadata import *
import datetime
from gssutils.metadata import Distribution, GOV
pd.options.mode.chained_assignment = None
import json

def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

def mid(s, offset, amount):
    return s[offset:offset+amount]


info = json.load(open('info.json')) 
landingPage = info['Landing Page'] 
landingPage 


# In[3]:


scraper = Scraper(landingPage) 
scraper.select_dataset(latest=True) 
dist = scraper.distribution(title=lambda x: x.startswith('Table 102'))
scraper.dataset.title = dist.title   
dist


# In[4]:


tabs = (t for t in dist.as_databaker())

tidied_sheets = []

for tab in tabs:
    
    cell = tab.filter(contains_string('Table 102'))

    remove = cell.expand(DOWN).filter(contains_string('1. ')).expand(DOWN).expand(RIGHT)

    period_year = cell.shift(2,6).expand(DOWN).is_not_blank().shift(-2,0) - remove
    
    period_start = cell.shift(0,6).expand(DOWN).is_not_blank() - period_year - remove

    area = 'K03000001'
        
    tenure_1 = cell.shift(2,3).expand(RIGHT)
    
    tenure_2 = cell.shift(2,4).expand(RIGHT)
    
    tenure_3 = cell.shift(2,5).expand(RIGHT)

    observations = period_year.shift(RIGHT).fill(RIGHT).is_not_blank()

    dimensions = [
        HDim(period_year, 'Period Year', DIRECTLY, LEFT),
        HDim(period_start, 'Period Start', CLOSEST, ABOVE),
        HDim(tenure_1, 'Tenure 1', DIRECTLY, ABOVE),
        HDim(tenure_2, 'Tenure 2', DIRECTLY, ABOVE),
        HDim(tenure_3, 'Tenure 3', DIRECTLY, ABOVE),
        HDimConst('Area', area),
        HDimConst('Measure Type', 'Count'),
        HDimConst('Unit', 'Dwellings (thousands)')
        ]

    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    savepreviewhtml(tidy_sheet, fname="Preview.html")

    tidied_sheets.append(tidy_sheet.topandas())
        


# In[5]:


df = pd.concat(tidied_sheets, ignore_index = True, sort = False).fillna('')

df['Tenure'] = df['Tenure 1'] + ' ' + df['Tenure 2'] + ' ' + df['Tenure 3']

df = df.replace({'Period Start' : {
    '1 April 2' : '04', 
    '31 December 3' : '12', 
    '31 March 3,4' : '03'}})

df['Period'] = df.apply(lambda x: 'gregorian-interval/' + left(x['Period Year'],4) + '-' + x['Period Start'] + '-01T00:00:00/P1Y' if '04' in x['Period Start'] else 'gregorian-interval/' + left(x['Period Year'],4) + '-' + x['Period Start'] + '-31T00:00:00/P1Y', axis = 1)

df = df.drop(['Tenure 1', 'Tenure 2', 'Tenure 3', 'Period Year', 'Period Start'], axis=1)

df = df.replace({'Tenure' : {
    ' All Dwellings' : 'All Dwellings', 
    ' Owner  Occupied' : 'Owner Occupied', 
    'Other  public sector dwellings' : 'Other Public Sector Dwellings',
    'Rented Privately or with a job or business' : 'Private Enterprise',
    'Rented from Housing Associations' : 'Housing Associations', 
    'Rented from Local Authorities' : 'Local Authorities'},
                'DATAMARKER' : {
    '..' : 'not available'
                }})

df.rename(columns={'OBS' : 'Value',
                   'DATAMARKER' : 'Marker',
                   'Tenure' : 'MCHLG Tenure'}, inplace=True)

df.head(50)


# In[6]:


from IPython.core.display import HTML
for col in df:
    if col not in ['Value']:
        df[col] = df[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(df[col].cat.categories)    


# In[7]:


tidy = df[['Area','Period', 'MCHLG Tenure', 'Value', 'Marker', 'Measure Type', 'Unit']]

for column in tidy:
    if column in ('Marker', 'MCHLG Tenure'):
        tidy[column] = tidy[column].map(lambda x: pathify(x))

tidy.head(50) 


# In[8]:


destinationFolder = Path('out')
destinationFolder.mkdir(exist_ok=True, parents=True)

TAB_NAME = 'observations'

tidy.drop_duplicates().to_csv(destinationFolder / f'{TAB_NAME}.csv', index = False)

scraper.dataset.family = 'affordable-housing'
scraper.dataset.comment = """
        Data for earlier years are less reliable and definitions may not be consistent throughout the series
        """

with open(destinationFolder / f'{TAB_NAME}.csv-metadata.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())

csvw = CSVWMetadata('https://gss-cogs.github.io/family-affordable-housing/reference/')
csvw.create(destinationFolder / f'{TAB_NAME}.csv', destinationFolder / f'{TAB_NAME}.csv-schema.json')
tidy


# In[ ]:




