#!/net/local/home/gulleyd/Documents/Scripts/venv/bin/python python2
"""
bulletin.py

To hold the properties of advisory or warnings retrieved for CWUL

Bulletin public properties
url     : string   - Location of the bulletin in the datamart
kind    : string   - Two-letter code denoting advisory/warning/other bulletins
body    : string   - Full bulletin text
date    : string   - When the bulletin was issued*
ID      : string   - Trailing text for bulletin
regions : string   - Regions affected **

Created 2025-02-27

*  Note: bulletin_associator relies on date to return as a string and not a datetime object for the moment
"""
import urllib
class bulletin:

    # Properties passed into the class
    url = ''
    
    # Properties determined by reading the URL
    kind = '' # WO WW - Advisory or Warning respectively
    body = "" # The bulletin text itself
    date = None # datetime for when the bulletin was issued
    ID = ''
    office = 'CWUL'
    
    # Properties determined by the splitting the body into sections on instantiation
    info = ""
    regions = ""
    description = ""
        
    
    def __init__(self,url):
        
        base_url = 'https://dd.weather.gc.ca/bulletins/alphanumeric/'
         
        self.url = url
        
        # https://dd.weather.gc.ca/bulletins/alphanumeric/20250217/WO/CWUL/09/WOCN10_CWUL_170915___36248
        
        self.body =  urllib.urlopen(url).read()
        
        
        # This is all information based off of the current naming conventions on datamart
        url_info = url.split(base_url)[1].split('/') # Retrieves everything in the url trailing alphanumeric/
        # Example
        # ['20250217','WO','CWUL','09','WOCN10_CWUL_170915___36248']
        self.date = url_info[0]
        self.kind = url_info[1]
        self.office = url_info[2]
        self.ID = url_info[3]
        
        
        # Assuming the typical format, split the body into sections, not valid for AW
        try :
            section = self.body.split('---------------------------------------------------------------------')
            
            self.info = section[0]        # Contains kind body and date unformatted
            self.regions = section[1]     # Regions affected by the Bulletin
            self.description = section[2] # Detailed description of the event and impacts
            
        except IndexError: # This happens when the section could not be split into the different regions due to unusual formatting
            
            # Just include everything in 
            self.info = 'Unusal format: see description'
            self.regions = 'Unusual format: see description'
            self.description = self.body
