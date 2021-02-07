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

def test_headers_type():
    bot = HTTP.objects.Request()
    bot.get( url="https://fr.wikipedia.org", method="HEAD" )
    assert type( bot.headers ) == dict


