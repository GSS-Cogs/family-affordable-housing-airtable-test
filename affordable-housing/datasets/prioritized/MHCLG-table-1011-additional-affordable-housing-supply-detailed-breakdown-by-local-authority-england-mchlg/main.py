# # MHCLG-table-1011-additional-affordable-housing-supply-detailed-breakdown-by-local-authority-england-mchlg 

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