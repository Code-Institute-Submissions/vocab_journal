import os
import requests
import json
try:
    import setup_config 
except ImportError:
    # taken from the env
    pass
APP_ID = os.getenv("APP_ID")
APP_KEY = os.getenv("APP_KEY")

# --- API PREREQUISITES ---------------------------
language = 'en'

class OxDictApi:
    
    """ 
    do various task with dictionary api:
    get definition of a vocab
    get synonyms of a vocab
    get example sentences for a vocab
        
    """
    
    def __init__(self, word, jdebug=0):
        self.word = word
        self.jdebug = jdebug
        
    def get_definitions(self):
        """ get vocab definitions """
        
        if self.jdebug > 0: print("\nget_definitions() method was called!")
        
        # --- PREREQUISITES ---------------------------
        defs_output = dict() # blank dictionary to store all definintions in - function will return this dictionary once populated!
        url = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/' + language + '/' + self.word.lower() + '/' + 'definitions'
        r = requests.get(url, headers = {'app_id': APP_ID, 'app_key': APP_KEY})
        
        # fetch response_code from API 
        response_code = r.status_code
        
        if self.jdebug > 0: print("response_code = {}".format(response_code))
        
        # response_code "200": vocab was successfully found and picked up by the API
        if response_code == 200:
            g = r.json()
        else:
            # response_code "404": No entry is found matching supplied id and source_language. - BAIL!
            # response_code "500": Internal Error. An error occurred while processing the data. - BAIL!
            return response_code, defs_output

        # --- START ------------------------------------
        results = g["results"] # get all the results to loop over one by one
        for resultNum in range(len(results)):
            if self.jdebug > 0: print("Analysing result number '{}' for '{}'".format(len(g["results"]), self.word ) )
            
            # contains list of dictionaries for each lexicalEntries ("Noun", "Adjective" and so on)
            lexicalEntries = results[resultNum]["lexicalEntries"]
            for lexicalEntry in lexicalEntries:                     # loop over all entries
                lexicalCategory = lexicalEntry["lexicalCategory"]   # "Noun", "Adjective", "Adverb"
                lexicalEntryContents = lexicalEntry["entries"]      # full content of "Noun" or "Adjective" or ...
                
                if self.jdebug > 2: print("\nlexicalCategory = {}".format(lexicalCategory))
                if self.jdebug > 7: print("lexicalEntryContents = ", lexicalEntryContents) 

                def_list = [] # collect all local definitions, senses or subsens(if exists)!
                for content in lexicalEntryContents:
                    
                    # fetch sense contents
                    senses = content["senses"]
                    for sense in senses:
                        for vocab_def in sense["definitions"]:
                            def_list.append(vocab_def) # save vocab definition into "def_list"
                    try:
                        # some vocabs dont have any subsenses
                        # fetch sense subsenses
                        subsenses = content["subsenses"]
                        for subsense in subsenses:
                            for vocab_def in subsense["definitions"]:
                                def_list.append(vocab_def) # save vocab definition into "def_list"
                    except:
                        pass
                    
                    if self.jdebug > 2: print("def_list = ", def_list)
                    
                # store ALL extracted definitions based on their lexicalCategory(noun, adverb, ...)
                defs_output[lexicalCategory] = def_list
                
        if self.jdebug > 4: print("\ndefs_output = {}\n".format(defs_output))  
        
        # NOTE: response_code will be "200" at this point
        return response_code, defs_output
    
    
    
    def get_synonyms(self):
        """ get vocab definitions """
        
        if self.jdebug > 0: print("\get_synonyms() method was called!")
        
        # --- PREREQUISITES ---------------------------
        syns_output = dict() # blank dictionary to store all definintions in - function will return this dictionary once populated!
        url = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/' + language + '/' + self.word.lower() + '/synonyms'
        r = requests.get(url, headers = {'app_id': APP_ID, 'app_key': APP_KEY})
        
        # fetch response_code from API 
        response_code = r.status_code
        
        if self.jdebug > 0: print("response_code = {}".format(response_code))
        
        # response_code "200": vocab was successfully found and picked up by the API
        if response_code == 200:
            g = r.json()
        else:
            # response_code "404": No entry is found matching supplied id and source_language. - BAIL!
            # response_code "500": Internal Error. An error occurred while processing the data. - BAIL!
            return response_code, syns_output
        
        # --- START ------------------------------------
        results = g["results"] # get all the results to loop over one by one
        for resultNum in range(len(results)):
            if self.jdebug > 0: print("Analysing result number '{}' for '{}'".format(len(g["results"]), self.word ) )
            
            # contains list of dictionaries for each lexicalEntries ("Noun", "Adjective" and so on)
            lexicalEntries = results[resultNum]["lexicalEntries"]
            for lexicalEntry in lexicalEntries:                     # loop over all entries
                lexicalCategory = lexicalEntry["lexicalCategory"]   # "Noun", "Adjective", "Adverb"
                lexicalEntryContents = lexicalEntry["entries"]      # full content of "Noun" or "Adjective" or ...
                
                if self.jdebug > 2: print("\nlexicalCategory = {}".format(lexicalCategory))
                if self.jdebug > 7: print("lexicalEntryContents = ", lexicalEntryContents) 

                syn_list = [] # collect all local synonyms, senses or subsens(if exists)!
                for content in lexicalEntryContents:
                    
                    # fetch sense contents
                    senses = content["senses"]
                    for sense in senses:
                        for vocab_syn in sense["synonyms"]:
                            syn_list.append(vocab_syn["text"]) # save vocab synonyms into "syn_list"
                    try:
                        # some vocabs dont have any subsenses
                        # fetch sense subsenses
                        subsenses = content["subsenses"]
                        for subsense in subsenses:
                            for vocab_syn in subsense["synonyms"]:
                                syn_list.append(vocab_syn["text"]) # save vocab synonyms into "syn_list"
                    except:
                        pass
                    
                    if self.jdebug > 2: print("syn_list = ", syn_list)
                    
                # store ALL extracted synonyms based on their lexicalCategory(noun, adverb, ...)
                syns_output[lexicalCategory] = syn_list
        
        if self.jdebug > 4: print("\nsyns_output = {}\n".format(syns_output)) 
        
        # NOTE: response_code will be "200" at this point
        return response_code, syns_output
        
    
    def get_examples(self):
        """ get vocab examples """
        
        if self.jdebug > 0: print("\get_examples() method was called!")
        
        # --- PREREQUISITES ---------------------------
        exas_output = dict() # blank dictionary to store all definintions in - function will return this dictionary once populated!
        url = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/' + language + '/' + self.word.lower() + '/sentences'
        r = requests.get(url, headers = {'app_id': APP_ID, 'app_key': APP_KEY})
        
        # fetch response_code from API 
        response_code = r.status_code
        
        if self.jdebug > 0: print("response_code = {}".format(response_code))
        
        # response_code "200": vocab was successfully found and picked up by the API
        if response_code == 200:
            g = r.json()
        else:
            # response_code "404": No entry is found matching supplied id and source_language. - BAIL!
            # response_code "500": Internal Error. An error occurred while processing the data. - BAIL!
            return response_code, exas_output
        
        # --- START ------------------------------------
        results = g["results"] # get all the results to loop over one by one
        for resultNum in range(len(results)):
            if self.jdebug > 0: print("Analysing result number '{}' for '{}'".format(len(g["results"]), self.word ) )
            
            # contains list of dictionaries for each lexicalEntries ("Noun", "Adjective" and so on)
            lexicalEntries = results[resultNum]["lexicalEntries"]
            for lexicalEntry in lexicalEntries:                     # loop over all entries
                
                lexicalCategory = lexicalEntry["lexicalCategory"]   # "Noun", "Adjective", "Adverb"
                lexicalSentences= lexicalEntry["sentences"] 

                exa_list = [] # collect all local examples
                for sentence in lexicalSentences:
                    exa_list.append(sentence["text"])
                exas_output[lexicalCategory] = exa_list
                

        if self.jdebug > 4: print("\nexas_output = {}\n".format(exas_output)) 
        
        # NOTE: response_code will be "200" at this point
        return response_code, exas_output