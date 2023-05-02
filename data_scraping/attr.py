import requests
from bs4 import BeautifulSoup
import re
import time
import base64

proxies = {
   'https': 'http://154.64.211.145:999',
}
URL = "https://www.city-data.com/articles/Florida4.html"
#in line 5, copy and paste the url of the state's page
page = requests.get(URL)

soup = BeautifulSoup(page.content, "html.parser")

places = soup.find_all("a")
links = places.copy()

for place in range(len(places)):
    places[place] = places[place].text
start = places.index("Lily Leon Hotel")
# change the string to the first attraction on that state's page - should match EXACTLY
end = places.index("Portofino Island Resort and Spa")+1
# same thing, but with the last attraction (if multi-column, then last entry of rightmost column)
places = places[start:end]
# print(places)


d = {}
f = open('fl_names.txt', 'w')
#change pa to the abbrev of the state
for p in places:
    f.write(p+'\n')
    d[p] = True
f.close()

descs = open('fl_descs.txt', 'w')
#change pa to the abbrev of the state
trycnt = 5
for a in links[start:end]:
    if a.text in d and trycnt > 0:
      try:
        URL = "https://www.city-data.com/"+ a['href']
        time.sleep(1.5)
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")
        description = soup.find("div", class_="well")
        desc = description.find_all("p")
        t = ''
        for i in range(len(desc)):
            t += desc[i].text
        descs.write(t+'\n')
      except ConnectionError as ex:
        if trycnt <= 0: 
          print("Failed to retrieve: " + URL + "\n" + str(ex))  # done retrying
        else: 
           trycnt -= 1  # retry
        time.sleep(0.5)  # wait 1/2 second then retry

descs.close()