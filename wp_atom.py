#!/usr/bin/python3

import sys
import datetime

sys.path.append("../wiki_bayes/")
from wiki_important import get_a_page


def page_to_link(page):
    from urllib.parse import quote
    return "http://fr.wikipedia.org/wiki/%s" % quote(page)


def add_to_json(json_file="wikipedia.json"):
    import json
    try:
        data = json.load(open(json_file))
    except:
        data = {}
    today = str(datetime.date.today())
    if today not in data:
        data[today] = get_a_page()[0]
        with open(json_file, "w") as fp:
            json.dump(data, fp, indent=4)
    return data


def atom():
    data = add_to_json()
    result = ""
    result += '<?xml version="1.0" encoding="utf-8"?>\n'
    result += '<feed xmlns="http://www.w3.org/2005/Atom">\n\n'
    result += ' <title>Wikipedia fr</title>\n'
    for date in sorted(data, reverse=True):
        datef = date + "T11:00:00Z"
        title = data[date]
        link = page_to_link(title)
        result += ' <entry>\n'
        result += '   <title>%s</title>\n' % title
        result += '   <link href="%s"/>\n' % link
        result += '   <updated>%s</updated>\n' % datef
        result += ' </entry>\n'
    result += '\n</feed>\n'
    return result

if __name__ == '__main__':
    print(atom())
