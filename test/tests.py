#!/usr/bin/python3
# coding: utf-8

#///////////
# IMPORTS /
#/////////

import time,json,urllib3
import HTTP.objects

def test_import():
    import HTTP.objects
    
def test_init():
    bot = HTTP.objects.Request()
    assert type(bot) == HTTP.objects.Request

def test_head_headers_type():
    bot = HTTP.objects.Request()
    bot.get( url="https://fr.wikipedia.org", method="HEAD" )
    assert type( bot.headers ) == dict

def test_get_headers_type():
    bot = HTTP.objects.Request()
    bot.get( url="https://fr.wikipedia.org", method="GET" )
    assert type( bot.headers ) == dict

def test_get_content_type():
    bot = HTTP.objects.Request()
    bot.get( url="https://httpbin.org/get", method="GET", headers={"Content-Type":"application/json"} )
    assert "Content-Type" in bot.headers.keys()
    assert bot.headers["Content-Type"] == "application/json"

def test_get_response_type():
    bot  = HTTP.objects.Request()
    bot.get( url="https://httpbin.org/get", method="GET", headers={"Content-Type":"application/json"} )
    data = bot.content
    data = json.loads(data)
    assert type(data) == dict


