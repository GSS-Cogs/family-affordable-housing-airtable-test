#!/usr/bin/env python
# coding: utf-8

# In[46]:


from gssutils import *
from databaker.framework import *
import pandas as pd
from gssutils.metadata import THEME
from gssutils.metadata import *
import datetime
from gssutils.metadata import Distribution, GOV
pd.options.mode.chained_assignment = None
import inspect

def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

def mid(s, offset, amount):
    return s[offset:offset+amount]


scraper = Scraper('https://www.gov.uk/government/statistical-data-sets/live-tables-on-affordable-housing-supply')
scraper


# In[47]:


dist = scraper.distribution(title=lambda x: x.startswith('Tables 1006'))
dist


# In[48]:


tabs = (t for t in dist.as_databaker())

tidied_tables = {}
tidied_sheets = []

for tab in tabs:
    
    if 'Live Table 100' in tab.name and '1009' not in tab.name:
        
        cell = tab.filter(contains_string('Table 100'))

        remove = cell.expand(DOWN).filter(contains_string('1. ')).expand(DOWN).expand(RIGHT)
        
        area = cell.shift(1,5).expand(DOWN).is_not_blank()

        period = cell.shift(3,3).expand(RIGHT).is_not_blank()   
        
        if 'Starts' in str(cell):
            completions = 'Starts'
        elif 'Completions' in str(cell):
            completions = 'Completions'
        else:
            completions = 'ERROR'

        observations = area.shift(2,0).fill(RIGHT) & period.expand(DOWN)

        dimensions = [
            HDim(period, 'Period', DIRECTLY, ABOVE),
            HDim(area, 'Area', DIRECTLY, LEFT),
            HDimConst('Measure Type', 'Count'),
            HDimConst('Unit', 'Dwellings'),
            HDimConst('Completions', completions),
            HDimConst('Tenure', mid(str(cell), 30, 75)),
            HDimConst('Provider', 'Local Authority')
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        savepreviewhtml(tidy_sheet, fname="Preview.html")
        
        tidied_sheets.append(tidy_sheet.topandas())
        
    elif '1009' in tab.name:
        
        table_name = 'Table 1009'
    
        cell = tab.filter(contains_string('Table 100'))

        remove = cell.expand(DOWN).filter(contains_string('1. ')).expand(DOWN).expand(RIGHT)
        
        period = cell.shift(1,2).expand(RIGHT).is_not_blank()   
        
        tenure = cell.expand(DOWN).filter(contains_string(', of which'))
        
        scheme_type = cell.shift(0,4).expand(DOWN).is_not_blank() - tenure - remove
        
        observations = scheme_type.shift(1,0).expand(RIGHT) - remove

        dimensions = [
            HDim(period, 'Period', DIRECTLY, ABOVE),
            HDimConst('Area', 'E92000001'),
            HDimConst('Measure Type', 'Count'),
            HDimConst('Unit', 'Dwellings'),
            HDim(tenure, 'Tenure', CLOSEST, ABOVE),
            HDim(scheme_type, 'Scheme Type', DIRECTLY, LEFT)
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        savepreviewhtml(tidy_sheet, fname="Preview.html")
        
        tidied_sheets2 = []
        tidied_sheets2.append(tidy_sheet.topandas())
        
        table_2 = pd.concat(tidied_sheets2, ignore_index = True, sort = True).fillna('')
        
        tidied_tables[table_name] = table_2

table_name = 'Tables 1006 to 1008'
        
table_1 = pd.concat(tidied_sheets, ignore_index = True, sort = True).fillna('')
        
tidied_tables[table_name] = table_1        


# In[49]:


GROUP_ID = 'MCHLG-tables-1006-to-1009-additional-affordable-homes-provided-by-type-of-scheme-and-local-authority-England'.lower()
scraper.set_base_uri('http://gss-data.org.uk')
from gssutils.metadata import THEME
scraper.dataset.theme = THEME['affordable-housing']

for i in tidied_tables:
    
    if i == 'Tables 1006 to 1008':
        
        df1 = tidied_tables.get(i)

        df1['Period'] = df1['Period'].map(lambda x: 'year/' + left(x,4))

        df1 = df1.replace({'DATAMARKER' : {
            '..' : 'not applicable'},
                         'Tenure' : {
            ' London affordable rent dwellings provided by local authority area - Comple' : 'London Affordable Rent',
            ' London affordable rent dwellings provided by local authority area - Starts' : 'London Affordable Rent',
            ' affordable rent dwellings provided by local authority area - Completions 1' : 'All Affordable',
            ' affordable rent dwellings provided by local authority area - Starts on sit' : 'All Affordable',
            ' units of affordable home ownership provided by local authority area - Comp' : 'Affordable Home Ownership',
            ' units of affordable home ownership provided by local authority area - Star' : 'Affordable Home Ownership',
            ' units of intermediate rent provided by local authority area - Completions1' : 'Intermediate Rent',
            ' units of intermediate rent provided by local authority area - Starts on si' : 'Intermediate Rent',
            ' units of shared ownership provided by local authority area - Completions1,' : 'Shared Ownership',
            ' units of shared ownership provided by local authority area - Starts on sit' : 'Shared Ownership',
            'ional affordable dwellings provided by local authority area - Completions1,' : 'Affordable Rent',
            'ional affordable dwellings provided by local authority area - Starts on sit' : 'Affordable Rent',
            'social rent dwellings provided by local authority area - Completions1,2,3,4' : 'Social Rent',
            'social rent dwellings provided by local authority area - Starts on site1,2,' : 'Social Rent'
                         }})

        df1.rename(columns={'OBS' : 'Value',
                           'DATAMARKER' : 'Marker',
                           'Tenure' : 'MCHLG Tenure',
                           'Provider' : 'MCHLG Provider',
                           'Completions' : 'MCHLG Completions'}, inplace=True)
        
        tidy1 = df1[['Area','Period', 'MCHLG Tenure','MCHLG Completions','MCHLG Provider','Value','Marker','Measure Type','Unit']]
        
        indexNames = tidy1[ tidy1['Area'].str.contains('E07AHS')].index
        tidy1.drop(indexNames, inplace = True)
        #Region codes of this format were mock codes used in the 90s which have no method of translation to current geography reference website

        for column in tidy1:
            if column in ('Marker', 'MCHLG Tenure','MCHLG Completions','MCHLG Provider'):
                tidy1[column] = tidy1[column].map(lambda x: pathify(x))
                
        destinationFolder = Path('out')
        destinationFolder.mkdir(exist_ok=True, parents=True)

        TAB_NAME = pathify(i)
        
        tidy1.drop_duplicates().to_csv(destinationFolder / f'{TAB_NAME}.csv', index = False)

        scraper.dataset.family = 'affordable-housing'
        scraper.dataset.comment = """
                This contains tables relating to the MHCLG Affordable Housing Statistics. The latest Statistical Publication is available here.
                https://www.gov.uk/government/collections/affordable-housing-supply
                """
        scraper.dataset.title = 'Tables 1006 to 1008: additional affordable homes provided by type of scheme and local authority, England'
        scraper.set_dataset_id(f'gss_data/affordable-housing/{GROUP_ID}/{TAB_NAME}')        
        
        with open(destinationFolder / f'{TAB_NAME}.csv-metadata.trig', 'wb') as metadata:
            metadata.write(scraper.generate_trig())

        csvw = CSVWMetadata('https://gss-cogs.github.io/family-affordable-housing/reference/')
        csvw.create(destinationFolder / f'{TAB_NAME}.csv', destinationFolder / f'{TAB_NAME}.csv-schema.json')

    else:
        
        df2 = tidied_tables.get(i)

        df2['Period'] = df2['Period'].map(lambda x: 'year/' + left(x,4))

        df2 = df2.replace({'DATAMARKER' : {
            '..' : 'not applicable'},
                         'Scheme Type' : {
            'Acquisitions' : 'Acquisition or rehabilitation', 
            'New Build' : 'New build', 
            'Not Known2' : 'Unknown'},
                         'Tenure' : {
            'Affordable Home Ownership, of which:' : 'Affordable Home Ownership', 
            'Affordable Rent, of which:' : 'Affordable Rent',
            'All affordable1, of which:' : 'All affordable', 
            'Intermediate Rent, of which:' : 'Intermediate Rent',
            'London Affordable Rent, of which:' : 'London Affordable Rent', 
            'Shared Ownership4, of which' : 'Shared Ownership',
            'Social Rent, of which:' : 'Social Rent', 
            'Unknown Tenure, of which:' : 'Unknown Tenure'
                         }})
        
        

        df2.rename(columns={'OBS' : 'Value',
                           'DATAMARKER' : 'Marker',
                           'Tenure' : 'MCHLG Tenure',
                           'Scheme Type' : 'MCHLG Scheme Type'}, inplace=True)
        
        tidy2 = df2[['Area','Period', 'MCHLG Tenure','MCHLG Scheme Type','Value','Marker','Measure Type','Unit']]
        
        indexNames = tidy2[ tidy2['Area'].str.contains('E07AHS')].index
        tidy2.drop(indexNames, inplace = True)
        #Region codes of this format were mock codes used in the 90s which have no method of translation to current geography reference website

        for column in tidy2:
            if column in ('Marker', 'MCHLG Tenure','MCHLG Scheme Type'):
                tidy2[column] = tidy2[column].map(lambda x: pathify(x))
                
        destinationFolder = Path('out')
        destinationFolder.mkdir(exist_ok=True, parents=True)

        TAB_NAME = pathify(i)

        tidy2.drop_duplicates().to_csv(destinationFolder / f'{TAB_NAME}.csv', index = False)

        scraper.dataset.family = 'affordable-housing'
        scraper.dataset.comment = """
                Figures for some  units, e.g. some affordable traveller pitches and some delivery under the Affordable Housing Guarantees programme, cannot be broken down to show new build and acquisitions.
                Figures shown represent our best estimate and may be subject to revisions. 
                """
        scraper.dataset.title = 'Table 1009: Additional New Build and Acquired Affordable Homes Provided'
        scraper.set_dataset_id(f'gss_data/affordable-housing/{GROUP_ID}/{TAB_NAME}')       
        
        with open(destinationFolder / f'{TAB_NAME}.csv-metadata.trig', 'wb') as metadata:
            metadata.write(scraper.generate_trig())

        csvw = CSVWMetadata('https://gss-cogs.github.io/family-affordable-housing/reference/')
        csvw.create(destinationFolder / f'{TAB_NAME}.csv', destinationFolder / f'{TAB_NAME}.csv-schema.json')
tidy1.head(50)


# In[50]:


tidy2.head(50)

