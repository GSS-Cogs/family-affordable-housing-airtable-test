# # MHCLG-table-244-permanent-dwellings-started-and-completed-by-tenure-england-historical-calendar-year-series-mchlg 

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