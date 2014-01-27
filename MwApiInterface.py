
import urllib.request
import urllib.parse
import json

import sqlite3
import pickle
import os
import re


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
        returns a random page name in a given namespace (default main)
        """
        result = self.raw_query_request( {'list':'random', 'rnlimit':1, 'rnnamespace':0} )
        if self.debug:
            print ("Result: " + str(result) )
        page = result['query']['random'][0]
        return page['title']
    def get_page_links (self, title, namespace=0):
        """
        returns a list of all internal links in a page
        returns None if the page does not exist
        """
        if self.dbif:
            result = self.dbif.read_links(title)
        else:
            result = None
        if result is None:
            result = []
            query_continue = None
            while True:
                query = {'titles': title, 'prop': 'links',
                         'plnamespace': namespace, 'pllimit': 500}
                if query_continue:
                    query['plcontinue'] = query_continue
                    result_req = self.raw_query_request(query)
                else:
                    result_req = self.raw_query_request(query)
                if self.debug:
                    print ("Result: " + str(result_req) )
                pages = result_req['query']['pages']
                page_id = list(pages)[0]
                if page_id == '-1': #Page does not exist
                    result = None
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
            if 'redirlinks' in page:
                for subpage in page['redirlinks']:
                    result_list.append(subpage['title'])
            else:
                result_list.append(page['title'])
        return result_list

    def get_wikitext(self, title, expandtemplates=True):
        """
        returns the wikitext of the given article title
        """
        request = {'titles': title, 'prop': 'revisions', 'rvprop': 'content'}
        if expandtemplates:
            request['rvexpandtemplates'] = ''
        result = self.raw_query_request(request)
        if self.debug:
            print("Result: " + str(result))
        pages = result['query']['pages']
        page_id = list(pages)[0]
        if page_id == '-1':  # Page does not exist
            return None
        else:
            wikitext = pages[page_id]['revisions'][0]['*']
            return WikiText(wikitext)


class WikiText(str):
    def __init__(self, wikitext):
        str.__init__(wikitext)

    def get_links(self):
        links = re.findall("\[\[(.*?)\]\]", self)
        #Remove links with :
        links = [link for link in links if ':' not in link]
        #Remove |title constructs
        links = [re.sub("\|.*$", "", link) for link in links]
        #Capitalize first letter
        links = [link[0].upper() + link[1:] for link in links]

        return set(links)

    def count_occur(self, in_text):
        if type(in_text) == set:
            in_text = list(in_text)
        if type(in_text) == list:
            text = in_text[:]
            regexp = r"\b("
            for word in text[:-1]:
                word = word.replace("(", "\(")
                word = word.replace(")", "\)")
                regexp += r"%s|" % word
            word = text[-1]
            word = word.replace("(", "\(")
            word = word.replace(")", "\)")
            regexp += r"%s)\b" % word
            #print(regexp)
            all_matches = (re.findall(regexp, self, re.I))
            result = [0] * len(text)
            #print(all_matches)
            text = [elem.upper() for elem in text]
            for match in all_matches:
                result[text.index(match.upper())] += 1
            #print(result)
            return result
        elif type(in_text) == str:
            return len(re.findall(r"\b%s\b" % in_text, self, re.I))
        else:
            raise Exception
