# # MHCLG-table-1012-affordable-housing-starts-and-completions-funded-by-homes-england-and-the-gla-mchlg 

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