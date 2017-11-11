
import urllib.request, urllib.parse
import re, sys, json
import NaiveBayes

def getwords(doc):
  splitter=re.compile('\\W*')
  # Split the words by non-alpha characters
  words=[s.lower() for s in splitter.split(doc) 
          if len(s)>2 and len(s)<20]
  # Return the unique set of words only
  return [w for w in words]

#proxy = urllib.request.ProxyHandler({'http': r'http://mgi:totpiw27@proxy.disa.dolphin.fr:8080/'})
#auth = urllib.request.HTTPBasicAuthHandler()
#opener = urllib.request.build_opener(proxy, auth, urllib.request.HTTPHandler)
#urllib.request.install_opener(opener)

wiki = 'http://fr.wikipedia.org/w/api.php'
def request (data):
	dataenc = urllib.parse.urlencode(data)
	f = urllib.request.urlopen(wiki + "?" + dataenc)
	result = f.read()
	return result

def train():
  (title, page_id, content) = get_random_page()
  print ( "====================== {}, id={} =============================".format(title, page_id) )
  print ( content )

  classifier = init_classifier()

  words = getwords(content)
  print (classifier.classify(words, 'interesting'))

  result = None
  while result != 'i' and result != 'n':
    result = input("What do you think (i/n) ?")

  if result == 'i':
    classifier.train(words, 'interesting')
  else:
    classifier.train(words, 'not-interesting')

  classifier.save_data("test.json")


def get_random_page():
  random_page = request( {'generator':'random', 'action':'query', 'prop':'revisions', 'rvprop':'content', 'rvlimit':1, 'format':'json', 'grnnamespace':0} )
  data = json.loads(random_page.decode('utf-8'))
  page_id, page_data = data['query']['pages'].popitem()
  title = page_data['title']
  content = page_data['revisions'][0]['*']
  return ( title, page_id, content )

def get_page_by_id( page_id ):
  random_page = request( {'action':'query', 'pageids':page_id, 'prop':'revisions', 'rvprop':'content', 'rvlimit':1, 'format':'json', 'grnnamespace':0} )
  data = json.loads(random_page.decode('utf-8'))
  page_id, page_data = data['query']['pages'].popitem()
  title = page_data['title']
  content = page_data['revisions'][0]['*']
  return ( title, page_id, content )

def init_classifier():
  import NaiveBayes
  classifier = NaiveBayes.NaiveBayes()
  classifier.load_data("test.json")
  classifier.default_threshold = 2
  return classifier

def get_page_note(page_id):
  (title, page_id, content) = get_page_by_id(page_id)
  words = getwords(content)
  classifier = init_classifier()
  (res, interest) = classifier.classify(words, 'interesting')
  return interest

def train_with_article( page_id, interesting ):
  print("Training with article id {} ({})".format(page_id, interesting))
  (title, page_id, content) = get_page_by_id(page_id)
  words = getwords(content)

  classifier = init_classifier()
  if interesting:
    classifier.train(words, 'interesting')
  else:
    classifier.train(words, 'not-interesting')
  classifier.save_data("test.json")

def generate_page_list( nb=10, only_interesting=False):
  pages_list = []
  nb_pages = 0
  nb_of_trials = 0
  while nb_pages < nb:
    nb_of_trials += 1
    (title, page_id, content) = get_random_page()
    classifier = init_classifier()
    words = getwords(content)
    (res, interest) = classifier.classify(words, 'interesting')
    if interest > 1 or not only_interesting:
      pages_list.append( (title, page_id, interest, nb_of_trials) )
      nb_of_trials = 0
      nb_pages +=1
  return pages_list

def main():
  (title, page_id, content) = get_page_by_id(5985933)
  print ( "====================== {}, id={} =============================".format(title, page_id) )
  print ( content )

if __name__ == "__main__":
  main()
