#!/usr/bin/python3
# coding: utf-8
# CLI INTERFACE

#///////////
# IMPORTS /
#/////////

# BUILT IN PYTHON MODULES
import re,sys,json,time
from argparse import ArgumentParser

# MODULE IMPORT
from params  import *
from objects import *

# TO AVOID BROKEN PIPES
from signal import signal, SIGPIPE, SIG_DFL

#/////////////////
# CLI INTERFACE /
#///////////////

if __name__ == '__main__':

    # OPTION / ARGUMENT PARSER: DEFINE MORE IF NEEDED
    op = ArgumentParser(description="HTTP Request command", epilog=f"v{VERSION}")
    op.add_argument(dest="url",nargs="+")
    op.add_argument("-m","--method",   type=str)
    op.add_argument("-t","--tags",     type=str, nargs="+")
    op.add_argument("-a","--attrs",    type=str, nargs="+")
    op.add_argument("-H","--headers",  type=str, nargs="+")
    op.add_argument("-d","--data",     type=str, nargs="*")
    op.add_argument("-r","--raw",      action="store_true")

    args = op.parse_args()
    bot  = Request( charset="UTF-8" )
    
    signal(SIGPIPE,SIG_DFL)
    
    # EASY NOTATION: HTTP METHOD IS CATCHED AND REMOVED FROM URL LIST
    body_data = {}
    urls  = []
    for url in args.url:
        if url in ["HEAD","OPTIONS","GET","POST","PUT","DELETE"]:
            args.method = url
        elif url.count("=") and not url.count("?"):
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
                for kv in [ x.split("=") if x.count('=') else x.split(":") for x in args.data ]:
                    if type(kv)==list and len(kv)==2:
                        k,v = kv
                        body_data.update({k:v})
        else:
            headers.update({"Content-Type":"application/x-www-urlencoded"})
            urls = [ url+"?"+"&".join(args.data) for url in urls ]

    urls = [ url if url.startswith('http') else 'https://'+url for url in urls ]
    
    # FOR EACH GIVEN URLS
    for url in urls:
        bot.get( url     = url,
                 method  = args.method,
                 headers = headers,
                 body    = body_data)
        # TAGS/ATTRS PARSING
        if args.tags:
            bot.find_all( args.tags, args.attrs )
        # RESPONSE ONLY ('RAW' CONTENT)
        if args.raw:
            if type(bot.content) == str:
                print( bot.content )
            else:
                print( json.dumps( bot.content, indent=2) )
        else:
            print( bot )
