#-*- coding: utf-8 -*-
import requests, json, re
import csv
from string import printable

"""
**************** Notes ******************
Structure of query is immutable, following is the correct order of variables.

*****************************************
"""

# ******** Module globals ******** 
_baseurl = "http://px.hagstofa.is/pxis/api/v1/is"
#Hardcoded json payload and url for hotel nights
_hotelpayload = { "query": [ { "code": "Þjóðerni", "selection": { "filter": "all", "values": [ "*", ] } }, { "code": "Ár", "selection": { "filter": "item", "values": [ "0","1" ] } }, { "code": "Landsvæði", "selection": { "filter": "all", "values": [ "*", ] } }, { "code": "Mánuður", "selection": { "filter": "all", "values": [ "*", ] } } ], "response": { "format": "json" } } 
_hotelurl = "/Atvinnuvegir/ferdathjonusta/Gisting/GiHotGist/SAM01102.px"
_hotelfname = "px.hotelnights.csv"
_trans = str.maketrans('ÁÐÉÍÓÚÝÞÆÖáðéíóúýþæö ','ADEIOUYTAOadeiouytao_')

def main():
  data,metadata = getpxjson(_hotelurl,_hotelpayload)
  datatuples = parsepxjson(metadata,data)
  writepxjson_to_csv(datatuples,_hotelfname)

def writepxjson_to_csv(data,fname,noIceChars=False):
  """
    Desc: Write pxjsondata to csv with header row.

    Use: writepxjson_to_csv(data,fname,noIceChars=0)
    Before: data is list of tuples, fname is name of csv file to write.
            if noIceChars is True then all icelandic characters and ' ' are
              translated according to module transtable.
    After: tuples in data have been written to fname.
  """
  with open(fname, 'w', newline='') as csvfile:
    w = csv.writer(csvfile, delimiter=',',quoting=csv.QUOTE_MINIMAL)
    if not noIceChars:
      for tup in data:
        w.writerow(tup)
    else:
      translator = lambda x: x.translate(_trans)
      for tup in data:
        w.writerow(tuple(map(translator,tup)))

def parsepxjson(metadata,data):
  """
    Desc: Create data n-tuples from pxjsondata. Returns list of n-tuples, first tuple
      containing dataheaders.

    Use: x = parsepxjson(metadata,data)
    Before: metadata, data are json strings from px server.
    After: x is a list of tuples containing data, first tuple is dataheaders.
  """
  metavars = metadata['variables']
  headers = list()
  datatuples = list()
  #Get data headers
  for var in metavars:
    headers.append(var['text'])
  for i,val in enumerate(data[0]['values']):
    #Generic name for headers of cols containing values
    headers.append('Value'+str(i))
  datatuples.append(tuple(headers))
  #Get data values
  for keyval in data:
    t = list()
    for i,key in enumerate(keyval['key']):
      t.append(metavars[i]['valueTexts'][int(key)])
    #Does any pxdata contain multiple values for a single key?
    for val in keyval['values']:
      t.append(val)
    datatuples.append(tuple(t))
  return datatuples

def getpxjson(suburl,payload):
  """
    Desc: Get pxjsondata from Statstics Iceland on payed hotel nights in Iceland.
      Returns dictonaries containing data and metadata.

    Use: x,y = getpxjson(suburl,payload)
    Before: suburl is relative path to a table on px server.
            payload is request in json format.
    After: x is json data, y is json metadata from table.
  """
  url = _baseurl+suburl
  r = requests.post(url,json=payload)
  g = requests.get(url)
  metadata = json.loads(g.text)
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
    Before: fname is path/to/file/filename.
    After: x is json string.
  """
  with open(fname) as f:
    return f.read()

#-----------------------------------------------
if __name__ == "__main__":
  main()
