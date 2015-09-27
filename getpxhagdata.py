import requests, json
import re
from string import printable

# ******** Module globals ******** 
_finBaseUrl = "http://pxnet2.stat.fi/PXWeb/api/v1/en"
_hagBaseUrl = "http://px.hagstofa.is/pxis/api/v1/is"
_headerjson = {'Content-Type':'application/json; charset=utf-8'}
_headers = { 'Content-Type': 'application/json',
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.8,is;q=0.6'
    }
lson = { "query": [ { "code": "Þjóðerni", "selection": { "filter": "item", "values": [ "0", ] } }, { "code": "Ár", "selection": { "filter": "item", "values": [ "0", ] } }, { "code": "Landsvæði", "selection": { "filter": "item", "values": [ "0", ] } }, { "code": "Mánuður", "selection": { "filter": "item", "values": [ "0", ] } } ], "response": { "format": "json" } } 

def main():
  getpxjson_hotelnights()

def getpxjson_hotelnights():
  #Specific url for data on hotel nights 1997-2015
  hotelNightsUrl = "/Atvinnuvegir/ferdathjonusta/Gisting/GiHotGist/SAM01102.px"
  url = _hagBaseUrl+hotelNightsUrl
  jsonfile = 'px.hotelnights.json'
  #***********
  #404 error caused by the payload being read from file, hardcoding works
  #payload = readjsonfromfile(jsonfile).rstrip()
  #print(repr(payload))
  #payload = payload.replace('\n','').replace(' ','').replace('\r','')
  #print(repr(payload))
  #***********
  r = requests.post(url,json=lson)
  #out = re.sub("[^{}]+".format(printable), "", r.text)
  #Remove '\ufeff' char at front of returned data string
  out = r.text[1:]
  query = json.loads(out)
  data = query['data']
  print(data[0]['values'])

  #finnish test code
  """kuolUrl = "/StatFin/vrm/kuol/010_kuol_tau_101.px"
  turl = _finBaseUrl+kuolUrl
  jf = 'pxfin.kuol.json'
  dj = readjsonfromfile(jf)
  tr = requests.post(turl,json=dj,headers=_headerjson)"""

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
