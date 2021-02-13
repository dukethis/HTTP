#!/usr/bin/python3
# coding: utf-8
# OBJECTS

#///////////
# IMPORTS /
#/////////

# BUILT IN PYTHON MODULES
import re,sys,json,time,urllib3

# MODULE IMPORT
from params import *

# THIRD PARTY PYTHON MODULES
try:
    import certifi
    from bs4 import BeautifulSoup
except Exception as e:
    # COURTESY SIGNALING
    print( e )
    print("Python is missing ressources. You need to $ sudo pip3 install certifi urllib3")
    sys.exit(1)

#////////////////////////////////////////////////
# Request() CLASS OVERLOAD urllib3.PoolManager /
#//////////////////////////////////////////////
class Request(urllib3.PoolManager):

    """ Please refer to help(urllib3.PoolManager) for more details """
    
    def __init__(self, **kargs):
        """ Receive: keyword arguments (optionally) """
        # DEFAULT ATTRIBUTES
        self.url      = None
        self.method   = "HEAD"
        self.redirect = True
        self.timeout  = 10
        self.charset  = "UTF-8"
        self.response = None
        self.content  = None
        self.headers  = {
            "User-Agent"   : f"HTTP.py/{VERSION} ; (source +https://github.com/dukethis/HTTP)",
            "Content-Type" : "application/json"
        }
        
        self.__dict__.update( kargs )

        urllib3.PoolManager.__init__( self,
                                      cert_reqs = 'CERT_REQUIRED',
                                      ca_certs  = certifi.where(),
                                      headers   = self.headers
        )
        
        

    def get(self, url=None, method=None, body=None, headers={}):
        """ Main request method """
        # METHOD/URL OVERWRITING
        self.method = method if method != None else self.method
        self.url    = url    if    url != None else self.url

        # REQUEST HEADERS
        self.headers.update ( headers )

        # ACTUAL REQUEST
        tx = time.time()
        if body in [{},None]:
            self.response = self.request_encode_url(
                self.method,
                self.url,
                timeout  = self.timeout,
                redirect = self.redirect,
                headers  = self.headers
        )
        else:
            body = json.dumps(body)
            self.response = self.request_encode_body(
                self.method,
                self.url,
                timeout  = self.timeout,
                redirect = self.redirect,
                headers  = self.headers,
                body     = body)
            
        tx = time.time()-tx

        self.response.time = round(tx,5)
        
        # CONTENT RETRIEVAL
        data = self.response.data.decode('utf-8')
        try:
            JSON = json.loads( data )
            data = json.dumps( JSON, indent=2)
        except Exception as e:
            #print( e )
            pass
        
        self.content = data

        return self.content
    
    def find_all(self, tags, attrs=[]):
        """ Find all tags (list) with eventually a set of attribute keys to match (list) """
        # Kick in the try/except directly
        try:
            html = BeautifulSoup( self.content, 'lxml')          
        except Exception as e:
            print(e)
            return
        # Gather tags list
        data = []
        for tag in html.find_all( tags ):
            if attrs and len(attrs)>0 and any([tag.get(u) for u in attrs if tag.get(u)]):
                data.append( {"name":tag.name, "attrs":{ u:tag.get(u) for u in attrs if tag.get(u)} } )
            else:
                data.append( tag )
        # Build up JSON        
        output = []
        for tag in data:
            if not tag: continue
            if type(tag)==dict:
                jtag = { "name" : tag["name"] }
                jtag.update( tag["attrs"] )
            else:
                jtag = { "name" : tag.name }
                jtag.update( tag.attrs )
            output.append( jtag )
        self.content = output
        return json.dumps( output, indent=2 )
    
    def __str__(self):
        """ JSON Datagram """
        if "Content-Type" in self.response.headers.keys() and self.response.headers["Content-Type"].count("json") :
            body = json.loads( self.content ) if self.content else None
        else:
            body = self.content #json.dumps( self.content, indent=2) 
        this = {
            "request": {
                "url"     : self.url,
                "method"  : self.method,
                "charset" : self.charset,
                "headers" : dict(self.headers)
            },
            "response": {
                "status"  : self.response.status,
                "time"    : self.response.time,
                "headers" : dict(self.response.headers),
                "body"    : body
            }
        }
        return json.dumps( this, indent=2 )
