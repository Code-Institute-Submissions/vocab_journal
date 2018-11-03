import requests
import json

# TODO: replace with your own app_id and app_key
app_id = '413b2e3a'
app_key = '84354fe4c72b838606558498c33f6eb1'
language = 'en'

# word_id = 'myriad'

# # url = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/' + language + '/' + word_id.lower() + '/synonyms;antonyms'
# url = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/' + language + '/' + word_id.lower()

# r = requests.get(url, headers = {'app_id': app_id, 'app_key': app_key})

# print("code {}\n".format(r.status_code))
# # print("text \n" + r.text)
# # print(r.text)
# # print("json \n" + json.dumps(r.json()))
# g = r.json()

# results = g["results"][0]
# print(type(results), results.keys())

# # for key in results.keys():
# # #   print(key, results[key])
# #   print(key)
# print('results["lexicalEntries"] type = ', type(results["lexicalEntries"]))
# for key in results["lexicalEntries"]:
#     print(key)
# # print(results["lexicalEntries"][0].keys())

# # for x in results["lexicalEntries"][0].keys():
# #   print("x = ",x,results["lexicalEntries"][0][x])
# # print(results["lexicalEntries"]['definitions'])
# # print("final = ", type(final))


# print("\n\n")
# final = results["lexicalEntries"][0]["entries"][0]
# # print(final["senses"][0])
# final2 =  final["senses"][0]
# print(final2["definitions"])
# print(final2["short_definitions"])
# print(final2["examples"])

class OxDictApi:
    
    """ 
    do various task with dictionary api:
    get definition of a word
    get synonyms of a word
    get example sentences for a word
        
    """
    
    def __init__(self, word):
        self.word = word
        
    def get_definition(self):
        """ get word definitions """
        
        url = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/' + language + '/' + self.word.lower() + '/' + 'definitions'
        r = requests.get(url, headers = {'app_id': app_id, 'app_key': app_key})
        print("code {}\n".format(r.status_code))
        g = r.json()
        # print(g)
        # for k in g:
        #     print(type(k), k)
        
        
        
        # TIER 1 - get number of results!
        # print(len(g["results"]) , type(g["results"]))
        print("'{}' generated {} results in a list format".format(self.word, len(g["results"]) ) )
        
        # TIER 2 - get total number of lexicalEntries
        print(len(g["results"][0]["lexicalEntries"]), type(g["results"][0]["lexicalEntries"]))
        print("\tthere are a total of '{}' lexicalEntries in {} format ".format( len(g["results"][0]["lexicalEntries"]), type(g["results"][0]["lexicalEntries"]) ) )
        
        # contains list of dictionaries for each lexicalEntries ("Noun", "Adjective" and so on)
        lexicalEntries = g["results"][0]["lexicalEntries"]
        for lexicalEntry in lexicalEntries:
            lexicalCategory = lexicalEntry["lexicalCategory"]
            contents = lexicalEntry["entries"] # contains list of dicts [{"definition: []"},{"definition: []"}]
            print(" ")
            print("lexicalCategory = ", lexicalCategory)
            print("contents = ", contents)
            for content in contents:
                senses = content["senses"]
                for sense in senses:
                    for vocab_def in sense["definitions"]:
                        print("vocab_def = ", vocab_def)
                try:
                    subsenses = content["subsenses"]
                    for subsense in subsenses:
                        for vocab_def in subsense["definitions"]:
                            print("vocab_def = ", vocab_def)
                except:
                    pass

        print("\n\n================================================")

        
        defs_output = dict()
        results = g["results"]
        for resultNum in range(len(results)):
            print("Analysing result number '{}' for '{}'".format(len(g["results"]), self.word ) )
            
            # contains list of dictionaries for each lexicalEntries ("Noun", "Adjective" and so on)
            lexicalEntries = results[resultNum]["lexicalEntries"]
            for lexicalEntry in lexicalEntries:
                lexicalCategory = lexicalEntry["lexicalCategory"]
                lexicalEntryContent = lexicalEntry["entries"]
                
                print("lexicalCategory = ", lexicalCategory) # "Noun", "Adjective"
                # print("lexicalEntryContent = ", lexicalEntryContent) # content of "Noun" or "Adjective"
                
                contents = lexicalEntry["entries"] # contains list of dicts [{"definition: []"},{"definition: []"}]
                def_list = []
                for content in contents:
                    
                    senses = content["senses"]
                    for sense in senses:
                        for vocab_def in sense["definitions"]:
                            print("vocab_def = ", vocab_def)
                            def_list.append(vocab_def)
                    try:
                        subsenses = content["subsenses"]
                        for subsense in subsenses:
                            for vocab_def in subsense["definitions"]:
                                print("vocab_def = ", vocab_def)
                                def_list.append(vocab_def)
                    except:
                        pass                
                    print("def_list = ", def_list)
                    
                defs_output[lexicalCategory] = def_list
                

        return defs_output



# get_definition("myriad")

myLocalDict = OxDictApi("quick")
# myLocalDict = OxDictApi("myriad")
# myLocalDict = OxDictApi("hierarchy")
kkobj = myLocalDict.get_definition()

for k,v in kkobj.items():
        print("vocab as '{}' with definitions: {}".format(k,v))