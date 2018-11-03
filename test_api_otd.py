from py_define import OxDictApi






# myLocalDict = OxDictApi("quick") 
# myLocalDict = OxDictApi("kill", 5)
myLocalDict = OxDictApi("myriad")
# myLocalDict = OxDictApi("hierarchy")
# myLocalDict = OxDictApi("kos")
status , kkobj = myLocalDict.get_definitions()

print("status = ", status)
for k,v in kkobj.items():
        print("vocab as '{}' with definitions: {}".format(k,v))