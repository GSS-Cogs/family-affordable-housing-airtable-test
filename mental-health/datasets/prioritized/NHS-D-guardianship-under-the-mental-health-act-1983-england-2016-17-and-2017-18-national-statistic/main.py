# # NHS-D-guardianship-under-the-mental-health-act-1983-england-2016-17-and-2017-18-national-statistic 

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