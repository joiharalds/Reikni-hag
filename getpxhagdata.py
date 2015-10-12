#-*- coding: utf-8 -*-
import argparse
import requests, json, re
import csv
from string import printable

"""
**************** Notes ******************
Structure of query is immutable, following is the correct order of variables.

There is misrepancy in the icelandic and english version of data for overnight
  stays at hotels from 1997-2015.
  See [iceurl]/SAM01102.px and [engurl]/SAM01103.px.
*****************************************
***************** TODO ******************
Write a function that constructs a query string from specified code:[values] pairs
  handling missing code IDs approprietly.
  def make_pxjsonquery(valueselector,metadata):
*****************************************
"""

# ******** Module globals ******** 
_icebaseurl = "http://px.hagstofa.is/pxis/api/v1/is"
_engbaseurl = "http://px.hagstofa.is/pxen/api/v1/en"
#Hardcoded json payload and url for hotel nights
_icehotelpayload = { "query": [ { "code": "Ríkisfang", "selection": { "filter": "all", "values": [ "*", ] } }, { "code": "Ár", "selection": { "filter": "item", "values": [ "0","1" ] } }, { "code": "Landsvæði", "selection": { "filter": "all", "values": [ "*", ] } }, { "code": "Mánuður", "selection": { "filter": "all", "values": [ "*", ] } } ], "response": { "format": "json" } } 
_enghotelpayload = { "query": [ { "code": "Citizenship", "selection": { "filter": "all", "values": [ "*", ] } }, { "code": "Year", "selection": { "filter": "item", "values": [ "0","1" ] } }, { "code": "Region", "selection": { "filter": "all", "values": [ "*", ] } }, { "code": "Month", "selection": { "filter": "all", "values": [ "*", ] } } ], "response": { "format": "json" } } 
_icehotelurl = "/Atvinnuvegir/ferdathjonusta/gisting/GiHotGist/SAM01201.px"
_enghotelurl = "/Atvinnuvegir/ferdathjonusta/gisting/GiHotGist/SAM01201.px"
_icehotelfname = "pxice.hotelnights.csv"
_enghotelfname = "pxeng.hotelnights.csv"
_trans = str.maketrans('ÁÐÉÍÓÚÝÞÆÖáðéíóúýþæö ','ADEIOUYTAOadeiouytao_')

def main(args):
  inEnglish = args.eng
  if inEnglish:
    data,metadata = getpxjson(_engbaseurl,_enghotelurl,_enghotelpayload)
    datatuples = parsepxjson(metadata,data)
    writepxjson_to_csv(datatuples,_enghotelfname)
  else:
    data,metadata = getpxjson(_icebaseurl,_icehotelurl,_icehotelpayload)
    datatuples = parsepxjson(metadata,data)
    writepxjson_to_csv(datatuples,_icehotelfname,westquarter)

def writepxjson_to_csv(data,fname,f=False):
  """
    Desc: Write pxjsondata to csv with header row.

    Use: writepxjson_to_csv(data,fname)
    Before: data is list of tuples, fname is name of csv file to write.
            f (optional) is a data handling function applied to each value in each row.
    After: tuples in data have been written to fname.
  """
  with open(fname, 'w', newline='') as csvfile:
    w = csv.writer(csvfile, delimiter=',',quoting=csv.QUOTE_MINIMAL)
    if not f:
      for tup in data:
        w.writerow(tup)
    else:
      for tup in data:
        w.writerow(tuple(map(f,tup)))

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

def getpxjson(baseurl,suburl,payload):
  """
    Desc: Get pxjsondata from Statstics Iceland on payed hotel nights in Iceland.
      Returns dictonaries containing data and metadata.

    Use: x,y = getpxjson(suburl,payload)
    Before: suburl is relative path to a table on px server.
            payload is request in json format.
    After: x is json data, y is json metadata from table.
  """
  url = baseurl+suburl
  r = requests.post(url,json=payload)
  g = requests.get(url)
  metadata = json.loads(g.text)
  #Remove '\ufeff' char at front of returned data string
  out = r.text[1:]
  query = json.loads(out)
  data = query['data']
  return data,metadata

# ******** HELPER FUNCTIONS *********
def westquarter(x):
  """
    Desc: Handling of specific Iceland geographical values
  """
  if 'Vesturland' in x:
    return 'Vesturland, Vestfirðir'
  else:
    return x

def translator(x):
  return x.translate(_trans)

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
  #Set up command line argument handling
  parser = argparse.ArgumentParser(description='Get data from Statistics Iceland pxweb')
  #Language of data
  parser.add_argument('--eng', action='store_true',help='Get data in English else it defaults to Icelandic')
  args = parser.parse_args()
  main(args)
