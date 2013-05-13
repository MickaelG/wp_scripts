
import re, sys
import time, threading
import MwApiInterface

api = MwApiInterface.MwApiInterface('http://fr.wikipedia.org/w/api.php')



def get_article():
  data = api.raw_request( {'generator':'random', 'action':'query', 'prop':'categories', 'cllimit':500, 'clshow':'!hidden', 'grnnamespace':1} )
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
        if imp<1:
          imp = 1
      elif re.search("moyenne$", categ):
        if imp<10:
          imp = 10
      elif re.search("élevée$", categ):
        if imp<100:
          imp = 100
      elif re.search("maximum$", categ):
        if imp<1000:
          imp = 1000
      else:
        raise Exception('Unknown importance: {}'.format(categ))

  return (art_title, imp)

result = None
debug = False
threshold = 10
def worker(lock):
  global result
  (art_title, imp) = get_article()
  if debug:
    if imp > threshold:
      print ( "{} ({})".format(art_title, imp) )
      result = (art_title, imp)
    else:
      print ('.')
  else:
    if imp > threshold:
      if lock.acquire(False):
        result = (art_title, imp)

def get_a_page():
  global result

  if debug:
    ts = time.time()

  threads = []
  lock = threading.Lock()

  result = None
  while not result:
    if debug:
      print("New cycle")
    for i_thread in range(20):
      t = threading.Thread(target=worker, args=(lock,) )
      threads.append(t)
      t.start()

    [t.join() for t in threads]

  if debug:
    te = time.time()
    print ("total time:{}".format(te-ts))
  return result

if __name__ == "__main__":
  get_a_page()
