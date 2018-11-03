from py_define import OxDictApi






# myLocalDict = OxDictApi("quick") 
# myLocalDict = OxDictApi("kill")
myLocalDict = OxDictApi("myriad", 5)
# myLocalDict = OxDictApi("hierarchy")
# myLocalDict = OxDictApi("kos")


# status , kkobj = myLocalDict.get_definitions()
status , kkobj = myLocalDict.get_synonyms()

# print("status = ", status)
# for k,v in kkobj.items():
#         print("vocab as '{}' with definitions: {}".format(k,v))