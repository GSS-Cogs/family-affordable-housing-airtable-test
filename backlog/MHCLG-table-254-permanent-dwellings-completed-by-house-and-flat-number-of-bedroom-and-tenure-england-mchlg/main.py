# # MHCLG-table-254-permanent-dwellings-completed-by-house-and-flat-number-of-bedroom-and-tenure-england-mchlg 

from gssutils import * 
import json 

info = json.load(open('info.json')) 
landingPage = info['Landing Page'] 
landingPage 

# + 
#### Add transformation script here #### 

scraper = Scraper(landingPage) 
scraper.select_dataset(latest=True) 
scraper 