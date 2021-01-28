#!/usr/bin/python3
# coding: utf-8

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
    # SIGNALING MISSING LIB
    print(e)
    print("Python is missing ressources. Try $ sudo pip3 install certifi urllib3")
    sys.exit(1)



# SCRIPT PARAMETERS
VERSION   = "0.15"
USERAGENT = f"HTTP.py/{VERSION} ; (source +https://github.com/dukethis/HTTP)"
METHOD    = "GET"
REDIRECT  = 1
TIMEOUT   = 5
CHARSET   = "utf-8"

# CLASS INTERFACE / OVERLOOOAD IS COMING
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
        
        if self.response.headers["Content-Type"].count("html"):
            HTML = BeautifulSoup( data, 'lxml')
            self.content = HTML

        return self.content
    
    def __str__(self):
        """ JSON Datagram for the verbose mode """
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

# CLI INTERFACE
if __name__ == '__main__':

    # OPTION / ARGUMENT PARSER: DEFINE MORE IF NEEDED
    op = ArgumentParser(description="HTTP Request command", epilog=f"v{VERSION}")
    op.add_argument(dest="url",nargs="+")
    op.add_argument("-m","--method",   type=str, default="GET")
    op.add_argument("-t","--tag",      type=str, nargs="+")
    op.add_argument("-a","--attribute",type=str)
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

    # TEST PAYLOAD PRESENCE
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

    # ALL IN ONE
    for url in urls:
        request = bot.get( url     = url,
                           method  = args.method,
                           headers = headers,
                           body    = body_data)
        # TODO TAGS / ATTRIBUTES
        if args.raw:
            print( request.response.data.decode('utf-8') )
        else:
            print( request )
