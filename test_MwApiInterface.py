#!/usr/bin/python3

import unittest

import MwApiInterface

class TestRandom( unittest.TestCase ):
    def setUp(self):
        self.api = MwApiInterface.MwApiInterface('http://fr.wikipedia.org/w/api.php')
    def test_00_get_random_page(self):
        result = self.api.get_random_page()
        print ("Result: {}" + str(result))
    def test_01_get_page_links(self):
        result = self.api.get_page_links('Théorème de Bayes')
        print ("Result: " + str(result))
    def test_02_get_page_uplinks(self):
        result = self.api.get_page_uplinks('Théorème de Bayes')
        print ("Result: " + str(result))
    def test_03_get_page_categories(self):
        result = self.api.get_page_categories('Théorème de Bayes')
        print ("Result: " + str(result))


if __name__ == '__main__':
    unittest.main(verbosity=2)

