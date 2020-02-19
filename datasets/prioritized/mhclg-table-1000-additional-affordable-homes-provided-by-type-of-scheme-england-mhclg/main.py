#!/usr/bin/env python
# coding: utf-8

# In[3]:


from gssutils import *
from databaker.framework import *
import pandas as pd
from gssutils.metadata import THEME
from gssutils.metadata import *
import datetime

def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

year = int(right(str(datetime.datetime.now().year),2)) - 1

scraper = Scraper('https://www.gov.uk/government/statistical-data-sets/live-tables-on-affordable-housing-supply')
dist = scraper.distribution(title=lambda x: x.startswith('Table 1000'))
scraper.dataset.title = dist.title
dist


# In[4]:


tabs = (t for t in dist.as_databaker())

tidied_sheets = []

for tab in tabs:
    
    if 'Live Table' in tab.name and right(tab.name,1) is not '0': #all data in 'Live Table 1000' is included in 'Live Table 1000C'
        
        cell = tab.filter("England")
        
        period = cell.shift(RIGHT).expand(RIGHT).is_not_blank()
        
        remove = tab.filter("Notes:").expand(RIGHT).expand(DOWN)
        
        tenure = cell.shift(0,2).expand(DOWN).is_not_blank().filter(contains_string("of which:")) | tab.filter(contains_string('All affordable'))
        
        scheme = cell.shift(0,2).expand(DOWN).is_not_blank() - tenure
        
        header = tab.filter(contains_string('type of scheme'))
        
        print(str(header))
        
        if 'Completions' in str(header):
            scheme_type = 'Completions'
        elif 'Starts' in str(header):
            scheme_type = 'Starts'
        else:
            scheme_type = 'ERROR'
        
        observations = cell.shift(1,2).expand(DOWN).expand(RIGHT).is_not_blank() - remove - cell.shift(0,2).expand(DOWN).is_not_blank().filter(contains_string("of which:")).expand(RIGHT)
        
        dimensions = [
                HDim(period, 'Period', DIRECTLY, ABOVE),
                HDimConst('Area', 'E92000001'),
                HDim(tenure, 'Tenure', CLOSEST, ABOVE),
                HDim(scheme, 'Scheme', CLOSEST, ABOVE),
                HDimConst('Scheme Type', scheme_type),
                HDimConst('Measure Type', 'Count'),
                HDimConst('Unit', 'Dwellings')
        ]
        
        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        savepreviewhtml(tidy_sheet, fname="Preview.html")

        tidied_sheets.append(tidy_sheet.topandas())
        


# In[5]:


df = pd.concat(tidied_sheets, ignore_index = True, sort = False).fillna('')
df['Period'] = df['Period'].map(lambda x: 'gregorian-interval/' + left(x,4) + '-04-01T00:00:00/P1Y')

df.rename(columns={'OBS':'Value',
                   'DATAMARKER':'Marker'}, inplace=True)

df = df.replace({'Tenure' : { 
    'Affordable Home Ownership3, of which:' : 'Affordable Home Ownership', 
    'Affordable Rent, of which:' : 'Affordable Rent',
    'All affordable8' : 'All affordable', 
    'Intermediate Rent9, of which:' : 'Intermediate Rent',
    'London Affordable Rent, of which:' : 'London Affordable Rent', 
    'Shared Ownership3, of which:' : 'Shared Ownership',
    'Social Rent, of which:' : 'Social Rent', 
    'Unknown tenure, of which:' : 'Unknown tenure'},
                    'Scheme' : {
    '' : 'All', 
    'Affordable Housing Guarantees 2' : 'Affordable Housing Guarantees',
    'Local Authorities1 HE/GLA grant funded' : 'Local Authorities HE/GLA grant funded',
    'Local Authorities1 HE/GLA grant funded 3' : 'Local Authorities HE/GLA grant funded',
    'Non-Registered Providers1 HE funded' : 'Non-Registered Providers HE funded', 
    'Other 7' : 'Other',
    'Permanent Affordable Traveller Pitches 6 ' : 'Permanent Affordable Traveller Pitches',
    'Private Finance Initiative 5' : 'Private Finance Initiative',
    'Private Registered Providers1 HE/GLA funded' : 'Private Registered Providers HE/GLA funded',
    'Section 106 (nil grant) 4' : 'Section 106 (nil grant)', },
                    'Marker' : {
    '..' : 'not applicable'}})

for column in df:
    if column in ('Marker', 'Tenure', 'Scheme', 'Scheme Type'):
        df[column] = df[column].map(lambda x: pathify(x))

from IPython.core.display import HTML
for col in df:
    if col not in ['Value']:
        df[col] = df[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(df[col].cat.categories)    


# In[6]:


tidy = df[['Period','Area','Tenure','Scheme','Scheme Type','Value','Marker','Measure Type','Unit']]
tidy.rename(columns={'Tenure':'MCHLG Tenure',
                     'Scheme':'MCHLG Scheme',
                     'Scheme Type' : 'MCHLG Completions'}, inplace=True)
tidy


# In[7]:


destinationFolder = Path('out')
destinationFolder.mkdir(exist_ok=True, parents=True)

TAB_NAME = 'observations'

tidy.drop_duplicates().to_csv(destinationFolder / f'{TAB_NAME}.csv', index = False)

scraper.dataset.family = 'affordable-housing'

with open(destinationFolder / f'{TAB_NAME}.csv-metadata.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())

csvw = CSVWMetadata('https://gss-cogs.github.io/family-affordable-housing/reference/')
csvw.create(destinationFolder / f'{TAB_NAME}.csv', destinationFolder / f'{TAB_NAME}.csv-schema.json')
tidy


# In[ ]:




