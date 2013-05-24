
import urllib.request, urllib.parse
import json

import sqlite3
import pickle
import os
class DbIf:
    def __init__(self, filename):
        new_db = not os.path.exists(filename)
        self.sqlcon = sqlite3.connect(filename)
        if new_db:
            self._create_tables()
    def _create_tables(self):
        self.sqlcon.execute("create table links (article text primary key, link_list blob)")
        self.sqlcon.execute("create table categories (article text primary key, categ_list blob)")
        self.sqlcon.commit()
    def write_links(self, article, link_list):
        self.sqlcon.execute("insert into links values (?,?)", (article, pickle.dumps(link_list)))
        self.sqlcon.commit()
    def write_categories(self, article, categ_list):
        self.sqlcon.execute("insert into categories values (?,?)", (article, pickle.dumps(categ_list)))
        self.sqlcon.commit()
    def read_links(self, article):
        result = self.sqlcon.execute("select * from links where article=?", (article,)).fetchone()
        if result == None:
            return None
        else:
            return pickle.loads(result[1])
    def read_categories(self, article):
        result = self.sqlcon.execute("select * from categories where article=?", (article,)).fetchone()
        if result == None:
            return None
        else:
            return pickle.loads(result[1])

class MwApiInterface:
    def __init__(self, api_addr, db_filename=None, debug=False):
        self.api = api_addr
        self.debug = debug
        if db_filename:
            self.dbif = DbIf(db_filename)
        else:
            self.dbif = None
    def _request (self, data):
        dataenc = urllib.parse.urlencode(data)
        req_addr = self.api + "?" + dataenc
        if self.debug:
            print ("Request to api address: " + req_addr)
        f = urllib.request.urlopen(req_addr)
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
        if self.dbif:
            result = self.dbif.read_links(title)
        else:
            result = None
        if result == None:
            result = []
            query_continue = None
            while True:
                if query_continue:
                    result_req = self.raw_query_request( {'titles':title, 'prop':'links', 'plnamespace':namespace, 'pllimit':500, 'plcontinue':query_continue} )
                else:
                    result_req = self.raw_query_request( {'titles':title, 'prop':'links', 'plnamespace':namespace, 'pllimit':500} )
                if self.debug:
                    print ("Result: " + str(result) )
                pages = result_req['query']['pages']
                page_id = list(pages)[0]
                if page_id == '-1': #Page does not exist
                    break
                else:
                    result.extend([link['title'] for link in pages[page_id]['links']])
                    if 'query-continue' in result_req:
                        query_continue = result_req['query-continue']['links']['plcontinue']
                    else:
                        break
            if self.dbif:
                self.dbif.write_links(title, result)
        return result
    def get_page_categories (self, title):
        """
        returns a list of all categories of a page
        """
        if self.dbif:
            result = self.dbif.read_categories(title)
        else:
            result = None
        if result == None:
            result_req = self.raw_query_request( {'titles':title, 'prop':'categories', 'cllimit':500} )
            if self.debug:
                print ("Result: " + str(result_req) )
            pages = result_req['query']['pages']
            page_id = list(pages)[0]
            if page_id == '-1': #Page does not exist
                result = []
            else:
                if 'categories' in pages[page_id]:
                    result = [categ['title'] for categ in pages[page_id]['categories']]
                else:
                    result = []
            if self.dbif:
                self.dbif.write_categories(title, result)
        return result
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
