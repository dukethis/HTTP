#!/usr/bin/python3
# coding: utf-8

#///////////
# IMPORTS /
#/////////

# BUILT IN PYTHON MODULES
import re,sys,json,time
from argparse import ArgumentParser

# TO AVOID BROKEN PIPES
from signal import signal, SIGPIPE, SIG_DFL


# THIRD PARTY PYTHON MODULES
try:
    import urllib3,certifi
    from bs4 import BeautifulSoup
except Exception as e:
    # COURTESY SIGNALING
    print(e)
    print("Python is missing ressources. Try $ sudo pip3 install certifi urllib3")
    sys.exit(1)


#//////////////
# PARAMETERS /
#////////////

VERSION = "0.28"

#////////////////////////////////////////////////
# Request() CLASS OVERLOAD urllib3.PoolManager /
#//////////////////////////////////////////////
class Request(urllib3.PoolManager):

    """ Please refer to help(urllib3.PoolManager) for more details """
    
    def __init__(self, url=None, default_method="GET", **kargs):
        """ Receive: url (mandatory) and default_method or keyword arguments (optionally) """
        self.headers = {
            "User-Agent"   : f"HTTP.py/{VERSION} ; (source +https://github.com/dukethis/HTTP)",
            "Content-Type" : "application/json"
        }
        if "headers" in kargs.keys():
            self.headers.update( kargs["headers"] )

        urllib3.PoolManager.__init__(
            self,
            cert_reqs = 'CERT_REQUIRED',
            ca_certs  = certifi.where(),
            headers   = self.headers
        )
        self.url      = url
        self.method   = kargs["method"]   if "method"   in kargs.keys() else default_method
        self.redirect = kargs["redirect"] if "redirect" in kargs.keys() else True
        self.timeout  = kargs["timeout"]  if "timeout"  in kargs.keys() else 10
        self.charset  = kargs["charset"]  if "charset"  in kargs.keys() else "UTF-8"
        self.response = None
        self.content  = None

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
            print( e )
        
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
            # If attributes list is set and the tag got it || OR no attributes list (all tags)
            if not attrs or any([tag.get(u) for u in attrs]):
                data.append( tag )
        # Build up JSON        
        output = []
        for tag in data:
            if not tag: continue
            jtag = { "name" : tag.name }
            jtag.update( tag.attrs )
            jtag.update( { "content" : tag.get_text() } )
            output.append( jtag )
        self.content = output
        return json.dumps( output, indent=2 )
    
    def __str__(self):
        """ JSON Datagram """
        if self.response.headers["Content-Type"].count("json") :
            body = json.loads( self.content )
        else:
            body = self.content
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

#/////////////////
# CLI INTERFACE /
#///////////////

if __name__ == '__main__':

    # OPTION / ARGUMENT PARSER: DEFINE MORE IF NEEDED
    op = ArgumentParser(description="HTTP Request command", epilog=f"v{VERSION}")
    op.add_argument(dest="url",nargs="+")
    op.add_argument("-m","--method",   type=str, default="GET")
    op.add_argument("-t","--tags",     type=str, nargs="+")
    op.add_argument("-a","--attrs",    type=str, nargs="+")
    op.add_argument("-H","--headers",  type=str, nargs="+")
    op.add_argument("-d","--data",     type=str, nargs="*")
    op.add_argument("-r","--raw",      action="store_true")

    args = op.parse_args()
    bot = Request( charset="UTF-8" )
    
    signal(SIGPIPE,SIG_DFL)
    
    # EASY NOTATION: HTTP METHOD IS CATCHED AND REMOVED FROM URL LIST
    body_data = {}
    urls  = []
    for url in args.url:
        if url in ["HEAD","OPTIONS","GET","POST","PUT","DELETE"]:
            args.method = url
        elif url.count("=") and not url.startswith("http"):
            k,v = url.split("=")[0],"=".join(url.split("=")[1:])
            body_data.update({k:v})
        else:
            urls.append( url )

    # HEADERS CONTRUCTION
    headers = {}
    if args.headers:
        for kv in args.headers:
            if not kv.count(":"):
                print(f"Warning: header {kv} not recognized")
                continue
            kv = kv.split(":")
            k,v = kv[0], ':'.join(kv[1:])
            headers.update({k:v})

    # IS PAYLOAD
    if args.data:
        if "Content-Type" in headers.keys() and headers["Content-Type"].count("json"):
            try:
                body_data = json.loads(args.data)
            except:
                ## RCST JSON FROM ARGS
                print( args.data )
                for kv in [ x.split("=") if x.count('=') else x.split(":") for x in args.data ]:
                    print(kv)
                    if type(kv)==list and len(kv)==2:
                        k,v = kv
                        body_data.update({k:v})
        else:
            headers.update({"Content-Type":"application/x-www-urlencoded"})
            urls = [ url+"?"+"&".join(args.data) for url in urls ]

    # FOR EACH GIVEN URLS
    for url in urls:
        bot.get( url     = url,
                 method  = args.method,
                 headers = headers,
                 body    = body_data)
        # TAGS/ATTRS PARSING
        if args.tags:
            bot.find_all( args.tags, args.attrs )
        # RESPONSE ONLY ('RAW')
        if args.raw:
            print( bot.content )
        else:
            print( bot )
