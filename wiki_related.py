#!/usr/bin/python3

import MwApiInterface

#Number of level 2 articles to select
Level2Articles = 100
#BaseArticle = "Théorème de Bayes"
BaseArticle = "Cryptologie"
#BaseArticle = "Mathématiques"

api = MwApiInterface.MwApiInterface('http://fr.wikipedia.org/w/api.php', debug=False)

selected_articles = [BaseArticle]

level1 = api.get_page_links(BaseArticle)
print ( "Level 1: {} articles".format(len(level1)) )

selected_articles.extend( list(set(level1)) )

level2 = []
for article in level1:
    local_level2 = api.get_page_links(article)
    print ( "Article {}: {} articles".format(article, len(local_level2)) )
    level2.extend ( local_level2 )

print ( "Level 2: {} articles".format(len(level2)) )

level2_nodup = list(set(level2))
print ( "Level 2 without duplicates: {} articles".format(len(level2_nodup)) )


#number_of_level2 = TotalArticles-len(level1)
number_of_level2 = Level2Articles
if number_of_level2 > 0:
    import collections
    counter = collections.Counter([article for article in level2 if article not in selected_articles])
    most_commons = counter.most_common(number_of_level2)
    print (most_commons)
    selected_articles.extend( [article[0] for article in most_commons] )

print ( "selected: {} articles (theory: {})".format(len(selected_articles), len(list(set(level1)))+Level2Articles+1) )
print ( "selected without duplicates: {} articles".format(len(list(set(selected_articles)))) )
print ("Selection: " + str(sorted(selected_articles)))
