
import urllib.request, urllib.parse
import json

class MwApiInterface:
    def __init__(self, api_addr, debug=False):
        self.api = api_addr
        self.debug = debug
    def _request (self, data):
        dataenc = urllib.parse.urlencode(data)
        f = urllib.request.urlopen(self.api + "?" + dataenc)
        raw_result = f.read()
        result = json.loads(raw_result.decode('utf-8'))
        return result
    def raw_query_request (self, req_dict):
        req_dict['format'] = 'json'
        req_dict['action'] = 'query'
        return self._request(req_dict)

    def get_random_page (self, namespace=0):
        """
        returns a random page in given namespace (default main)
        """
        result = self.raw_query_request( {'list':'random', 'rnlimit':1, 'rnnamespace':0} )
        if self.debug:
            print ("Result: " + str(result) )
        page = result['query']['random'][0]
        return page['title']
    def get_page_links (self, title, namespace=0):
        """
        returns a list of all internal links in a page
        """
        result = self.raw_query_request( {'titles':title, 'prop':'links', 'plnamespace':namespace, 'pllimit':500} )
        if self.debug:
            print ("Result: " + str(result) )
        pages = result['query']['pages']
        page_id = list(pages)[0]
        if page_id == '-1': #Page does not exist
            return []
        else:
            return [link['title'] for link in pages[page_id]['links']]
    def get_page_categories (self, title, namespace=0):
        """
        returns a list of all categories of a page
        """
        result = self.raw_query_request( {'titles':title, 'prop':'categories', 'plnamespace':namespace, 'pllimit':500} )
        if self.debug:
            print ("Result: " + str(result) )
        pages = result['query']['pages']
        page_id = list(pages)[0]
        return [categ['title'] for categ in pages[page_id]['categories']]
    def get_page_uplinks (self, title, namespace=0):
        """
        returns a list of all internal links which go to a page
        """
        result = self.raw_query_request( {'list':'backlinks', 'bltitle':title, 'blnamespace':namespace, 'bllimit':500, 'blredirect':''} )
        if self.debug:
            print ("Result: " + str(result) )
        pages = result['query']['backlinks']
        result_list = []
        for page in pages:
            if 'redirect' in page:
                for subpage in page['redirlinks']:
                    result_list.append(subpage['title'])
            else:
                result_list.append(page['title'])
        return result_list
