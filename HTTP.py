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
signal(SIGPIPE,SIG_DFL)

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

VERSION   = "0.15"
USERAGENT = f"HTTP.py/{VERSION} ; (source +https://github.com/dukethis/HTTP)"
METHOD    = "GET"
REDIRECT  = 1
TIMEOUT   = 5
CHARSET   = "utf-8"

#////////////////////////////////////////////////
# Request() CLASS OVERLOAD urllib3.PoolManager /
#//////////////////////////////////////////////
class Request(urllib3.PoolManager):
    """ Please refer help(urllib3.PoolManager) for more details """
    def __init__(self,url=None,**kargs):
        HEADERS = {
            "User-Agent"   : USERAGENT,
            "Content-Type" : "application/json"
        }
        HEADERS = HEADERS.update(kargs["headers"]) if "headers" in kargs.keys() else HEADERS

        urllib3.PoolManager.__init__(
            self,
            cert_reqs = 'CERT_REQUIRED',
            ca_certs  = certifi.where(),
            headers   = HEADERS
        )
        self.url      = url
        self.method   = kargs["method"]   if "method"   in kargs.keys() else METHOD
        self.redirect = kargs["redirect"] if "redirect" in kargs.keys() else REDIRECT
        self.timeout  = kargs["timeout"]  if "timeout"  in kargs.keys() else TIMEOUT
        self.charset  = kargs["charset"]  if "charset"  in kargs.keys() else CHARSET
        self.response = None
        self.content  = None

    def get(self,url=None,method=None,tag=None,body=None,parse=0,attr=None,headers={},verbose=0):
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
                headers  = headers
        )
        else:
            body = json.dumps(body)
            self.response = self.request_encode_body(
                self.method,
                self.url,
                timeout  = self.timeout,
                redirect = self.redirect,
                headers  = headers,
                body     = body)
        tx = time.time()-tx

        self.response.time = round(tx,5)

        # CONTENT TYPE RETRIEVAL
        data = self.response.data
        
        try:
            JSON = json.loads( data )
            data = json.dumps( JSON, indent=2)
        except Exception as e:
            data = data.decode('utf-8')
        
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
        this = {
            "request": {
                "url"     : self.url,
                "method"  : self.method,
                "charset" : self.charset,
                "headers" : self.headers
            },
            "response": {
                "status"  : self.response.status,
                "time"    : self.response.time,
                "headers" : dict(self.response.headers),
                "body"    : self.content
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
    op.add_argument("-H","--headers",  type=str, nargs="*")
    op.add_argument("-d","--data",     type=str, nargs="*")
    op.add_argument("-p","--parse",    action="store_true")
    op.add_argument("-r","--raw",      action="store_true")

    args = op.parse_args()
    bot = Request( charset="UTF-8" )

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
        for k,v in [ x.split(":") for x in args.headers ]:
            headers.update({k:v})

    # IS PAYLOAD
    if args.data:
        if "Content-Type" in headers.keys() and headers["Content-Type"].count("json"):
            try:
                body_data = json.loads(args.data)
            except:
                ## RCST JSON FROM ARGS
                for k,v in [ x.split(":") for x in args.data ]:
                    body_data.update({k:v})
        else:
            headers.update({"Content-Type":"application/x-www-urlencoded"})
            urls = [ url+"?"+"&".join(args.data) for url in urls ]

    # FOR EACH GIVEN URLS
    for url in urls:
        request = bot.get( url     = url,
                           method  = args.method,
                           headers = headers,
                           body    = body_data)
        # TAGS/ATTRS PARSING
        if args.tags:
            bot.find_all( args.tags, args.attrs )
        # RESPONSE ONLY ('RAW')
        if args.raw:
            print( json.dumps( bot.content, indent=2 ) )
        else:
            print( bot )
