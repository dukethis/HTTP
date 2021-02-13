#!/usr/bin/python3
# coding: utf-8

#///////////
# IMPORTS /
#/////////

import os,time,json,urllib3
import HTTP.objects, HTTP.cli

def test_import():
    import HTTP.objects, HTTP.cli
    
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
    data = json.loads(bot.content)
    assert type(data) == dict

def test_post_response_type():
    bot  = HTTP.objects.Request()
    bot.get( url="https://httpbin.org/post", method="POST", headers={"Content-Type":"application/json"} )
    data = json.loads(bot.content)
    assert type(data) == dict

def test_post_01():
    bot  = HTTP.objects.Request()
    bot.get( url="https://httpbin.org/post",
             method="POST",
             headers={"Content-Type":"application/json"})
    data = json.loads(bot.content)
    assert data["url"] == "https://httpbin.org/post"

def test_post_02():
    bot  = HTTP.objects.Request()
    bot.get( url="https://httpbin.org/post",
             method="POST",
             headers={"Content-Type":"application/json"},
             body={"test":"success"} )
    data = json.loads(bot.content)
    assert data["json"]["test"] == "success"


def test_cli_sequence_01():
    args = "GET httpbin.org/get"
    code = os.system(f"HTTP {args}")
    assert code == 0

def test_cli_sequence_02():
    args = "GET httpbin.org/get -r"
    code = os.system(f"HTTP {args}")
    assert code == 0

def test_cli_sequence_03():
    args = "GET httpbin.org/get -t a -r"
    code = os.system(f"HTTP {args}")
    assert code == 0

def test_cli_sequence_04():
    args = "GET httpbin.org/get -t a -a href -r"
    code = os.system(f"HTTP {args}")
    assert code == 0

def test_cli_sequence_05():
    args = "POST httpbin.org/post -d test=toto -r"
    code = os.system(f"HTTP {args}")
    assert code == 0