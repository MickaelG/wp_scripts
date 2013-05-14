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

def get_feedback_score(article, fb_list):
    link_list = api.get_page_links(article)
    nb_of_links = len(link_list)
    nb_of_matching_links = len([tmp_art for tmp_art in link_list if tmp_art in fb_list])
    if nb_of_links:
        feedback_score = 100*nb_of_matching_links/nb_of_links
    else:
        feedback_score = 0.0
    return (feedback_score, nb_of_links)

fb_articles_list = [BaseArticle]
for article in level1:
    (fb_score, nb_of_links) = get_feedback_score(article, selected_articles)
    print ( "Article {}: {} links, feedback score: {:.2}%".format(article, nb_of_links, fb_score ) )
    if fb_score > 2: #2%. Low level to only discriminate unrelated
        fb_articles_list.append(article)


level2 = []
for article in fb_articles_list:
    local_level2 = api.get_page_links(article)
    print ( "Article {}: {} articles".format(article, len(local_level2) ) )
    level2.extend ( local_level2 )

print ( "Level 2: {} articles".format(len(level2)) )
level2 = list(set(level2))
level2 = [article for article in level2 if article not in selected_articles]
print ( "Level 2 without duplicates: {} articles".format(len(level2)) )

level2_fbs = []
for article in level2:
    (feedback_score, nb_of_links) = get_feedback_score(article, fb_articles_list)
    print ( "Article {}: {} links, feedback score: {:.2}%".format(article, nb_of_links, feedback_score ) )
    level2_fbs.append( (article, feedback_score) )

#sort elements by feedback score
level2_fbs.sort(key=lambda elem:elem[1])

number_of_level2 = Level2Articles
level2_selection = [article[0] for article in level2_fbs[0:number_of_level2-1]]
print( "level2 selection: " + str(sorted(level2_selection)) )
print( "last selected article score: {}".format(level2_fbs[number_of_level2-1])
selected_articles.extend( level2_selection )

print ( "selected: {} articles (theory: {})".format(len(selected_articles), len(list(set(level1)))+Level2Articles+1) )
print ( "selected without duplicates: {} articles".format(len(list(set(selected_articles)))) )
print ("Selection: " + str(sorted(selected_articles)))
