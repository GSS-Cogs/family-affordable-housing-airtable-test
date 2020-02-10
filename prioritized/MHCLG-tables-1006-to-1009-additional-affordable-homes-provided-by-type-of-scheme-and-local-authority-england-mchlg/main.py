# # MHCLG-tables-1006-to-1009-additional-affordable-homes-provided-by-type-of-scheme-and-local-authority-england-mchlg 

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