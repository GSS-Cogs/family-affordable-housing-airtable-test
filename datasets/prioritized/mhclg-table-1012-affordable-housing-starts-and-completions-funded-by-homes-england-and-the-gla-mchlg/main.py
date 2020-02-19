#!/usr/bin/env python
# coding: utf-8

# In[5]:


from gssutils import *
from databaker.framework import *
import pandas as pd
from gssutils.metadata import THEME
from gssutils.metadata import *
import datetime
from gssutils.metadata import Distribution, GOV
pd.options.mode.chained_assignment = None

def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

year = int(right(str(datetime.datetime.now().year),2)) - 1

scraper = Scraper('https://www.gov.uk/government/statistical-data-sets/live-tables-on-affordable-housing-supply')
dist = scraper.distribution(title=lambda x: x.startswith('Table 1012'))
scraper.dataset.title = dist.title
#scraper.dataset.description = 'Affordable housing supply statistics (AHS) 2017-18. Table 1012: Affordable Housing Starts and Completions funded by Homes England and the Greater London Authority 1,2,4'    
dist


# In[6]:


tabs = (t for t in dist.as_databaker())

tidied_sheets = []

for tab in tabs:
    
    if 'LT 1012' in tab.name:
        
        cell = tab.filter("ENGLAND")
        
        year = cell.fill(RIGHT).is_not_blank()
        
        period = cell.shift(1,1).expand(RIGHT).is_not_blank()
        
        remove = tab.filter(contains_string('1. ')).expand(RIGHT).expand(DOWN)
        
        completions = cell.expand(DOWN).filter(contains_string('Starts')) | cell.expand(DOWN).filter(contains_string('Completions'))
        
        tenure = cell.shift(0,2).expand(DOWN).is_not_blank() - remove - completions
        
        observations = tenure.fill(RIGHT).is_not_blank()
        
        dimensions = [
                HDim(year, 'Year', CLOSEST, LEFT),
                HDim(period, 'Period', DIRECTLY, ABOVE),
                HDim(tenure, 'Tenure', DIRECTLY, LEFT),
                HDim(completions, 'Completions', CLOSEST, ABOVE),
                HDimConst('Measure Type', 'Count'),
                HDimConst('Unit', 'Dwellings')
        ]
        
        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        savepreviewhtml(tidy_sheet, fname="Preview.html")

        tidied_sheets.append(tidy_sheet.topandas())
    


# In[7]:


df = pd.concat(tidied_sheets, ignore_index = True, sort = False).fillna('')

df = df.replace({'Completions' : {
    'Starts on Site3' : 'Starts'},
                'Tenure' : {
    'Affordable Home Ownership/Shared Ownership' : 'Affordable Home Ownership', 
    'Intermediate Rent5' : 'Intermediate Rent', 
    'London Affordable Rent6' : 'London Affordable Rent', 
    'Total Affordable' : 'All Affordable', 
    'Unknown' : 'Unknown Tenure'},
                'DATAMARKER' : {
    '..' : 'Not Applicable'},
                'Period' : {
    'Apr-Sep' : '04/6Months', 
    'Oct-Mar' : '10/6Months', 
    'Total' : '1Year'
                }})

df['Period'] = df.apply(lambda x: 'gregorian-interval/' + left(x['Year'],4) + '-' + left(x['Period'],2) + '-01T00:00:00/P6M' if 'Months' in x['Period'] else 'gregorian-interval/' + left(x['Year'],4) + '-04-01T00:00:00/P1Y', axis = 1)

df = df.drop(['Year'], axis=1)

df['Area'] = 'E92000001'

df.rename(columns={'Completions' : 'MCHLG Completions',
                   'Tenure' : 'MCHLG Tenure',
                   'Units' : 'Value',
                   'DATAMARKER' : 'Marker',
                   'OBS' : 'Value'}, inplace=True)

df.head()


# In[8]:


from IPython.core.display import HTML
for col in df:
    if col not in ['Value']:
        df[col] = df[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(df[col].cat.categories)    


# In[9]:


tidy = df[['Area','Period','MCHLG Tenure','MCHLG Completions','Value','Marker','Measure Type','Unit']]

for column in tidy:
    if column in ('Marker', 'MCHLG Tenure', 'MCHLG Completions'):
        tidy[column] = tidy[column].map(lambda x: pathify(x))

tidy.head()


# In[10]:


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




