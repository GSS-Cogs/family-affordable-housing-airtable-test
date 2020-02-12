# # ONS-index-of-cancer-survival-for-clinical-commissioning-groups-in-england-adults-diagnosed-2001-to-2016-and-followed-up-to-2017 

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