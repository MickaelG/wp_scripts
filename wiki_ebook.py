#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import MwApiInterface
import random
import sys
from PyQt4 import QtGui, QtCore

import urllib.request
import urllib.parse
import json
import time

import os
import re


class WpEbook():
    def __init__(self):
        self.api = MwApiInterface.MwApiInterface(
            'http://fr.wikipedia.org/w/api.php')
        self.articles = []
        self.rejected = []
        #Random score < 0.1 added for each link, and kept during all the
        #session to discriminate links with same score for suggestions
        self.link_rand_score = {}

        #For each article in articles, list of tuples (link, score)
        self.articles_links = {}

    def get_suggestions(self, nb_suggestions=10):
        self._update_articles_links()
        links = {}

        for article in self.articles:
            for (article_link, score) in self.articles_links[article]:
                if article_link not in self.articles and \
                   article_link not in self.rejected:
                    if article_link in links:
                        links[article_link] += score
                    else:
                        links[article_link] = score

        for link in links:
            if link in self.link_rand_score:
                rand_score = self.link_rand_score[link]
            else:
                rand_score = random.random() * 0.1
                assert rand_score < 0.1
                self.link_rand_score[link] = rand_score
            links[link] += rand_score

        sorted_links = sorted(links.items(), key=lambda link: link[1],
                              reverse=True)

        result = []
        if nb_suggestions > len(sorted_links):
            result = [link[0] for link in sorted_links]
        else:
            result = [link[0] for link in sorted_links[0:nb_suggestions]]

        assert len(result) <= nb_suggestions
        return result

    def _update_articles_links(self):
        time0 = time.time()
        for article in self.articles:
            if article not in self.articles_links:
                links = []
                wikitext = self.api.get_wikitext(article)
                wt_links = wikitext.get_links()
                print("Nb of links: %i / %i" % (len(wt_links), len(set(wt_links))))
                print("link subloop at %f" % (time.time() - time0))
                counts = wikitext.count_occur(wt_links)
                for (link, count) in zip(wt_links, counts):
                    score = 1 + (count - 1) * 0.1
                    links.append((link, score))
                self.articles_links[article] = links
                print("link loop5 at %f" % (time.time() - time0))
        print("End up art after %f" % (time.time() - time0))

    def get_suggestions_links_only(self, nb_suggestions=10):
        all_links = []
        for article in self.articles:
            uplinks = self.api.get_page_links(article)
            all_links.extend(links)

        links_score = []
        for link in set(all_links):
            if link not in self.articles and link not in self.rejected:
                nb_occur = all_links.count(link)
                if link in self.link_rand_score:
                    rand_score = self.link_rand_score[link]
                else:
                    rand_score = random.random()
                    self.link_rand_score[link] = rand_score
                links_score.append((link, nb_occur + rand_score))

        links_score.sort(key=lambda link: link[1], reverse=True)
        result = []
        if nb_suggestions > len(links_score):
            result = [link[0] for link in links_score]
        else:
            result = [link[0] for link in links_score[0:nb_suggestions]]

        assert len(result) <= nb_suggestions
        return result


def main_perf():
    ebook = WpEbook()
    article = "Dinosaure"
    ebook.articles.append(article)
    #suggestions = ebook.get_suggestions()

    wikitext = ebook.api.get_wikitext(article)
    wt_links = wikitext.get_links()

    print("Nb of links: %i / %i" % (len(wt_links), len(set(wt_links))))

    time0 = time.time()
    links1 = []
    for link in wt_links:
        nb_occur = wikitext.count_occur(link)
        score = 1 + (nb_occur - 1) * 0.1
        links1.append((link, score))
    print("link loop1 at %f" % (time.time() - time0))

    time0 = time.time()
    links2 = []
    counts = wikitext.count_occur(wt_links)
    assert type(counts) == list, type(counts)
    for (link, count) in zip(wt_links, counts):
        score = 1 + (count - 1) * 0.1
        links2.append((link, score))
    print("link loop2 at %f" % (time.time() - time0))

    assert links1 == links2, str(links1) + str(links2)


class ListModel(QtCore.QAbstractListModel):
    def __init__(self, elem_list, parent=None):
        super().__init__(parent)
        self.elem_list = elem_list

    def rowCount(self, parent):
        return len(self.elem_list)

    def data(self, index, role):
        if role == 0:
            if index.column() == 0:
                return self.elem_list[index.row()]


class ListWidget(QtGui.QListView):
    def __init__(self, elem_list, parent=None):
        super().__init__(parent)
        model = ListModel(elem_list)
        self.setModel(model)

    def index(self):
        result = self.selectionModel().currentIndex().row()
        if result < 0:
            return None
        return result.name

    def update_list(self):
        self.model().layoutChanged.emit()


class MainWindow(QtGui.QWidget):
    """
    Main application window
    """
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.ebook = WpEbook()

        self.showMaximized()
        self.layout = QtGui.QGridLayout(self)

        self.result_widget = ListWidget(self.ebook.articles, self)

        self.labela = QtGui.QLabel('New article:', self)
        self.article_edit = QtGui.QLineEdit(self)
        self.add_article_btn = QtGui.QPushButton("Add article", self)
        self.add_article_btn.clicked.connect(lambda: self.add_article())
        tmplayout = QtGui.QHBoxLayout()
        tmplayout.addWidget(self.labela)
        tmplayout.addWidget(self.article_edit)
        tmplayout.addWidget(self.add_article_btn)

        self.sugg_widget = SuggestionsWidget()
        self.sugg_widget.add_article.connect(self.add_article)
        self.sugg_widget.rej_article.connect(self.reject_article)

        self.layout.addWidget(self.result_widget)
        self.layout.addLayout(tmplayout, 1, 0)
        self.layout.addWidget(self.sugg_widget)

    def add_article(self, article=None):
        if article is None:
            article = self.article_edit.text()
        if article in self.ebook.articles:
            QtGui.QMessageBox.warning(
                self, "Warning",
                "Article {} already in selection".format(article))
            return

        article_links = self.ebook.api.get_page_links(article)
        if article_links is None:
            QtGui.QMessageBox.warning(
                self, "Warning", "Article {} does not exist".format(article))
            return

        self.ebook.articles.append(article)
        print(self.ebook.articles)
        self.result_widget.update_list()
        self.update_suggestions()
        print("Article {} added".format(article))

    def reject_article(self, article):
        self.ebook.rejected.append(article)
        self.update_suggestions()

    def create_sugg_widget(self):
        result = QtGui.QWidget(self)
        layout = QtGui.QVerticalLayout()
        result.addLayout(layout)
        return result

    def update_suggestions(self):
        suggestions = self.ebook.get_suggestions()
        print("new suggestions : {}".format(suggestions))
        self.sugg_widget.update(suggestions)


class SuggestionsWidget(QtGui.QWidget):
    add_article = QtCore.pyqtSignal(str)
    rej_article = QtCore.pyqtSignal(str)

    def __init__(self, nb_suggestions=10, parent=None):
        super().__init__(parent)
        self.layout = QtGui.QVBoxLayout(self)
        self.sugg_layouts = []
        self.labels = []

        for isug in range(nb_suggestions):
            linelayout = QtGui.QHBoxLayout()
            add_btn = QtGui.QPushButton("+", self)
            rej_btn = QtGui.QPushButton("-", self)
            label = QtGui.QLabel(self)
            add_btn.clicked.connect(lambda s, isug=isug: self.add_article.emit(self.suggestions[isug]))
            rej_btn.clicked.connect(lambda s, isug=isug: self.rej_article.emit(self.suggestions[isug]))
            linelayout.addWidget(add_btn)
            linelayout.addWidget(rej_btn)
            linelayout.addWidget(label)
            self.layout.addLayout(linelayout)
            self.sugg_layouts.append(linelayout)
            self.labels.append(label)
        self.update([])

    def update(self, suggestions):
        self.suggestions = suggestions
        for il, layout in enumerate(self.sugg_layouts):
            if il < len(suggestions):
                for iw in range(layout.count()):
                    itemw = layout.itemAt(iw)
                    itemw.widget().setEnabled(True)
                self.labels[il].setText(suggestions[il])
            else:
                for iw in range(layout.count()):
                    itemw = layout.itemAt(iw)
                    itemw.widget().setEnabled(False)
                self.labels[il].setText("")


def main_gui():
    app = QtGui.QApplication(sys.argv)
    MainWin = MainWindow()
    MainWin.show()
    sys.exit(app.exec_())


##############################################################################
# TEST
##############################################################################
import unittest


class Test01suggestions(unittest.TestCase):
    def setUp(self):
        self.ebook = WpEbook()

    def test_00_add_existing(self):
        """
        Tests that rejecting an article does not change the order of next
        suggestion
        """
        self.ebook.articles.append("Chien")
        sug1 = self.ebook.get_suggestions()
        self.ebook.rejected.append(sug1[3])
        sug2 = self.ebook.get_suggestions()
        self.assertEqual(sug2[0:7], sug1[0:3] + sug1[4:8])


def launch_tests():
    unittest.main(verbosity=2, argv=[__file__])
##############################################################################


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        launch_tests()
    elif len(sys.argv) > 1 and sys.argv[1] == "perf":
        main_perf()
    else:
        main_gui()

if __name__ == '__main__':
    main()
