#!/net/local/home/gulleyd/Documents/Scripts/venv/bin/python python2
# -*- coding: UTF-8 -*-
"""
menu_fr.py

This is a simplified version of the bulletin associator old_menu.py wrapper meant mainly just to browse, view, and sort bulletins.

Unfinished, last update 2025-04-04
"""
version = '1.0'

from os import system as sys
sys('clear')
print('---------------- Outil de navigation des bulletins {0} ----------------\nOutils en chargement...'.format(version))
from bulletin_associator import retrieve_by_date , chain_bulletins, correlation_matrix
import pickle
import datetime as dt
print('9 jours de bulletins en chargement...')
bulletin_list = retrieve_by_date() # By default just loads the previous 9 days wortth of bulletins
lang_loaded = False # Default import of bulletins by language
C = None # The correlation matrix
chain = None # Holds the library of bulletins and their correlations with all other associated bulletins forwards or backwards in time
print('Fait!')

def submenu(options):
    """
    Prints a submenu with the list of options the user may select
    
    params
        options   : array-like string - items displayed in the menu
    return
        selection : string            - selected item from menu items
    
    """
    proceed = False
    option_numbers = [str(i+1) for i in range(len(options))]
    for option,i in zip(options,option_numbers):
        print('{0}) {1}'.format(i, option))
    
    while not proceed:
        selection = raw_input('\n> ').strip()
        proceed = selection in option_numbers
    
    return selection


def load_bulletins():
    global bulletin_list
    global lang_loaded
    sys('clear')
    print('-- Charger bulletins --')
    
    
    selection = submenu(['Charger dans une plage de dates', 'Charger depuis 9 jours jusqu\'à maintenant','Charger depuis n-jours jusqu\'à maintenant','Revenir à l\'outil de navigation'])
    
    input_str = ''
    if selection == '1': # Load within a date range
        
        # Space to hold the start and end dates for the bulletin retrieval
        startdate = dt.datetime.now()
        enddate = dt.datetime.now()
        
        # Ask for raw_input of a date range
        while True:
            try: # check formatting, if wrong, ask again
                input_str = raw_input('Entrez une date de début au format yyyy-mm-dd:\n>')
                year_month_day_1 = [int(i) for i in input_str.split('-')] # Split the user input into year-month-day
                
                input_str = raw_input('Entrez une date de fin au format yyyy-mm-dd:\n> ')
                year_month_day_2 = [int(i) for i in input_str.split('-')] # Split the user input into year-month-day
                
                # Load the datetimes
                startdate = dt.date(year_month_day_1[0],year_month_day_1[1],year_month_day_1[2])
                enddate = dt.date(year_month_day_2[0],year_month_day_2[1],year_month_day_2[2])
                
                # If the user mixed up the start and end dates, mix them up right
                if startdate > enddate :
                    holder = startdate
                    startdate = enddate
                    enddate = holder
                break
            
            except ValueError:
                print('Veuillez entrez une date valide')
            except TypeError:
                print('Veuillez entrez une date valide')
            except IndexError:
                print('Veuillez entrez une date valide')
        # Use bulletin_associator.retrieve_by_date(start,end)
        print('Chargement en cours, veuillez patienter')
        bulletin_list = retrieve_by_date(startdate,enddate)
        
    elif selection == '2': # Load previous 9 days
        print('Chargement en cours, veuillez patienter')
        bulletin_list = retrieve_by_date() # Defaults
    
    elif selection == '3': # Load previous n-days
        # Ask for number of days ago
        # Check formatting, if wrong, ask again
        days = 0
        while True:
            try: # check formatting, if wrong, ask again
                input_str = raw_input('Entrez la nombre des jours:\n> ')
                days =int( (( int(input_str) )**2 )**(0.5) )
                break
                
            except ValueError:
                print('Veuillez entrez une nombre')
        # use bulletin_associator.retrieve_by_date(start) and load into bulletins
        print('Chargement en cours, veuillez patienter')
        bulletin_list = retrieve_by_date(startdate = dt.datetime.now() - dt.timedelta(days=days), enddate = dt.datetime.now())
    elif selection == '4':
        browser()
        
    lang_loaded = False # The retrieved list can now be filtered by language once more
    browser()


def print_bulletins():
    sys('clear')
    if bulletin_list != None:
        for i in bulletin_list:
            print(i.url)
    else: # The application has not pulled any bulletins
        load_bulletins()
        print_bulletins()
    print('{0} dans cette liste'.format(len(bulletin_list)))
    
    selection = submenu(['Montrer le corps du texte de chaucun','Revenir à l\'outil de navigation'])
    if selection == '1':
        sys('clear')
        print_bulletin_text(bulletin_list)
    elif selection == '2':
        browser()

def print_bulletin_text(list_to_search,to_browser=True):
    sys('clear')
    if list_to_search != None:
        for i in list_to_search:
            print('\n\n******************************************************************************************************************************************')
            print(i.url)
            print('******************************************************************************************************************************************')
            print(i.body)
    else:
        print('\nAucun bulletin dans cette liste')
    print('******************************************************************************************************************************************')
    raw_input('Maintenez Ctrl+Maj+C en copiant de Konsole\nAppuyez sur entrée pour revenir...')
    if to_browser:
        browser()
    
def url_by_language(lang_code = 'CN7'):
    """
    URLS containing CN7 are French
    URLS containing CN1 are English
    
    Eliminates bulletins not in the requested language 
    """
    global bulletin_list
    
    if bulletin_list != None:
        bulletin_list = [b for b in bulletin_list if lang_code in b.url]
    

def url_by_variable(list_to_search):
    global bulletin_list
    # Prints the sublist of bulletins of a specific warning type
    variable = raw_input('Veuillez entrer les types de bulletin dont vous voudriez chercher: \n> ')
    variable = variable.split(' ') # Multiple variables to search
    matched_list = []
    for v in variable:
        for b in list_to_search:
            if v.upper() in b.url.split('/')[6]:
                print(b.url)
                matched_list.append(b)
                
    if matched_list != []:
        print('\n{0} bulletins dans cette liste'.format(len(matched_list)))
        print('Correspondent au type demandé\n')
        selection = submenu(['Chercher un autre type','Enregistrer cette liste et revenir à l\'outil de navigation','Revenir à l\'outil de navigation'])
        
        if selection == '1':
            url_by_variable(list_to_search)
        elif selection == '2':
            bulletin_list = matched_list
            browser()
        elif selection == '3':
            browser()
    else:
        print('Type de bulletin pas trouvé dans votre liste')
        selection = submenu(['Chercher un autre type','Revenir à l\'outil de navigation'])
        if selection == '1':
            url_by_variable(list_to_search)
        elif selection == '2':
            browser()
            
            
def keyword_search(list_to_search):
    global bulletin_list
    keyword = raw_input('Entrez un mot-clé à chercher: \n> ')
    matched_list = [] 
    for b in list_to_search:
        if keyword.upper().replace('-',' ') in b.body.upper().replace('-',' '):
            matched_list.append(b)
    
    if matched_list == []:
        print('Mot-clé pas trouvé dans votre liste enregistrée.\nQu\'est-ce que vous aimez faire?')
        selection = submenu(['Chercher un autre mot','Revenir à l\'outil de navigation'])
        if selection == '1':
            keyword_search(list_to_search)
        elif selection == '2':
            browser()
            
    else: # The keywrod exists in list_to_search
        print('Mot-clé détecté dans les bulletins suivants:')
        for i in matched_list:
            print(i.url)
        print('\n{0} bulletins dans cette liste'.format(len(matched_list)))

        print('\nQu\'est-ce que vous aimez faire?')
        selection = submenu(['Chercher dans cette liste un autre mot-clé','Enregistrer cette liste et revenir à l\'outil de navigation','Revenir à l\'outil de navigation'])
        
        if selection == '1':
            keyword_search(matched_list)
        elif selection =='2':
            bulletin_list = matched_list    
            browser()
        elif selection == '3':
            browser()
        
def print_related(num_elements,url):
    """
    Recursively lists more bulletins
    """
    global chain

    for i in chain[url][num_elements-5:num_elements]: # i is in the form [bulletin1_selected_by_user,associated_bulletin, correlation_value]
        print(i[1].url + '      ==Description== similarité: {0}% '.format(int(round(float(i[2])*100))).replace(' 0%', 'différents').replace('100%','identiques'))
                
    print('----------')
    selection = submenu(['Montre plus...','Montrer le corps du texte de chaucun','Revenir à l\'outil de navigation'])
    
    if selection == '1' :
        print_related(num_elements+5,url)
    elif selection == '2':
        print_bulletin_text([ch[1] for ch in chain[url][num_elements-5:num_elements]],to_browser=False) # i is in the form [bulletin1_selected_by_user,associated_bulletin, correlation_value]
        sys('clear')
        print_related(num_elements,url)
    elif selection == '3' :
        browser()


def bulletins_from_url():
    global bulletin_list
    global C
    global chain
    sys('clear')
    print('-- Trouver par URL les bulletins les plus probablement connectés --')
    
    if bulletin_list == None:
        load_bulletins()
    
    
    if chain == None:
        print('Trouver les bulletins:\n')
        selection = submenu(['Plus vieux que le mien (chercher en arrière dans le temps)','Plus récents que le mien (chercher en avant dans le temps)'])
        
        
        if selection == '1': # Older than my bulletin (look backwards in time)
            print('En les associant ensemble, veuillez patienter...')
            C = correlation_matrix(bulletin_list=bulletin_list,correlate_by='description',descending_dates=True)
            chain = chain_bulletins(C)
            
        elif selection == '2': # Newer than my bulletin (look forwards in time)
            print('En les associant ensemble, veuillez attendre...')
            C = correlation_matrix(bulletin_list=bulletin_list,correlate_by='description',descending_dates=False)
            chain = chain_bulletins(C)
        elif selection == '3':
            browser()
    
    url = raw_input('Tapez l\'URL de votre bulletin pour trouver les autres les plus liés\n> ')
    print('\n')
    if chain == None or url not in chain.keys():
        print('Ça semble que cet URL ne correspond avec aucun autre.')
        selection = submenu(['Chercher avec une URL differente','Réassocier les bulletins','Charger une liste differente','Revenir à l\'outil de navigation' ])
        if selection == '1':
            bulletins_from_url()
        elif selection == '2':
            chain = None
            bulletins_from_url()
        elif selection == '3':
            bulletin_list == None
            chain = None
            load_bulletins()
        elif selection == '4':
            browser()
    else:
        print('Les suivants ont les descriptions les plus similaires que votre sélection:')
        print_related(5,url)
    sys('clear')
    browser()


def browser():    
    # For viewing 
    global bulletin_list
    global lang_loaded
    if bulletin_list != None: # Can only browse bulletins if they've been loaded
        
        if lang_loaded == False : # Fr program contains no Eng bulletins, Eng program contains no Fr bulletins
            print('Filtrage par la langue...')
            url_by_language('CN7') 
            lang_loaded = True
        sys('clear')
        print('-- Outil de navigation des {0} bulletins chargé --'.format(len(bulletin_list)))
        
        selection = submenu(['Chercher un mot-clé','Énumérer les bulletins chargés','Récuperer par type (comme AW WW)', 'Charger bulletins differents','Outil de similarité des descriptions','Aide', 'Sortir'])
        if selection == '1':
            keyword_search(bulletin_list)
        elif selection == '2': # List loaded bulletins
            print_bulletins()
        elif selection == '3':
            sys('clear')
            url_by_variable(bulletin_list)
        elif selection == '4':
            load_bulletins()
        elif selection == '5':
            bulletins_from_url()
        elif selection == '6':
            sys('less aide.txt')
        elif selection == '7':
            quit()
    else: # To load bulletins before browsing
        load_bulletins()
        browser()


browser()

