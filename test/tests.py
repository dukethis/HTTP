#!/usr/bin/python3
# coding: utf-8

#///////////
# IMPORTS /
#/////////

import HTTP,time,json,urllib3

def test_import():
    import HTTP

def test_init():
    bot = HTTP.Request()
    assert type(bot) == HTTP.Request

def test_headers_type():
    bot = HTTP.Request()
    bot.get( url="https://fr.wikipedia.org", method="HEAD" )
    assert type( bot.headers ) == dict


