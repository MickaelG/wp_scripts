#!/usr/bin/python3

import re, sys
import time, threading
import MwApiInterface

from concurrent.futures import ThreadPoolExecutor

import logging

api = MwApiInterface.MwApiInterface('http://fr.wikipedia.org/w/api.php')



def get_article():
  data = api.raw_query_request( {'generator':'random', 'action':'query', 'prop':'categories', 'cllimit':500, 'clshow':'!hidden', 'grnnamespace':1} )
  (page_id, page_data) = data['query']['pages'].popitem()
  title = page_data['title']
  art_title = re.sub("^Discussion:", "", title)
  try:
    categories = [ categ['title'] for categ in page_data['categories'] ]
  except KeyError:
    categories = []

  imp = 0;
  for categ in categories:
    if re.search("d'importance", categ):
      if re.search("inconnue$", categ):
        pass
      elif re.search("faible$", categ):
        imp += 1
      elif re.search("moyenne$", categ):
        imp += 10
      elif re.search("élevée$", categ):
        imp += 100
      elif re.search("maximum$", categ):
        imp += 1000
      else:
        raise Exception('Unknown importance: {}'.format(categ))

  return (art_title, imp)


def get_a_page(debug=False):
  ts = time.time()

  executor = ThreadPoolExecutor(max_workers=10)
  futures = []
  for ifut in range(100):
    futures.append(executor.submit(get_article))

  max_score = 0
  max_title = None
  for future in futures:
    (title, score) = future.result()
    if score > max_score:
        max_score = score
        max_title = title

  te = time.time()
  logging.debug("{} ({})".format(max_title, max_score))
  logging.debug("total time:{}".format(te-ts))

  return (max_title, max_score)


def get_link(debug=False):
    from urllib.parse import quote
    page = get_a_page()[0]
    return "<a href=http://fr.wikipedia.org/wiki/%s>%s</a>" % (quote(page), page)


if __name__ == "__main__":
  logging.basicConfig(level=logging.DEBUG)
  get_a_page(debug=True)
