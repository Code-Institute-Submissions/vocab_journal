import requests
import json

# TODO: replace with your own app_id and app_key
app_id = '413b2e3a'
app_key = '84354fe4c72b838606558498c33f6eb1'

language = 'en'
word_id = 'fickle'

# url = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/' + language + '/' + word_id.lower() + '/synonyms;antonyms'
url = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/' + language + '/' + word_id.lower()

r = requests.get(url, headers = {'app_id': app_id, 'app_key': app_key})

print("code {}\n".format(r.status_code))
# print("text \n" + r.text)
# print(r.text)
# print("json \n" + json.dumps(r.json()))
g = r.json()

results = g["results"][0]
print(type(results), results.keys())
print("="*30)
# for key in results.keys():
#   print(key, results[key])
print("="*30)

print(results["lexicalEntries"][0].keys())
for x in results["lexicalEntries"][0].keys():
  print("x = ",x,results["lexicalEntries"][0][x])

final = results["lexicalEntries"][0]["entries"][0]
# print("final = ", type(final))
# print("final = ", final["definitions"])

print("\n\n")

# print(final["senses"][0])
final2 =  final["senses"][0]
print(final2["definitions"])
print(final2["short_definitions"])
print(final2["examples"])