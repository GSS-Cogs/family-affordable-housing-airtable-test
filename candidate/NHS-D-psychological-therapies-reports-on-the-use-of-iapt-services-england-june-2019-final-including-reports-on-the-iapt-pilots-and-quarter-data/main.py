# # NHS-D-psychological-therapies-reports-on-the-use-of-iapt-services-england-june-2019-final-including-reports-on-the-iapt-pilots-and-quarter-data 

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