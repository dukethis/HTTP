# HTTP.py

A simple HTTP request CLI

Yet another HTTP request tool. This one is derived from the native python **urllib3.PoolManager** (https://urllib3.readthedocs.io/en/latest/reference/urllib3.poolmanager.html).

It provides a set of essential functionalities when requesting on the web.

If you got there searching about a nice HTTP cli tool (but no necessarly python made) : check **curl** and the more recent **http**.

## Personal usage

  - Put this script in a directory which is part of the **PATH** environment variable. 
  - Set the **-x** execution mode on the script : `$ sudo chmod +x HTTP.py`.
  - The script is callable from any other place when you have **PATH** loaded in your environment.

## Help Menu
```
$ HTTP.py -h
usage: HTTP.py [-h] [-m METHOD] [-t TAG [TAG ...]] [-a ATTRIBUTE]
               [-H [HEADER [HEADER ...]]] [-d [DATA [DATA ...]]] [-p] [-r]
               url [url ...]

HTTP Request command

positional arguments:
  url

optional arguments:
  -h, --help            show this help message and exit
  -m METHOD, --method METHOD
  -t TAG [TAG ...], --tag TAG [TAG ...]
  -a ATTRIBUTE, --attribute ATTRIBUTE
  -H [HEADER [HEADER ...]], --header [HEADER [HEADER ...]]
  -d [DATA [DATA ...]], --data [DATA [DATA ...]]
  -p, --parse
  -r, --raw

v0.15
```

First information is that the only required argument is an URL.

## Spirit of this interface

Work on JSON at every level of our request.

For instance, let's do a HEAD request (no body content is returned) : 
```
$ HTTP.py HEAD dukeart.netlib.re
{
  "request": {
    "url": "dukeart.netlib.re",
    "method": "HEAD",
    "charset": "UTF-8",
    "headers": {
      "User-Agent": "HTTP.py/0.15 ; (source +https://github.com/dukethis/HTTP)"
    }
  },
  "response": {
    "status": 200,
    "time": 0.2490139,
    "headers": {
      "Cache-Control": "public, max-age=36000",
      "Content-Length": "0",
      "Content-Security-Police": "upgrade-insecure-requests",
      "Content-Type": "text/html; charset=UTF-8",
      "Referrer-Policy": "no-referrer-when-downgrade",
      "Server": "Caddy",
      "Strict-Transport-Security": "max-age=31536000",
      "X-Content-Type-Options": "nosniff",
      "X-Frame-Options": "sameorigin",
      "X-Robots-Tag": "index,follow,noarchive",
      "X-Xss-Protection": "1;mode=block",
      "Date": "Thu, 28 Jan 2021 08:59:27 GMT"
    },
    "body": ""
  }
}

```

Result is a javascript object notation with :
  - A **request** part mainly composed of metadata (request headers, charset, etc..)
  - A **response** part composed by the response headers and the body content
