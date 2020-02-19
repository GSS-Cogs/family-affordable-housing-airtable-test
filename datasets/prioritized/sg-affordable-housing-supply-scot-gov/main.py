# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.1.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# ## Affordable Housing Supply (Scot Gov)

from gssutils import *
from gssutils.metadata import THEME
scraper = Scraper('https://www2.gov.scot/Topics/Statistics/Browse/Housing-Regeneration/HSfS/NewBuild/AHSPtables')
scraper

# +
dist = scraper.distributions[0]
tabs = (t for t in dist.as_databaker())
tidied_sheets = []
tidied_fin_sheets = []

def left(s, amount):
    return s[:amount]
def right(s, amount):
    return s[-amount:]


# -

for tab in tabs:
    housing_type = 'unknown'
    
    if 'Approvals - qtrly' in tab.name or 'Starts - qtrly' in tab.name or 'Completions - qtrly' in tab.name:
        
        if 'Approvals - qtrly' in tab.name:
            housing_type = 'Approvals'
        if 'Starts - qtrly' in tab.name:
            housing_type = 'Starts'
        if 'Completions - qtrly' in tab.name:
            housing_type = 'Completions'
        
        remove1 = tab.excel_ref('B51').expand(DOWN)
        remove2 = ['C10','C11', 'C12', 'C13', 'C14','C15', 'C16', 'C17','C18', 'C19', 'C20', 'C24', 'C25', 'C26', 'C27', 'C28',
                  'C31','C31', 'C32', 'C33', 'C34', 'C35', 'C36', 'C37','C38', 'C39', 'C40', 'C41', 'C42', 'C43', 'C44',
                  'C45', 'C46', 'C47']
        remove3 = tab.excel_ref('C50').expand(DOWN)
        remove4 = tab.excel_ref('E50').expand(RIGHT).expand(DOWN)
        
        period = tab.excel_ref('E5').expand(RIGHT).is_not_blank() 
        quarter = tab.excel_ref('E6').expand(RIGHT).is_not_blank() 
        tenure = tab.excel_ref('B7').expand(DOWN).is_not_blank() - remove1
        AHSP_scheme = tab.excel_ref('C9').expand(DOWN) - remove3
        AHSP_scheme_type = tab.excel_ref('D11').expand(DOWN).is_not_blank()
        type_of_property = tab.excel_ref('E11').expand(DOWN)
        observations = quarter.fill(DOWN).is_not_blank() - remove4
        
        for cell in remove2:
            AHSP_scheme = AHSP_scheme - tab.excel_ref(cell)
        
        dimensions = [
            HDim(period, 'Period', DIRECTLY, ABOVE),
            HDim(quarter, 'Quarter', DIRECTLY, ABOVE),
            HDim(tenure, 'Tenure', CLOSEST, ABOVE),
            HDim(AHSP_scheme, 'AHSP Scheme', CLOSEST, ABOVE),
            HDim(AHSP_scheme_type, 'AHSP Scheme Type', CLOSEST, ABOVE),
            HDim(type_of_property, 'Property Type', DIRECTLY, LEFT),
            HDimConst('New Affordable Housing Type', housing_type),
            HDimConst('Measure Type', 'Count'),
            HDimConst('Unit', 'Housing'),
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)        
        savepreviewhtml(tidy_sheet, fname= tab.name + "Preview.html" )
        tidied_sheets.append(tidy_sheet.topandas())
        
    if 'Approvals -finyear' in tab.name or 'Starts - finyear' in tab.name or 'Completions - finyear' in tab.name:
        
        if 'Approvals -finyear' in tab.name:
            housing_type = 'Approvals'
        if 'Starts - finyear' in tab.name:
            housing_type = 'Starts'
        if 'Completions - finyear' in tab.name:
            housing_type = 'Completions'      
        
        remove1 = tab.excel_ref('B48').expand(DOWN)
        remove2 = ['C8','C9', 'C10', 'C11', 'C12','C13', 'C14', 'C15','C16', 'C17', 'C18', 'C22', 'C23', 'C24', 'C25', 'C26',
                  'C29', 'C30', 'C31', 'C32', 'C33', 'C34', 'C35','C36', 'C37', 'C38', 'C39', 'C40', 'C41', 'C42',
                  'C45', 'C46', 'C47']
        remove3 = tab.excel_ref('C50').expand(DOWN)
        remove4 = tab.excel_ref('E48').expand(RIGHT).expand(DOWN)
        
        period = tab.excel_ref('E4').expand(RIGHT).is_not_blank() 
        tenure = tab.excel_ref('B5').expand(DOWN).is_not_blank() - remove1
        AHSP_scheme = tab.excel_ref('C7').expand(DOWN) - remove3
        AHSP_scheme_type = tab.excel_ref('D9').expand(DOWN).is_not_blank()
        type_of_property = tab.excel_ref('E9').expand(DOWN)
        observations = period.fill(DOWN).is_not_blank() - remove4
        
        for cell in remove2:
            AHSP_scheme = AHSP_scheme - tab.excel_ref(cell)
        
        dimensions = [
            HDim(period, 'Period', DIRECTLY, ABOVE),
            HDim(tenure, 'Tenure', CLOSEST, ABOVE),
            HDim(AHSP_scheme, 'AHSP Scheme', CLOSEST, ABOVE),
            HDim(AHSP_scheme_type, 'AHSP Scheme Type', CLOSEST, ABOVE),
            HDim(type_of_property, 'Property Type', DIRECTLY, LEFT),
            HDimConst('New Affordable Housing Type', housing_type),
            HDimConst('Measure Type', 'Count'),
            HDimConst('Unit', 'Housing'),
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)        
        savepreviewhtml(tidy_sheet, fname=tab.name + "Preview.html")
        tidied_fin_sheets.append(tidy_sheet.topandas())    


# +
df1  = pd.concat(tidied_sheets, ignore_index = True, sort = False) #Quarter years 
df1['Period'] = df1['Period'].map(lambda x: 'quarter/' + left(x,4))
df1["Period"] = df1["Period"] + df1["Quarter"].map(lambda x: '-Q' + right(x,1))

df2 = pd.concat(tidied_fin_sheets,ignore_index = True, sort = False) #financial years 
df2['Period'] = df2['Period'].map(lambda x: 'year/' + left(x,4))
f5=((df2['Tenure'] =='TOTAL AFFORDABLE HOUSING SUPPLY') & (df2['AHSP Scheme'] == '')) 
df2.loc[f5,'AHSP Scheme'] = 'TOTAL AFFORDABLE HOUSING SUPPLY'

together = [df1, df2]
df = pd.concat(together,ignore_index = True, sort = False)

# +
df.rename(columns={'OBS' : 'Value','DATAMARKER' : 'Marker'}, inplace=True)

f1=((df['Tenure'] =='AFFORDABLE HOME OWNERSHIP') & (df['AHSP Scheme'] == '')) 
df.loc[f1,'AHSP Scheme'] = 'AFFORDABLE HOME OWNERSHIP'

f2=((df['Tenure'] =='TOTAL AFFORDABLE HOUSING SUPPLY') & (df['AHSP Scheme'] == ''))
df.loc[f2,'AHSP Scheme'] = 'TOTAL AFFORDABLE HOUSING SUPPLY'

f3=((df['AHSP Scheme'] =='Total Affordable Home Ownership') & (df['AHSP Scheme Type'] == 'Home Owner Support Fund (Shared Equity)'))
df.loc[f3,'AHSP Scheme Type'] = 'not applicable'

f4=((df['AHSP Scheme'] =='TOTAL AFFORDABLE HOUSING SUPPLY') & (df['AHSP Scheme Type'] == 'Home Owner Support Fund (Shared Equity)'))
df.loc[f4,'AHSP Scheme Type'] = 'Not Applicable'

f5=((df['Tenure'] =='TOTAL AFFORDABLE HOUSING SUPPLY') & (df['AHSP Scheme'] == ' ')) 
df.loc[f5,'AHSP Scheme'] = 'TOTAL AFFORDABLE HOUSING SUPPLY'

df = df.replace({'Property Type' : {'' : 'Not Applicable'}})
# -


tidy = df[['Period','Tenure','AHSP Scheme','AHSP Scheme Type', 'Property Type',
           'New Affordable Housing Type', 'Value', 'Measure Type', 'Unit']]

for column in tidy:
    if column in ('Tenure', 'AHSP Scheme', 'AHSP Scheme Type', 'Property Type', 'New Affordable Housing Type'):
        tidy[column] = tidy[column].map(lambda x: pathify(x))

# +
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
# -


