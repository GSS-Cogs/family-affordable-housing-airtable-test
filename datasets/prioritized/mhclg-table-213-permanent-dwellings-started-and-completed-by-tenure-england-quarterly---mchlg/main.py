#!/usr/bin/env python
# coding: utf-8

# In[3]:


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

scraper = Scraper('https://www.gov.uk/government/statistical-data-sets/live-tables-on-house-building')
dist = scraper.distribution(title=lambda x: x.startswith('Table 213'))
scraper.dataset.title = dist.title
#scraper.dataset.description = 'Live tables on house building: new build dwellings started and completed, by tenure, England'   
dist


# In[4]:


tabs = (t for t in dist.as_databaker())

tidied_sheets = []

for tab in tabs:
    
    if 'quarterly' in tab.name:
    
        cell = tab.filter(contains_string('Table 213'))

        remove = cell.expand(DOWN).filter(contains_string('1. ')).expand(RIGHT).expand(DOWN)

        year = cell.shift(0,5).expand(DOWN).is_not_blank() - remove

        period = cell.shift(1,5).expand(DOWN).is_not_blank()

        completions = cell.shift(4,2).expand(RIGHT).is_not_blank()

        tenure = completions.shift(-1,1).expand(RIGHT).is_not_blank()

        observations = tenure.shift(DOWN).fill(DOWN).is_not_blank() - remove

        dimensions = [
                HDim(year, 'Year', CLOSEST, ABOVE),
                HDim(period, 'Period', DIRECTLY, LEFT),
                HDim(tenure, 'Tenure', DIRECTLY, ABOVE),
                HDim(completions, 'Completions', CLOSEST, LEFT),
                HDimConst('Measure Type', 'Count'),
                HDimConst('Unit', 'Dwellings')
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        savepreviewhtml(tidy_sheet, fname="Preview.html")

        tidied_sheets.append(tidy_sheet.topandas())
        
    else:
        
        cell = tab.filter(contains_string('Table 213'))

        remove = cell.expand(DOWN).filter(contains_string('1. ')).expand(RIGHT).expand(DOWN)

        year = cell.shift(1,3).fill(DOWN).is_not_blank() - remove

        completions = cell.shift(5,2).expand(RIGHT).is_not_blank()

        tenure = completions.shift(-1,1).expand(RIGHT).is_not_blank()

        observations = tenure.shift(DOWN).fill(DOWN).is_not_blank() - remove

        dimensions = [
                HDim(year, 'Year', CLOSEST, ABOVE),
                HDimConst('Period', 'P1Y'),
                HDim(tenure, 'Tenure', DIRECTLY, ABOVE),
                HDim(completions, 'Completions', CLOSEST, LEFT),
                HDimConst('Measure Type', 'Count'),
                HDimConst('Unit', 'Dwellings')
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        savepreviewhtml(tidy_sheet, fname="Preview.html")

        tidied_sheets.append(tidy_sheet.topandas())

    


# In[5]:


df = pd.concat(tidied_sheets, ignore_index = True, sort = False).fillna('')


df = df.replace({'Completions' : {
    'Completed': 'Completions', 
    'Started' : 'Starts'},
                'Tenure' : {
    'All\nDwellings' : 'All Dwellings'},
                'DATAMARKER' : {
    '-' : 'Less than five'}})

df['Completions'] = df.apply(lambda x: 'Completions' if 'Private Enterprise' in x['Tenure'] and 'Starts' in x['Completions'] else x['Completions'], axis = 1)
df['Completions'] = df['Completions'].map(lambda x: 'Starts' if x == '' else x)

df['Period'] = df.apply(lambda x: 'quarter/' + left(x['Year'],4) + '-' + x['Period'] if 'Q' in x['Period'] else 'year/' + left(x['Year'],4), axis = 1)

df = df.drop(['Year'], axis=1)

df['Area'] = 'E92000001'

df.rename(columns={'Completions' : 'MCHLG Completions',
                   'Tenure' : 'MCHLG Tenure',
                   'DATAMARKER' : 'Marker',
                   'OBS' : 'Value'}, inplace=True)

df#.head()


# In[6]:


from IPython.core.display import HTML
for col in df:
    if col not in ['Value']:
        df[col] = df[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(df[col].cat.categories)    


# In[7]:


tidy = df[['Area','Period','MCHLG Tenure','MCHLG Completions','Value','Marker','Measure Type','Unit']]

for column in tidy:
    if column in ('Marker', 'MCHLG Tenure', 'MCHLG Completions'):
        tidy[column] = tidy[column].map(lambda x: pathify(x))

tidy.head()


# In[8]:


destinationFolder = Path('out')
destinationFolder.mkdir(exist_ok=True, parents=True)

TAB_NAME = 'observations'

tidy.drop_duplicates().to_csv(destinationFolder / f'{TAB_NAME}.csv', index = False)

scraper.dataset.family = 'affordable-housing'
scraper.dataset.comment = {'Missing Data' : 'Figures from October 2005 to March 2007 in England are missing a small number of starts and completions that were inspected by independent approved inspectors. These data are included from June 2007',
                           'Seasonal Adjustment' : 'Figures in this tables are not seasonally adjusted; for seasonally adjusted house building figures, please [live table 222](https://www.gov.uk/government/statistical-data-sets/live-tables-on-house-building)',
                           'New Build' : 'These figures are for new build dwellings only. The Department also publishes an annual release entitled "Housing Supply: net additional dwellings"'}


with open(destinationFolder / f'{TAB_NAME}.csv-metadata.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())

csvw = CSVWMetadata('https://gss-cogs.github.io/family-affordable-housing/reference/')
csvw.create(destinationFolder / f'{TAB_NAME}.csv', destinationFolder / f'{TAB_NAME}.csv-schema.json')
tidy


# In[ ]:




