import json
import urllib.parse
import requests
import time

with open('attrs.json', 'r') as f:
  data = json.load(f)
f = open('stars9.txt', 'w')

i = 0
for place in data[2620:]:
  print(i)
  i += 1
  search1 = urllib.parse.quote(place["state_name"]+' '+place['attr_name'])
  search2 = urllib.parse.quote(place['attr_name'])
  search3 = urllib.parse.quote("tourist attractions in "+place["state_name"])
  try:
    req = requests.get('https://maps.googleapis.com/maps/api/place/textsearch/json?query='+search1+'&key=AIzaSyAUZ11rhgywcPuyP1ICOF1UCcDDVmSnzKY', timeout=5)
    time.sleep(1)
  except:
    try:
      req = requests.get('https://maps.googleapis.com/maps/api/place/textsearch/json?query='+search2+'&key=AIzaSyAUZ11rhgywcPuyP1ICOF1UCcDDVmSnzKY', timeout=5)
      time.sleep(1)
    except:
      try:
        req = requests.get('https://maps.googleapis.com/maps/api/place/textsearch/json?query='+search3+'&key=AIzaSyAUZ11rhgywcPuyP1ICOF1UCcDDVmSnzKY', timeout=5)
        time.sleep(1)
      except:
        f.write('3.0'+'\n')

  if req.json()['status'] == "ZERO_RESULTS":
    search = urllib.parse.quote(search2)
    req = requests.get('https://maps.googleapis.com/maps/api/place/textsearch/json?query='+search2+'&key=AIzaSyAUZ11rhgywcPuyP1ICOF1UCcDDVmSnzKY', timeout=5)
    time.sleep(1)
    print(req.status_code)
  if req.json()['status'] == "ZERO_RESULTS":
    search = urllib.parse.quote(search3)
    req = requests.get('https://maps.googleapis.com/maps/api/place/textsearch/json?query='+search3+'&key=AIzaSyAUZ11rhgywcPuyP1ICOF1UCcDDVmSnzKY', timeout=5)
    time.sleep(1)
    print(req.status_code)
  results = req.json()['results']
  print(req.status_code)
  if len(results) > 15:
    results = results[:15]
  rating_acc = 0
  for entry in results:
    if 'rating' in entry:
      rating_acc += entry['rating']
  rating_acc = rating_acc/len(results)
  rating_acc = round(rating_acc,2)
  f.write(str(rating_acc)+'\n')
f.close()



  