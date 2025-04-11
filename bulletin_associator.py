#!/net/local/home/gulleyd/Documents/Scripts/venv/bin/python python2
"""
bulletin_associator.py

Associates WW (weather warning), WO (weather advisory or speacial weather statement), WWF (Tornado warning) start and end bulletins pulled from the Weather Bulletin Data Mart (https://dd.weather.gc.ca/) within a specified period. ***

Uses scypi's implementation of the Hamming distance to compare the relative similarity of region descriptions to help meteorologist more easily track weather advisories and statements.

Bulletin search help accessible through https://dd.weather.gc.ca/bulletins/doc/

***  Only Capable of WW WO depending on url_retriever.sh script
**** This will not associate bulletins of different languages as its most recent state it compares only the bulletin description to assign a correlation value

Last modified: 2025-03-07
Devon Gulley devon.gulley@ec.gc.ca for questions or suggestions on usage :)
"""

import datetime as dt
from scipy.spatial import distance
from urllib import urlopen as open # This has completely changed for more updated versions of Python 2to3 can update this script
from bulletin import bulletin
from os import system as sys
from os import popen
from pandas import date_range
from itertools import combinations, groupby

# Location of all bulletins
base_url = 'https://dd.weather.gc.ca/bulletins/alphanumeric/'


def retrieve_by_date (startdate = dt.datetime.now() - dt.timedelta(days = 9), enddate = dt.datetime.now()):
    """ 
    This function is a search tool:
    Retrieves all WW and WO bulletins within startdate and enddate by default within the previous 9 days.
    
    ** A substatial limitation of this right now is that it can only pull for WW and WO, to include more, the user must modify the url_retriever.sh script
    
    Params
        startdatem, enddate : datetime.datetime -- specify the start and end date of the date range of interest, default 9 days ago until now.
        
    Returns
        bulletins : array of type bulletin -- all bulletins within a date range of interest.
    """  
    
    # get_url_by_date_command uses the url_retriever.sh script with the date range 
    get_url_by_date_command = './url_retriever.sh "' + '|'.join(date_range(startdate,enddate).strftime('%Y%m%d')) + '"'
    
    # Sending formatted_range to url_retriever, retrieves array of url strings to be opened through bulletin.py
    all_urls = popen(get_url_by_date_command).read().split('\n')[:-1]
    
    # This retrieves all the bulletins found within the range and loads them into an array of type bulletin to return 
    all_bulletins = [bulletin(url) for url in all_urls]
    
    return all_bulletins


def str_corr(str1,str2):
    """
    Calculates the Hamming distance between two strings of the same size. If the strings are different sizes, add spaces to the end of the smaller until lengths are equal.
    Uses this definition to find a correlation between the strings between 0 -- where the strings are entirely different, to 1.0 -- where they're entirely the same.
    
    Params
        str1, str2 : string
    
    Returns
        float -- the Hamming distance between the same-sized strings.
    
    """
    if(len(str1) == len(str2)):
        return 1. - distance.hamming(list(str1),list(str2))
    
    # To compute the Hamming distance 
    if(len(str1)>len(str2)):
        str2 = str2 + ' '* (len(str1) - len(str2)) # strings should be equal length now
        return str_corr(str1,str2)
    else: # str2 > str1
        return str_corr(str2,str1) # Mix them back to compare the opposite way
        
def compare_two_bulletins(b1,b2,correlate_by='description'):
    """
    Params
        b1           : bulletin - key bulletin 
        b2           : bulletin - associated bulletin
        correlate_by : string   - which bulletin property to compare
    
    Returns 
        Hamming distance between the two bulletin text entries in the info, body, or description (by default) section. 
        The larger the Hamming distance, the more dissimilar they are considered to be, on a scale of 0 being identical to 1 being entirely different. 
        Subtracting this value from 1 gives a sort of quasi correlation value between the bulletins which is to be returned.
    
    * If new info, such as ==New== regions affected, this should be considered when comparing whether or not the bulletins are correlated so for the moment this will use bulletin.description
      to correlate by default.
    """
    
    str1 = ''
    str2 = ''
    
    if correlate_by == 'info':
        str1 = b1.info
        str2 = b2.info
    
    if correlate_by =='body':
        str1 = b1.body
        str2 = b2.body
    
    if correlate_by == 'description' or correlate_by =='':
        str1 = b1.description
        str2 = b2.description
    
    return str_corr(str1,str2)
    
    
    
def correlation_matrix(bulletin_list=None,correlate_by='description',descending_dates=True):
    """
    Calculates the bulletin correlation for each combination of two bulletins in a bulletin list.
    *  Uses itertool combinations to only calculate the lower/upper triangle of the matrix, reducing compute time because 
        - compare_two_bulletins(b1,b2) == compare_two_bulletins(b2,b1)
        - compare_two_bulletins(b1,b1) == 1
    
    
    Params
        bulletin_list    : array of type bulletin -- the list of bulletins to be correlated each bulletin with every other
        descending_dates : boolean                -- specify whether bulletins should be associated forwards in time or backwards, default looks backwards
    
        
    Returns
        3-tuple of each bulletin pair as the first two entries, and the correlation between them as the third
    
    """
    if bulletin_list == None:
        bulletin_list = retrieve_by_date()
    
     # If descending_dates is true, when the correlation matrix is built, it will associate newer bulletins with older bulletins otherwise it's the other way around
    bulletin_list = sorted(bulletin_list,key=lambda b_list: b_list.date,reverse=descending_dates) # Although the bulletins are likely already sorted, this ensures they are correctly
        
    return [(bulletin_i,bulletin_j,compare_two_bulletins(bulletin_i,bulletin_j,correlate_by)) for bulletin_i,bulletin_j in combinations(bulletin_list,2)]


def chain_bulletins(correlation=None):
    """
    For each bulletin it sorts the remaining associations in descending order by correlation value.
    * It is perhaps gratuitous to calculate each past more than two or three associated bulletins, much less hundreds, but it should work nonetheless
    
    
    Params
        correlation : array of 3-tuples (bulletin,bulletin,float) with the first two entries containing the bulletins being associated and the third, their correlation value.
    
    Returns
        bulletin_tree : dictionary of lists of 3-tuples in the form 
        {key_bulletin_url: [ (key_bulletin, 1st_most_highly_associated_bulletin, correlation), (key_bulletin, 2nd_most_highly_associated_bulletin, correlation), etc.. }
        
    Given an array with n distinct bulletins where n>2 this returns n-1 different chains of lengths
        {n   ,
         n-1 ,
         n-2 ,
         ... ,
         2    }
    
    
    ***It may be bad practice to use the key_bulletin's url as the key for each chain so this could change
    """
    
    if correlation == None:
        correlation = correlation_matrix()
        
    # This might break
    grouped = {key_bulletin.url: sorted(list(other_bulletins), key=lambda correlation: correlation[2],reverse=True) for key_bulletin,other_bulletins in groupby(correlation,key=lambda associated_bulletin: associated_bulletin[0])}
    
    return grouped

    
    
