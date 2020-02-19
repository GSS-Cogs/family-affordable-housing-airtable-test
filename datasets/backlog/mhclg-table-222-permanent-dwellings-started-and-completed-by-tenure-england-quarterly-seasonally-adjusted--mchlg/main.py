# # MHCLG Table 222  permanent dwellings started and completed, by tenure, England  quarterly seasonally adjusted  -MCHLG 

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