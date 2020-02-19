# # MHCLG Table 1000  additional affordable homes provided by type of scheme, England  MHCLG 

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