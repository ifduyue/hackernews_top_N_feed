#!/usr/bin/env python
#-*- coding: utf8 -*-

import os
import sys
import time
import logging
import urlfetch
import feedparser
from mako.template import Template
try:
    import simplejson as json
except ImportError:
    import json

def writeto(path, data):
    fh = open(path, 'w')
    fh.write(data)
    fh.close()
    
def readfrom(path):
    fh = open(path, 'r')
    data = fh.read()
    fh.close()
    return data
    
def dumpto(path, obj):
    with open(path, 'wb') as f:
        json.dump(obj, f)
    
def loadfrom(path):
    f = None
    obj = None
    try:
        f = open(path, 'rb')
        obj = json.load(f)
    except:
        pass
    finally:
        f and f.close()
    return obj

def get_path(dirname=None, filename=None):
    f = os.path.dirname(os.path.abspath(__file__))
    if dirname is not None:
        f = os.path.join(f, dirname)
        if not os.path.isdir(f):
            os.makedirs(f)
    if filename is not None:
        f = os.path.join(f, filename)
    return f

def load_last_entries(num):
    filename = 'last_entries.%d' % num
    return loadfrom(get_path('data', filename))
    
def save_last_entries(obj, num):
    filename = 'last_entries.%d' % num
    dumpto(get_path('data', filename), obj)

def mb_code(string, coding="utf-8"):
    if isinstance(string, unicode):
        return string.encode(coding)
    for c in ('utf-8', 'gb2312', 'gbk', 'gb18030', 'big5'):
        try:
            return string.decode(c).encode(coding)
        except:
            pass
    return string

def log(msg, *args): 
    def init():
        logger = logging.getLogger('wet')
        handler = logging.FileHandler(get_path('data', 'log'))
        formatter = logging.Formatter('[%(asctime)s] %(message)s', '%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        log.logger = logger
        return logger

    logger = getattr(log, 'logger', None)
    if logger is None:
        logger = init()
    
    logger.debug(msg, *args)

def get_rss_entries(url):
    try:
        log('fetching %s', url)
        r = urlfetch.get(url, timeout=5)
        log('%d bytes fetched', len(r.body))
        
        log('parsing feed content')
        d = feedparser.parse(r.body)
        log('parsing OK')
    except Exception, e:
        log('[error] get_rss_entries: %s', str(e))
        return []
        
    entries = []
    for e in d.entries:
        title = mb_code(e.title)
        href = mb_code(e.links[0]['href'])
        comments = mb_code(e['comments'])

        entry = {
            'title': title, 
            'url': href,
            'comments': comments
        }
    
        entries.append(entry)

    return entries

def write_rss_file(entries, num):
    f = get_path('rss', 'top_%d.rss' % num)
    template = get_path(filename='rss.mako')
    template = Template(filename=template)
    content = template.render(
        entries = entries,
        title = 'HackerNews Top %s Feed' % num,
        url = 'http://hackernews.lyxint.com/',
        description = 'HackerNews Top %s Feed, for your convenience' % num,
        generator = 'https://github.com/lyxint/hackernews_top_N_feed',
    )
    writeto(f, content)

def run():
    log('start.')
    
    url = 'http://news.ycombinator.com/rss'
    all_entries = get_rss_entries(url)
    
    for num in (1, 3, 5, 10, 15, 20, 25, 30, 1024):
        log('processing top_%d', num)
        last_entries = load_last_entries(num) or []
        entries = []
        
        for entry in all_entries[:num]:
            if entry not in last_entries:
                log('[new] %s(%s) added to %s.rss', entry['title'], entry['url'], num)
                entries.append(entry)
            
        entries.extend(last_entries)
        entries = entries[:1024]
        
        save_last_entries(entries, num)
        write_rss_file(entries, num)
        
    log('end.')

if __name__ == '__main__':
    run()
