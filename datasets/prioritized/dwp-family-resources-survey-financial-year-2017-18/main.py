# -*- coding: utf-8 -*-
# + {}
#### DWP Family Resources Survey for Financial Year 2017 to 2018 - Income & State Support - Affordable Housing ####

# +
from gssutils import *
import datetime as d
import numpy as np

mainURL = "https://www.gov.uk/government/statistics/family-resources-survey-financial-year-"
#### Construct a string based on the year you need to look at.
oneYrAgo = int(d.datetime.now().year) - 1      #### Get the year 1 year ago
twoYrAgo = oneYrAgo - 1                          #### Get the year 2 years ago
yrStr = str(twoYrAgo) + str(oneYrAgo)[2:4]       #### Join the years as a string, 201718
yrStr2 = str(twoYrAgo) + '/' + str(oneYrAgo)[2:4] #### This is for adding to columns later
try:
    #### EXAMPLE: https://www.gov.uk/government/statistics/family-resources-survey-#### Construct a string based on the year you need to look at.
    oneYrAgo = int(d.datetime.now().year) - 1        #### Get the year 1 year ago
    twoYrAgo = oneYrAgo - 1                          #### Get the year 2 years ago
    yrStr = str(twoYrAgo) + str(oneYrAgo)[2:4]       #### Join the years as a string, financial-year-201718
    urlStr = mainURL + yrStr
    print("1. Trying: " + urlStr)
    scraper = Scraper(urlStr)
    if (len(scraper.distributions) == 0): 
        oneYrAgo = int(d.datetime.now().year) - 2        #### Get the year 1 year ago
        twoYrAgo = oneYrAgo - 1                          #### Get the year 2 years ago
        yrStr = str(twoYrAgo) + str(oneYrAgo)[2:4]       #### Join the years as a string, 2financial-year-201718
        urlStr = mainURL + yrStr
        print("2. Trying: " + urlStr)
        scraper = Scraper(urlStr)
        if (len(scraper.distributions) == 0):
            oneYrAgo = int(d.datetime.now().year) - 3       #### Get the year 1 year ago
            twoYrAgo = oneYrAgo - 1                          #### Get the year 2 years ago
            yrStr = str(twoYrAgo) + str(oneYrAgo)[2:4]       #### Join the years as a string, financial-year-201718
            urlStr = mainURL + yrStr
            print("3. Trying: " + urlStr)
            scraper = Scraper(urlStr)
    
    currYr = str(twoYrAgo) + '/' + str(oneYrAgo)[2:4]
except Exception as e:
    print("Cannot find a suitable webpage!!")
scraper


# +
# Table 2.1: Sources of totel gross household income, UK
# Table 2_2: Sources of total gross household income by region/country, United Kingdom (2 Tables)
# Table 2_3: Sources of total gross household income by ethnic group of head, average, United Kingdom
# Table 2_4: Sources of total gross houshold income by age of head, United Kingdom
# Table 2_5: Households by composition and total gross weekly household income, United Kingdom
# Table 2_6: Households by region/country and gross weekly household income, United Kingdom
# Table 2_7: Households by ethnic group of head and gross weekly household income, United Kingdom
# Table 2_8: Benefit units by state support receippt and region/country, United Kingdom
# Table 2_9: Benefit units by state support receipt and benefit type unit, United Kingdom
# Table 2_10: Benefit units by state support receipt and ethnic group of head, United Kingdom
# Table 2_11: Benefit units by state support receipt and age of head, United Kingdom
# Tabel 2_12: Benefit units by state support receipt and tenure, United Kingdom
# Table 2_13: Benefit units by state support receipt and economic status, United Kingdom
# Table 2_14: Benefit units by amount of annual state support received, United Kingdom (2 Tables)
# -

def extract_sheet_single_table(refTab, tab, ref1, ref2, ref3, refSS, mainTitle1, mainTitle2, periodRef, sampleSizeInColumn, unitValue, periodRange):
    try:
        col1 = tab.excel_ref(ref1).fill(DOWN).is_not_blank()
        col2 = tab.excel_ref(ref2).is_not_blank()
        col3 = tab.excel_ref(ref3).expand(RIGHT).is_not_blank() 

        Dimensions = [
            HDim(col1,mainTitle1, DIRECTLY, LEFT),
            HDim(col3,mainTitle2, DIRECTLY, ABOVE)
            ]

        c1 = ConversionSegment(col2, Dimensions, processTIMEUNIT=True)
        c1 = c1.topandas()
        #### Sample Size is in a column
        if (sampleSizeInColumn):
            c2 = c1[[mainTitle1,mainTitle2,'OBS']][c1[mainTitle2].str.strip() == refSS]
            c1 = c1[(c1[mainTitle2].str.strip() != refSS) & (c1[mainTitle2].str.strip() != 'All')]
            tbl = pd.merge(c1, c2, on=mainTitle1)
            tbl = tbl.rename(columns={'OBS_x':valueTitle,mainTitle2 + '_x':mainTitle2,'OBS_y':refSS})
            tbl = tbl.drop(columns=[mainTitle2 +'_y'])
        #### Sample Size is on a row, usually the bottom
        else:
            c2 = c1[[mainTitle1,mainTitle2,'OBS']][c1[mainTitle1].str.strip() == refSS]
            c1 = c1[(c1[mainTitle1].str.strip() != refSS) & (c1[mainTitle2].str.strip() != 'All')]
            tbl = pd.merge(c1, c2, on=mainTitle2)
            tbl = tbl.rename(columns={'OBS_x':valueTitle,mainTitle1 + '_x':mainTitle1,'OBS_y':refSS})
            tbl = tbl.drop(columns=[mainTitle1 +'_y'])
            
        tbl[markerTitle] = ''
        
        if (periodRef != ''):
            tbl[periodTitle] = periodRef
            
        tbl[periodTitle] = tbl[periodTitle].map(lambda x: f'gregorian-interval/{str(x)[:4]}-03-31T00:00:00/P{periodRange}Y')      
        
        if (unitValue != ''):
            tbl[unitTitle] = unitValue
        
        tbl = tbl[tbl[valueTitle] != ''] 
        
        if ((periodTitle == mainTitle2)):
            tbl = tbl[[periodTitle, mainTitle1, refSS, markerTitle, valueTitle, unitTitle]] 
        elif ((periodTitle == mainTitle1)):
            tbl = tbl[[periodTitle, mainTitle2, refSS, markerTitle, valueTitle, unitTitle]] 
        else:
            tbl = tbl[[periodTitle, mainTitle1, mainTitle2, refSS, markerTitle, valueTitle, unitTitle]] 
        
        tbl = tbl.rename(columns={'Sample size': sampSzeTitle})
        
        return tbl
    except Exception as e:
        return "extract_sheet_single_table: " + str(e)


#### There are several spreadsheets so look for the one you want, which in this case is Income and Support
try:
    for i in scraper.distributions:
        if i.title == 'Income and state support data tables (XLS)':
            print(i.title)
            sheets = i
            break
except Exception as e:
         print(e.message, e.args)

#### Convert to a DataBaker object
try:
    sheets = sheets.as_databaker()
except Exception as e:
    print(e.message, e.args)

#### Set all the column names in one place
periodTitle = 'Period'
markerTitle = 'Marker'
valueTitle = 'Value'
dataMarkerTitle = 'DATAMARKER'
incomeTitle = 'DWP Source of Income'
incBreakTitle = 'DWP Income Breakdown'
ageTitle = 'DWP Age of Head'
ethnicTitle = 'DWP Ethnic Group'
regionTitle = 'DWP Region Country'
wklyIncomeTitle = 'DWP Gross Weekly Household Income'
houseCompTitle = 'DWP Household Composition'
steSupTitle = 'DWP State Support Received'
benUntTitle = 'DWP Benefit Unit Type'
tenureTitle = 'DWP Tenure'
econStatTitle = 'DWP Economic Status'
annAmtTitle = 'DWP Annual Amount State Support'
sampSzeTitle = 'Sample Size'
unitTitle = 'Measure Type'
unitVal1 = 'Percentage'
unitVal2 = 'Number of benefit units in millions'
threeYr = '2015/16'
#### Put all columm headings into an Array to used in a loop later
allMainTitles = [incomeTitle, ethnicTitle, regionTitle, wklyIncomeTitle, houseCompTitle, steSupTitle, benUntTitle, tenureTitle, econStatTitle]


def fixTable2_5(myTbl):
    try:
        stri = ['one child','two children','three or more children']
 
        for st in stri:
            samp = pd.DataFrame(myTbl[sampSzeTitle][(myTbl[houseCompTitle].str.strip() == str(st))].unique())
            samp.columns = ['SS']
            #print(samp)
            for index, row in samp.iterrows():
                #print('Looking at: ' + st + ' and SS: ' + str(row['SS']) + ' - Table size: '+ str(myTbl[houseCompTitle].count()))
                oc = myTbl[(myTbl[sampSzeTitle] == row['SS']) & (myTbl[houseCompTitle].str.strip() == st)]
                #print('1. OC Count: ' + str(oc[mainTitle1].count()) + ' - Index: ' + str(index))
                if (index == 0):
                    oc[houseCompTitle] = 'One adult ' + oc[houseCompTitle]
                    oc = oc.drop(oc.index[11:oc[houseCompTitle].count()])
                elif (index == 1):
                    oc[houseCompTitle] = 'Two adults ' + oc[houseCompTitle]
                    oc = oc.drop(oc.index[0:11])
                    oc = oc.drop(oc.index[11:oc[houseCompTitle].count()])
                elif (index == 2):
                    oc[houseCompTitle] = 'Three or more adults ' + oc[houseCompTitle]
                    oc = oc.drop(oc.index[0:22])
                #print('2. OC Count: ' + str(oc[mainTitle1].count()) + ' - Index: ' + str(index))
                myTbl = myTbl.drop(myTbl[(myTbl[sampSzeTitle] == row['SS']) & (myTbl[houseCompTitle].str.strip() == st)].index)
                myTbl = pd.concat([myTbl, oc])  
                #print('My Table size: '+ str(myTbl[mainTitle1].count()))"""
        return myTbl
    except Exception as e:
        print(str(e))


# +
# %%capture
#### Transform all the sheets
try:
    tbl1 = extract_sheet_single_table('2', [t for t in sheets if t.name == '2_1'][0], 'B8', 'C9:H22', 'C8', 'Sample Size', periodTitle, incomeTitle, '', True, unitVal1, '1')
    tbl2_1 = extract_sheet_single_table('2_1', [t for t in sheets if t.name == '2_2'][0], 'B8', 'C9:M31', 'C8', 'Sample size', regionTitle, incomeTitle, currYr, True, unitVal1, '1')
    tbl2_2 = extract_sheet_single_table('2_2', [t for t in sheets if t.name == '2_2'][0], 'B37', 'C38:H60', 'C37', 'Sample size', regionTitle, incomeTitle, currYr, True, unitVal1, '1')
    tbl3 = extract_sheet_single_table('3', [t for t in sheets if t.name == '2_3'][0], 'B8', 'C9:M23', 'C8', 'Sample size', ethnicTitle, incomeTitle, threeYr, True, unitVal1, '3')
    tbl4 = extract_sheet_single_table('4', [t for t in sheets if t.name == '2_4'][0], 'B8', 'C9:M22', 'C8', 'Sample size', ageTitle, incomeTitle, currYr, True, unitVal1, '1')
    tbl5 = extract_sheet_single_table('5', [t for t in sheets if t.name == '2_5'][0], 'B8', 'C9:O42', 'C8', 'Sample size', houseCompTitle, wklyIncomeTitle, currYr, True, unitVal1, '1')
    print('Count 1: ' + str(tbl5[houseCompTitle].count()))
    tbl5 = fixTable2_5(tbl5)
    print('Count 2: ' + str(tbl5[houseCompTitle].count()))
    tbl6 = extract_sheet_single_table('6', [t for t in sheets if t.name == '2_6'][0], 'B8', 'C9:O32', 'C8', 'Sample size', regionTitle, wklyIncomeTitle, currYr, True, unitVal1, '1')
    tbl7 = extract_sheet_single_table('7', [t for t in sheets if t.name == '2_7'][0], 'B8', 'C9:O23', 'C8', 'Sample size', ethnicTitle, wklyIncomeTitle, threeYr, True, unitVal1, '3')
    tbl8 = extract_sheet_single_table('8', [t for t in sheets if t.name == '2_8'][0], 'B8', 'C9:S41', 'C8', 'Sample size', steSupTitle, regionTitle, currYr, False, unitVal1, '1')
    tbl9 = extract_sheet_single_table('9', [t for t in sheets if t.name == '2_9'][0], 'B8', 'C9:Q42', 'C8', 'Sample size', steSupTitle, benUntTitle, currYr, False, unitVal1, '1')
    tbl10 = extract_sheet_single_table('10', [t for t in sheets if t.name == '2_10'][0], 'B8', 'C9:M42', 'C8', 'Sample size', steSupTitle, ethnicTitle, threeYr, False, unitVal1, '3')
    tbl11 = extract_sheet_single_table('11', [t for t in sheets if t.name == '2_11'][0], 'B8', 'C9:L42', 'C8', 'Sample size', steSupTitle, ageTitle, currYr, False, unitVal1, '1')
    tbl12 = extract_sheet_single_table('12', [t for t in sheets if t.name == '2_12'][0], 'B8', 'C9:H42', 'C8', 'Sample size', steSupTitle, tenureTitle, currYr, False, unitVal1, '1')
    tbl13 = extract_sheet_single_table('13', [t for t in sheets if t.name == '2_13'][0], 'B8', 'C9:K42', 'C8', 'Sample size', steSupTitle, econStatTitle, currYr, False, unitVal1, '1')
    tbl14_1 = extract_sheet_single_table('14_1', [t for t in sheets if t.name == '2_14'][0], 'B7', 'C8:E21', 'C7', 'Sample size', annAmtTitle, periodTitle, '', False, unitVal2, '1')
    tbl14_2 = extract_sheet_single_table('14_2', [t for t in sheets if t.name == '2_14'][0], 'B24', 'C25:E38', 'C24', 'Sample size', annAmtTitle, periodTitle, '', False, unitVal1, '1')

except Exception as e:
    print(str(e))

# +
 
allTbls = [tbl1, tbl2_1, tbl2_2, tbl3, tbl4, tbl5, tbl6, tbl7, tbl8, tbl9, tbl10, tbl11, tbl12, tbl13, tbl14_1, tbl14_2]
#tbl5[houseCompTitle].unique()
# -

#### STRIP THE NUMBER OFF THE END OF THE STRING AS WELL AS \N AND COMMA
for t in allTbls:
    for x in range(10): 
        if (x > 0):
            for ttl in allMainTitles:
                if ttl in t.columns:
                    #t[markerTitle][t[ttl].str.contains(str(x))] += ' ' + str(x)
                    #t[markerTitle] = t[markerTitle].str.lstrip()
                    t[ttl] = t[ttl].str.replace('\n',' ')
                    t[ttl] = t[ttl].str.strip(str(x))
                    t[ttl] = t[ttl].str.strip(',')
    for x in range(10): 
        if (x > 0):
            for ttl in allMainTitles:
                if ttl in t.columns:
                    #t[markerTitle][t[ttl].str.contains(str(x))] += ' ' + str(x)
                    #t[markerTitle] = t[markerTitle].str.lstrip()
                    t[ttl] = t[ttl].str.replace('\n',' ')
                    t[ttl] = t[ttl].str.strip(str(x))
                    t[ttl] = t[ttl].str.strip(',')

# +
#### Set all the names of output observation datasets
tableHeadings = [
    "DWP - Family Resource Survey - Sources of total gross household income by Region - Ethnic group - Age of head",
    "Table 2.5 - Households by composition and total gross weekly household income",
    "Table 2.6 - Households by region/country and gross weekly household income",
    "Table 2.7 - Households by ethnic group of head and gross weekly household income",
    "Table 2.8 - Benefit units by state support receippt and region/country",
    "Table 2.9 - Benefit units by state support receipt and benefit type unit",
    "Table 2.10 - Benefit units by state support receipt and ethnic group of head",
    "Table 2.11 - Benefit units by state support receipt and age of head",
    "Tabel 2.12 - Benefit units by state support receipt and tenure",
    "Table 2.13 - Benefit units by state support receipt and economic status",
    "Table 2.14_1 - Benefit units by amount of annual state support received - Units",
    "Table 2.14_2 - Benefit units by amount of annual state support received - Percentage"
]


ukTitle = 'United Kingdom'
hhTitle = 'All households'
abTitle = 'All benefit units'
# -

### SOURCES TABLE - Join some tables together adding columns where needed
#### Add various columns
allTbls[0][regionTitle] = ukTitle
allTbls[0][ethnicTitle] = hhTitle
allTbls[0][ageTitle] = abTitle
allTbls[0][incBreakTitle] = 'Higher breakdown'

allTbls[1][ethnicTitle] = hhTitle
allTbls[1][ageTitle] = abTitle
allTbls[1][incBreakTitle] = 'Lower breakdown'

allTbls[2][ethnicTitle] = hhTitle
allTbls[2][ageTitle] = abTitle
allTbls[2][incBreakTitle] = 'Higher breakdown'

allTbls[3][regionTitle] = ukTitle
allTbls[3][ageTitle] = abTitle
allTbls[3][incBreakTitle] = 'Lower breakdown'

allTbls[4][ethnicTitle] = hhTitle
allTbls[4][regionTitle] = hhTitle
allTbls[4][incBreakTitle] = 'Lower breakdown'
#### Set the column order
columnOrder = [periodTitle, ageTitle, regionTitle, ethnicTitle, incBreakTitle, incomeTitle, sampSzeTitle, markerTitle, valueTitle, unitTitle]
allTbls[0] = allTbls[0][columnOrder]
allTbls[1] = allTbls[1][columnOrder]
allTbls[2] = allTbls[2][columnOrder]
allTbls[3] = allTbls[3][columnOrder]
allTbls[4] = allTbls[4][columnOrder]
#### Concatenate the tables 
sourcesTbl = pd.concat([allTbls[0], allTbls[1], allTbls[3], allTbls[4]])

#### Pathify columns
sourcesTbl[ageTitle] = sourcesTbl[ageTitle].str.strip().apply(pathify)
sourcesTbl[regionTitle] = sourcesTbl[regionTitle].str.strip().apply(pathify)
sourcesTbl[ethnicTitle] = sourcesTbl[ethnicTitle].str.strip().apply(pathify)
sourcesTbl[incomeTitle] = sourcesTbl[incomeTitle].str.strip().apply(pathify)
sourcesTbl[incBreakTitle] = sourcesTbl[incBreakTitle].str.strip().apply(pathify)
#sourcesTbl.head(20)

# +
#### HOUSEHOLDS TABLE - Join some tables together adding columns where needed
#### Add various columns
allTbls[5][regionTitle] = ukTitle
allTbls[5][ethnicTitle] = hhTitle

allTbls[6][ethnicTitle] = hhTitle
allTbls[6][houseCompTitle] = hhTitle

allTbls[7][regionTitle] = ukTitle
allTbls[7][houseCompTitle] = hhTitle
#### Set the column order
columnOrder = [periodTitle, houseCompTitle, regionTitle, ethnicTitle, wklyIncomeTitle, sampSzeTitle, markerTitle, valueTitle, unitTitle]
allTbls[5] = allTbls[5][columnOrder]
allTbls[6] = allTbls[6][columnOrder]
allTbls[7] = allTbls[7][columnOrder]

#### Concatenate the tables 
householdsTbl = pd.concat([allTbls[5], allTbls[6], allTbls[7]])

# +
#### Pathify columns
householdsTbl[houseCompTitle] = householdsTbl[houseCompTitle].str.strip().apply(pathify)
householdsTbl[regionTitle] = householdsTbl[regionTitle].str.strip().apply(pathify)
householdsTbl[ethnicTitle] = householdsTbl[ethnicTitle].str.strip().apply(pathify)
householdsTbl[wklyIncomeTitle] = householdsTbl[wklyIncomeTitle].str.replace(',', '', regex=True)
householdsTbl[wklyIncomeTitle] = householdsTbl[wklyIncomeTitle].str.strip().apply(pathify)
householdsTbl[wklyIncomeTitle] = householdsTbl[wklyIncomeTitle].str.replace('ps', '', regex=True)

householdsTbl.head(12)

# +
#### BENEFITS TABLE - Join some tables together adding columns where needed
#### Add various columns
allTbls[8][benUntTitle] = abTitle
allTbls[8][ethnicTitle] = abTitle
allTbls[8][ageTitle] = abTitle
allTbls[8][econStatTitle] = abTitle
allTbls[8][tenureTitle] = abTitle
allTbls[8][annAmtTitle] = abTitle

allTbls[9][regionTitle] = ukTitle
allTbls[9][ethnicTitle] = abTitle
allTbls[9][ageTitle] = abTitle
allTbls[9][tenureTitle] = abTitle
allTbls[9][econStatTitle] = abTitle
allTbls[9][annAmtTitle] = abTitle

allTbls[10][benUntTitle] = abTitle
allTbls[10][regionTitle] = ukTitle
allTbls[10][ageTitle] = abTitle
allTbls[10][tenureTitle] = abTitle
allTbls[10][econStatTitle] = abTitle
allTbls[10][annAmtTitle] = abTitle

allTbls[11][regionTitle] = ukTitle
allTbls[11][ethnicTitle] = abTitle
allTbls[11][tenureTitle] = abTitle
allTbls[11][econStatTitle] = abTitle
allTbls[11][annAmtTitle] = abTitle
allTbls[11][benUntTitle] = abTitle

allTbls[12][ethnicTitle] = abTitle
allTbls[12][ageTitle] = abTitle
allTbls[12][regionTitle] = ukTitle
allTbls[12][econStatTitle] = abTitle
allTbls[12][annAmtTitle] = abTitle
allTbls[12][benUntTitle] = abTitle

allTbls[13][ethnicTitle] = abTitle
allTbls[13][ageTitle] = abTitle
allTbls[13][regionTitle] = ukTitle
allTbls[13][tenureTitle] = abTitle
allTbls[13][annAmtTitle] = abTitle
allTbls[13][benUntTitle] = abTitle

allTbls[14][steSupTitle] = abTitle
allTbls[14][ethnicTitle] = abTitle
allTbls[14][ageTitle] = abTitle
allTbls[14][regionTitle] = ukTitle
allTbls[14][tenureTitle] = abTitle
allTbls[14][econStatTitle] = abTitle
allTbls[14][benUntTitle] = abTitle

allTbls[15][steSupTitle] = abTitle
allTbls[15][ethnicTitle] = abTitle
allTbls[15][ageTitle] = abTitle
allTbls[15][regionTitle] = ukTitle
allTbls[15][tenureTitle] = abTitle
allTbls[15][econStatTitle] = abTitle
allTbls[15][benUntTitle] = abTitle
#### Set the column order
columnOrder = [periodTitle, steSupTitle, ethnicTitle, ageTitle, regionTitle, tenureTitle, econStatTitle, annAmtTitle, benUntTitle, sampSzeTitle, markerTitle, valueTitle, unitTitle]
allTbls[8] = allTbls[8][columnOrder]
allTbls[9] = allTbls[9][columnOrder]
allTbls[10] = allTbls[10][columnOrder]
allTbls[11] = allTbls[11][columnOrder]
allTbls[12] = allTbls[12][columnOrder]
allTbls[13] = allTbls[13][columnOrder]
allTbls[14] = allTbls[14][columnOrder]
allTbls[15] = allTbls[15][columnOrder]

#### Concatenate the tables 
benefitsTbl = pd.concat([allTbls[8], allTbls[9], allTbls[10], allTbls[11], allTbls[12], allTbls[13], allTbls[14], allTbls[15]])
# -

#### Pathify columns
benefitsTbl[steSupTitle] = benefitsTbl[steSupTitle].str.strip().apply(pathify)
benefitsTbl[ethnicTitle] = benefitsTbl[ethnicTitle].str.replace('/ ', ' ', regex=True)
benefitsTbl[ethnicTitle] = benefitsTbl[ethnicTitle].str.strip().apply(pathify)
benefitsTbl[ageTitle] = benefitsTbl[ageTitle].str.strip().apply(pathify)
benefitsTbl[regionTitle] = benefitsTbl[regionTitle].str.strip().apply(pathify)
benefitsTbl[tenureTitle] = benefitsTbl[tenureTitle].str.strip().apply(pathify)
benefitsTbl[econStatTitle] = benefitsTbl[econStatTitle].str.strip().apply(pathify)
benefitsTbl[annAmtTitle] = benefitsTbl[annAmtTitle].str.replace(',', '', regex=True)
benefitsTbl[annAmtTitle] = benefitsTbl[annAmtTitle].str.strip().apply(pathify)
benefitsTbl[benUntTitle] = benefitsTbl[benUntTitle].str.strip().apply(pathify)
#benefitsTbl[benUntTitle].unique()

# +
#### Set up the folder path for the output files
from pathlib import Path

out = Path('out')
out.mkdir(exist_ok=True, parents=True)

# +
# Output Observation.csv files
# Create and output Schema.json files
# Create and output metadata.trig files

import numpy as np

fn1 = 'sources-of-income-by-region-ethnicity-age'
fn2 = 'households-by-composition-region-ethnicity'
fn3 = 'benefits-units-state-support-received-by-region-benefit-ethnicity-age-tenure-economic-status-amount'
fleNmes = [fn1, fn2, fn3]
tblData = [sourcesTbl, householdsTbl, benefitsTbl]

scraper.dataset.family = 'affordable-housing'

i = 0
for fn in fleNmes:
    if ethnicTitle in tblData[i].columns:
        tblData[i][ethnicTitle] = tblData[i][ethnicTitle].str.replace('/', '-', regex=True)
    if annAmtTitle in tblData[i].columns:
        tblData[i][annAmtTitle] = tblData[i][annAmtTitle].str.replace('ps', '', regex=True) # ££££££££

    
    tblData[i].drop_duplicates().to_csv(out / (fn + '.csv'), index = False)
    scraper.set_dataset_id(f'gss_data/affordable-housing/dwp-family-resources-survey-income-and-state-support/{fn}/')
    with open(out / ('pre' + fn + '.csv-metadata.trig'), 'wb') as metadata:metadata.write(scraper.generate_trig())
    csvw = CSVWMetadata('https://gss-cogs.github.io/family-affordable-housing/reference/')
    csvw.create(out / (fn + '.csv'), out / ((fn + '.csv') + '-schema.json'))
    i = i + 1
# -

headMain = 'Family Resources Survey: financial year 2017/18'

import os
i = 1 #### Main looping index
k = 1 #### Secondary index to skip over lines with ns2
lineWanted = False
#### Loop around each element in the main heading list
for fn in fleNmes:
    newDat = ''
    curNme = f'out/pre{fn}.csv-metadata.trig'    #### Current file name
    newNme = f'out/{fn}.csv-metadata.trig'       #### New file name
    #### Open the file and loop around each line adding or deleting as you go
    with open(curNme, "r") as input:
        #### Also open the new file to add to as you go
        with open(newNme, "w") as output: 
            #### Loop around the input file
            for line in input:
                #### Change the lines to the value in the variabl headMain
                if headMain in line.strip("\n"):
                    newLine = line
                    newLine = line.replace(headMain, 'DWP - ' + headMain + ' - ' + fn)
                    output.write(newLine)
                else: 
                    lineWanted = True
                    #### Ignore lines with ns2 but loop for other ns# lines, deleteing any extra ones that do not match the value of k
                    if '@prefix ns2:' not in line.strip("\n"):
                        if '@prefix ns' in line.strip("\n"):
                            if f'@prefix ns{k}:' not in line.strip("\n"):
                                #### You do not want this line so ignore
                                lineWanted = False
                    #### If the line is needed check if it is a line that needs changing then write to new file 
                    if lineWanted: 
                        if 'a pmd:Dataset' in line.strip("\n"):
                            line = line.replace(f'{fn}/', f'{fn}')

                        if 'pmd:graph' in line.strip("\n"):
                            line = line.replace(f'{fn}/', f'{fn}')
                        #### Output the line to the new file                    
                        output.write(line)

    #### Close both files
    input.close
    output.close
    #### Old trig file no longer needed so remove/delete
    os.remove(curNme)
    #### Increment i, ns2 is used for something else so you have got to jump k up by 1 at this point
    i = i + 1
    if i == 2:
        k = k + 2
    else:
        k = k + 1














