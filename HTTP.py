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
        """ Request method:
            - url
            - method    (HTTP)
            - headers   (HTTP)
            - tag       (HTML/RSS)
            - attr      (HTML)
            - body      (PAYLOAD for POST,PUT)
            - parse     (PRINT TEXT CONTENT)
            - verbose   (PRINT ALL REQUEST)
        """
        # METHOD/URL OVERWRITING
        self.method = method if method != None else self.method
        self.url    = url    if url != None    else self.url

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

        self.response.time = round(tx,7)

        # CONTENT TYPE RETRIEVAL
        content_type = headers["Content-Type"] if "Content-Type" in headers else None
        charset = re.findall("charset=[^;]+",content_type) if content_type else self.charset
        if type(charset)==list and len(charset)>0:
            self.charset = charset[0].split("=")[1]
        else:
            self.charset = charset
        # IMAGE DOWNLOAD
        if content_type and content_type.count("image/"):
            ext = content_type.split("image/")[-1]
            ext = ext.split(";")[0]
            if ext in ["exe","sh","dll"]: return "Skip special extension "+ext
            filename = self.response.headers["Content-Disposition"].split(";")[-1].replace("filename=","").strip()
            with open(filename,"wb") as fd:
                fd.write(self.response.data)
            return "Saved image: %s"%(filename)

        content = None
        # CONTENT DECODING THE ASS
        try:
            content = self.response.data.decode(self.charset)
        except Exception as e:
            self.charset = CHARSET

        # CONTENT DECODING THE ASS - FINAL
        if not self.charset:
            for charset in ["UTF-8","ISO-8859-1","Latin-1"]:
                try:
                    content = self.response.data.decode(charset)
                    self.charset = charset
                except Exception as e:
                    self.charset = CHARSET

        # HTML PARSE FOR HTML/RSS CONTENT
        if not content_type or any([ content_type.count(x) for x in ["text/html","rss","xml"]]):
            data = BeautifulSoup(content,"lxml") if content else None
            if data and tag:
                content = []
                for xtag in tag:
                    content.append( data.find_all(xtag) )
                ncontent = []
                for u in zip(*content):
                    ncontent.extend( u )
                content = ncontent
                # OPTION -a: SEARCH FOR A SPECIFIC TAG ATTRIBUTE
                if attr:
                    # USING A KEY=VALUE SYNTAX TO TARGET A SPECIFIC ATTRIBUTE'S VALUE
                    if attr.count("="):
                        attr,val = attr.split("=")
                        content = [ str(x) for x in content if x.get(attr) and x.get(attr)==val ]
                    # ELSE RETRIEVE ALL TAGS WITH ATTRIBUTE
                    else:
                        content = [ str(x.get(attr)) for x in content if x.get(attr) ]
                # ELSE RETRIEVE ALL TAGS
                else:
                    content = [ str(x) for x in content ]
            # DECODING IS COMING
            else: # TRY A STRING TYPE OR ELSE JSON
                content = content.get_text() if content and type(content)!=str else json.dumps(content, indent=2)
        # JSON IS DETECTED
        elif content_type.count("json"):
            self.content = json.loads(content) if content else None
            return self
        # PLAIN TEXT CONTENT
        elif content_type.count("text/plain"):
            content = self.response.data.decode(self.charset)
            self.content = content.strip()
            return self
        self.content = json.loads(content) if type(content)==str else content
        return self

    def get_headers(self):
        return json.dumps( self.headers, indent=4 )

    def get_response_headers(self):
        return json.dumps( dict(self.response.headers), indent=4 )

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

    def write_rssfile(self,url):
        with open(self.rssfile,"a") as fd:
            fd.write("%s\n"%url)

    def catch_rss(self):
        if "Content-Type" in self.response.headers.keys() and any(self.response.headers["Content-Type"].count(x) for x in [
            "xml","rss"
        ]):
            self.write_rssfile(self.url)
            return True
        else:
            html = BeautifulSoup(self.response.data.decode(self.charset),"lxml")
            for link in html.find_all('link'):
                if link.get("type") == "application/rss+xml":
                    self.write_rssfile(self.url+"/"+link.get("href"))
                    return True
        return False

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
    req = Request( charset="utf-8" )

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
        request = req.get( url     = url,
                           method  = args.method,
                           headers = headers,
                           tag     = args.tag,
                           parse   = args.parse,
                           attr    = args.attribute,
                           body    = body_data)

        if args.raw:
            print( request.response.data.decode('utf-8') )
        else:
            print( request )
