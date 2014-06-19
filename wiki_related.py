#!/usr/bin/python3

import MwApiInterface

##################################################
# Parameters
##################################################
#Number of level 2 articles to select
Level2Articles = 100
#Score under which level1 articles are not used for level2 selection
Level1ScoreThreshold = 0.02

#BaseArticle = "Théorème de Bayes"
BaseArticle = "Cryptologie"
#BaseArticle = "Mathématiques"

##################################################
# Functions
##################################################

def get_insubject_score(article,  subject_list):
    """
    article: name of the article to analyse
    subject_list: can be a dictionary giving the subject_score of each article
    or a list of articles (a score of 1 is assumed in this case)
    """
    links_list = api.get_page_links(article)
    if links_list is None:
        return (0, 0)
    nb_of_links = len(links_list)
    score = 0
    for article_link in links_list:
            if article_link in subject_list:
                    if type(subject_list) == dict:
                        score += subject_list[article_link]
                    else:
                        score += 1
    if nb_of_links == 0:
        final_score = 0
    else:
        final_score = score/nb_of_links
    return (final_score,  nb_of_links)

##################################################
# Main
##################################################

api = MwApiInterface.MwApiInterface('http://fr.wikipedia.org/w/api.php', "wp_data_cache.db", debug=False)

selected_articles = [BaseArticle]

level1 = api.get_page_links(BaseArticle)
level1 = list(set(level1)) #To remove duplicates entries
print ( "Level 1: {} articles".format(len(level1)) )

selected_articles.extend( level1 )

subject_definition_articles = {}
subject_definition_articles[BaseArticle] = 1
level1_clean = []
for article in level1:
    (score, nb_of_links) = get_insubject_score(article, selected_articles)
    print ( "Article {}: {} links, score: {:.3f}%".format(article, nb_of_links, score*100 ) )
    if score > Level1ScoreThreshold: #discriminate unrelated articles for level2 analysis, to improve runtime
        subject_definition_articles[article] = score
        level1_clean.append(article)

print ( "Level 1 for level 2 analysis: {} articles".format(len(level1_clean)) )

level2 = []
for article in level1_clean :
    local_level2 = api.get_page_links(article)
    print ( "Article {}: {} articles".format(article, len(local_level2) ) )
    level2.extend ( local_level2 )

#Remove duplicates in level2
level2 = list(set(level2))
#Remove already selected article from level2
level2 = [article for article in level2 if article not in selected_articles]
print ( "Level 2: {} articles".format(len(level2)) )

level2_with_score = []
last_prog = 0
print ("Analysing level 2 articles…")
for (index, article) in enumerate(level2):
    (score, nb_of_links) = get_insubject_score(article, subject_definition_articles)
    #print ( "Article {}: {} links, feedback score: {:.3f}%".format(article, nb_of_links, score*100 ) )
    level2_with_score.append( (article, score) )
    progression = int(100*index/len(level2))
    if not progression%10 and progression != last_prog:
        print ("{}% done".format(progression))
        last_prog = progression

#sort elements by score
level2_with_score.sort(key=lambda elem:elem[1],  reverse=True)

logf = open("level2.log",  "w")
logf.write ("Level2 articles with feedback score\n")
for elem in level2_with_score:
    logf.write("{:.4f} : {}\n".format(elem[1]*100,  elem[0]))

number_of_level2 = Level2Articles
level2_selection = [article[0] for article in level2_with_score[0:number_of_level2]]
print("level2 selection: " + str(sorted(level2_selection)) )
print("last selected article score: {}".format(level2_with_score[number_of_level2]))
selected_articles.extend( level2_selection )

print ("Selected: {} articles".format(len(selected_articles)))
print ("Selection: " + str(sorted(selected_articles)))
