#!/usr/bin/env python
# coding: utf-8

# In[7]:


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
scraper


# In[8]:


dist = scraper.distribution(title=lambda x: x.startswith('Table 1011'))
dist.mediaType = Excel 
dist


# In[9]:


df = dist.as_pandas(sheet_name = 'data')

df.head()


# In[10]:


tidy = df[['LA code','Year','Tenure','Completions','Region code','Type','LT1000','Provider','Units']]
tidy.fillna('NaN', inplace=True)

tidy.rename(columns={'LA code' : 'Area',
                     'Year' : 'Period',
                     'Completions' : 'MCHLG Completions',
                     'Type' : 'MCHLG Scheme Type',
                     'Tenure' : 'MCHLG Tenure',
                     'LT1000' : 'MCHLG Scheme',
                     'Units' : 'Value',
                     'Provider' : 'MCHLG Provider'}, inplace=True)

tidy['Period'] = tidy['Period'].map(lambda x: 'gregorian-interval/' + left(x,4) + '-04-01T00:00:00/P1Y')
tidy['MCHLG Completions'] = tidy['MCHLG Completions'].map(lambda x: 'Completions' if 'Y' in x else 'Starts')
tidy['Area'] = tidy.apply(lambda x: x['Region code'] + x['Area'] if x['Area'] == 'NaN' else x, axis = 1)
tidy['Area'] = tidy['Area'].map(lambda x: left(x, 9) if x.endswith('NaN') else x)

indexNames = tidy[ tidy['Area'] == 'NaNNaN' ].index
tidy.drop(indexNames, inplace = True)
#If any rows have NaNNan still in the Area column then they have neither a local Area Code nor a Region Code, 
#and since this table is based around values per Area this values are no longer useful

indexNames = tidy[ tidy['Area'].str.contains('E07AHS')].index
tidy.drop(indexNames, inplace = True)
#Region codes of this format were mock codes used in the 90s which have no method of translation to current geography reference website

tidy = tidy.drop(['Region code'], axis=1)
tidy['Measure Type'] = 'Count'
tidy['Unit'] = 'Dwellings'

tidy = tidy.replace({'MCHLG Scheme' : {
    'Right to Buy recycled receipts' : 'Right  To  Buy  Additions  With  Recycled  Receipts',
    's106 nil grant' : 'Section  106  Nil  Grant',
    's106 part grant' : 'Section  106  Partial  Grant',
    'Private Registered Provider HE/GLA funded' : 'Private Registered Providers HE/GLA funded',
    'Private Registered Provider other funding' : 'Private Registered Providers other funding',
    'Affordable Homes Guarantees' : 'Affordable Housing Guarantees',
    'Local Authority HE/GLA funded' : 'Local  Authorities  He/Gla  Grant  Funded',
    'Local Authority other funding' : 'Local  Authorities  Other  Funding',
    'Non-Registered Provider HE funded' : 'Non  Registered  Providers  He  Funded'},
                'MCHLG Tenure' : {
    'Unknown' : 'Unknown Tenure'},
                'MCHLG Scheme Type' : {
    'NB' : 'New build',
    'AQ' : 'Acquisition or rehabilitation',
    'U' : 'unknown'},
                'MCHLG Provider' : {
    'RP' : 'Private Registered Provider',
    'LA' : 'Local Authority',
    'NR' : 'Non Registered Provider',
    'U' : 'Unknown'}})

for column in tidy:
    if column in ('Marker', 'MCHLG Tenure', 'MCHLG Scheme', 'MCHLG Completions', 'MCHLG Scheme Type','MCHLG Provider'):
        tidy[column] = tidy[column].map(lambda x: pathify(x))

tidy.head()


# In[11]:


from IPython.core.display import HTML
for col in tidy:
    if col not in ['Value']:
        tidy[col] = tidy[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(tidy[col].cat.categories)    


# In[12]:


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

