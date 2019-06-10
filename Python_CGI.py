#!/usr/bin/python
import cgi

print "Content-type:text/html\r\n\r\n"
print '<html>'
print '<head><title>To Check Page content</title></head>'
print '<body>'

print '<form method="post" action="concheck.cgi">'
print '<p>Application: <input list="App" name="Application"><datalist id="App"><option value="APP"></datalist></p>'
print '<p>Environment: <input list="Env" name="Environment"><datalist id="Env"><option value="Stage"><option value="ProdBatch1"><option value="ProdBatch2"><option value="Dev01"><option value="Dev02"><option value="QA01"><option value="QA02"></datalist></p>'
print '<p>Check : <input type="text" name="content" size=75 placeholder="Enter Content/Service URL E.g. - /services/systemcheck"/></p>'
print '<input type="submit" value="Submit" />'
print '</form>'

serlist = { "ProdBatch1": ["server1:8080","server2:8080"],
"ProdBatch2" : ["server1:8080","server2:8080"],
"Stage" :["server1:8080","server2:8080"],
"Dev01" : ["server1:8080","server2:8080"],
"Dev02" :["server1:8080","server2:8080"],
"QA01" :["server1:8080","server2:8080"],
"QA02" :["server1:8080","server2:8080"] }

form = cgi.FieldStorage()

#convert to dictionary
def cgiFieldStorageToDict(fieldStorage):
   params = {}
   for key in fieldStorage.keys(  ):
      params[key] = fieldStorage[key].value
   return params

keys = cgiFieldStorageToDict(form)

#Server List
def assignservers(app,env):
    out = app+env
    return out

serverlist = assignservers( keys['Application'], keys['Environment'])
servers = serlist[serverlist]

#iframe
for server in servers:
   url = "http://"+server+keys['content']
   print '<p><A href="'+url+'">'+url+'</A></p>'
   print '<iframe src="'+url+'" height="200" width="80%"></iframe>'


print '</body>'
print '</html>'
