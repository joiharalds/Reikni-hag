#-*- coding: utf-8 -*-
import requests, json
import re
from string import printable

# ******** Module globals ******** 
_hagBaseUrl = "http://px.hagstofa.is/pxis/api/v1/is"
#Note: Structure of query is immutable, following is the correct order of variables
lson = { "query": [ { "code": "Þjóðerni", "selection": { "filter": "item", "values": [ "0", ] } }, { "code": "Ár", "selection": { "filter": "item", "values": [ "0", ] } }, { "code": "Landsvæði", "selection": { "filter": "item", "values": [ "0", ] } }, { "code": "Mánuður", "selection": { "filter": "item", "values": [ "0", ] } } ], "response": { "format": "json" } } 
allson = { "query": [ { "code": "Þjóðerni", "selection": { "filter": "all", "values": [ "*", ] } }, { "code": "Ár", "selection": { "filter": "item", "values": [ "0","1" ] } }, { "code": "Landsvæði", "selection": { "filter": "all", "values": [ "*", ] } }, { "code": "Mánuður", "selection": { "filter": "all", "values": [ "*", ] } } ], "response": { "format": "json" } } 

def main():
  data,metadata = getpxjson_hotelnights()
  datatuples = parsepxjson_hotelnights(metadata,data)

def parsepxjson_hotelnights(metadata,data):
  """
    Desc: Create data n-tuples from pxdata. Returns list of n-tuples.
  """
  metavars = metadata['variables']
  headers = list()
  datatuples = list()
  #Get data headers
  for var in metavars:
    headers.append(var['text'])
  headers.append('Gildi')
  datatuples.append(tuple(headers))
  #Get data values
  for keyval in data:
    t = list()
    for i,key in enumerate(keyval['key']):
      t.append(metavars[i]['valueTexts'][int(key)])
    #Does any pxdata contain multiple values for a single key?
    t.append(keyval['values'][0])
    datatuples.append(tuple(t))
  return datatuples

#def makerequest_hotelnights():

def getpxjson_hotelnights():
  #Specific url for data on hotel nights 1997-2015
  hotelNightsUrl = "/Atvinnuvegir/ferdathjonusta/Gisting/GiHotGist/SAM01102.px"
  url = _hagBaseUrl+hotelNightsUrl
  jsonfile = 'px.hotelnights.json'
  #***********
  #404 error caused by the payload being read from file, hardcoding works
  #payload = readjsonfromfile(jsonfile).strip()
  #print(repr(payload))
  #payload = payload.replace('\n','').replace(' ','').replace('\r','')
  #print(repr(payload))
  #***********
  r = requests.post(url,json=allson)
  g = requests.get(url)
  metadata = json.loads(g.text)
  #out = re.sub("[^{}]+".format(printable), "", r.text)
  #Remove '\ufeff' char at front of returned data string
  out = r.text[1:]
  query = json.loads(out)
  data = query['data']
  return data,metadata

# ******** HELPER FUNCTIONS *********
def readjsonfromfile(fname):
  """
    Desc: Read a file containing a single json string.

    Use: x = readjsonfromfile(fname)
    Before: fname is path/to/file/filename
    After: x is json string
  """
  with open(fname) as f:
    return f.read()

#-----------------------------------------------
if __name__ == "__main__":
  main()
