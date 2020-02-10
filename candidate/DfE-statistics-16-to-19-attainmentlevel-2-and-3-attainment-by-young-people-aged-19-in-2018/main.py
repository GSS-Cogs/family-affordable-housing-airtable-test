# # DfE-statistics-16-to-19-attainmentlevel-2-and-3-attainment-by-young-people-aged-19-in-2018 

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