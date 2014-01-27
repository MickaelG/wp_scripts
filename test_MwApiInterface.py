#!/usr/bin/python3

import unittest

from MwApiInterface import MwApiInterface, WikiText

class Test_0_All( unittest.TestCase ):
    def setUp(self):
        self.api = MwApiInterface('http://fr.wikipedia.org/w/api.php')
    def test_00_get_random_page(self):
        result = self.api.get_random_page()
        print ("Result: " + str(result))
        self.assertTrue ( len(result) > 2 )
    def test_02_get_page_uplinks(self):
        result = self.api.get_page_uplinks('Théorème de Bayes')
        print ("Result: " + str(result))
        self.assertTrue ( len(result) > 5 )
    def test_021_get_page_uplinks_redirects(self):
        result = self.api.get_page_uplinks('Chiffre de Vigenère')
        self.assertIn('Charles Babbage', result)
    def test_03_get_page_categories(self):
        result = self.api.get_page_categories('Théorème de Bayes')
        print ("Result: " + str(result))
        self.assertTrue ( len(result) > 5 )
    def test_04_get_wikitext(self):
        result = self.api.get_wikitext('sntaetsnt')
        self.assertIsNone(result)
        result = self.api.get_wikitext('Thighpaulsandra')
        self.assertEqual(result[:50],
                         "{{Ébauche|musicien britannique}}\n[[File:Tighpaul.j")
        self.assertEqual(result[-34:], "[[Catégorie:Musicien britannique]]")

class Test_1_Links( unittest.TestCase ):
    def setUp(self):
        self.api = MwApiInterface('http://fr.wikipedia.org/w/api.php', "tmp_test.db")

    def tearDown(self):
        import os
        os.remove("tmp_test.db")

    def test_01_article_doesnt_exist(self):
        """
        get_page_links must return None if requested article does not exist
        """
        result = self.api.get_page_links("ATSECtsat et")
        self.assertIsNone(result)

    def test_11_check_data_cache_perf(self):
        import time
        time_b = time.perf_counter()
        result1 = self.api.get_page_links('Théorème de Bayes')
        time_e = time.perf_counter()
        time_result = 1000*(time_e-time_b)
        print ("Result1: {} in {:.3f} ms".format(str(result1), time_result))
        self.assertTrue( time_result>100 )

        time_b = time.perf_counter()
        result2 = self.api.get_page_links('Théorème de Bayes')
        time_e = time.perf_counter()
        time_result = 1000*(time_e-time_b)
        print ("Result2 in {:.3f} ms".format(time_result))
        self.assertTrue( time_result<1 )

        self.assertTrue ( len(result1) > 5 )
        self.assertEqual( result1, result2 )

    def test_12_more_than_500_links(self):
        result = self.api.get_page_links('Liste de photographes')
        self.assertTrue (len(result) > 500)


class Test_2_Links(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.api = MwApiInterface('http://fr.wikipedia.org/w/api.php',
                                  "tmp_test.db")

    def tearDown(self):
        import os
        os.remove("tmp_test.db")

    def test_01_extract_links_wikitext(self):
        article = "Dinosaure"
        wikitext = self.api.get_wikitext(article)
        links = self.api.get_page_links(article)
        wt_links = wikitext.get_links()
        self.assertEqual(sorted(links), sorted(wt_links))

    def test_02_count_occur(self):
        text = WikiText("Cryptographie [[Cryptographie]] cryptographie"
                        "cryptographier")
        result = text.count_occur("cryptographie")
        self.assertEqual(result, 3)


if __name__ == '__main__':
    unittest.main(verbosity=2)
