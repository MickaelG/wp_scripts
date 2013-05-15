#!/usr/bin/python3

import unittest

import MwApiInterface

class Test_0_All( unittest.TestCase ):
    def setUp(self):
        self.api = MwApiInterface.MwApiInterface('http://fr.wikipedia.org/w/api.php')
    def test_00_get_random_page(self):
        result = self.api.get_random_page()
        print ("Result: " + str(result))
        self.assertTrue ( len(result) > 2 )
    def test_02_get_page_uplinks(self):
        result = self.api.get_page_uplinks('Théorème de Bayes')
        print ("Result: " + str(result))
        self.assertTrue ( len(result) > 5 )
    def test_03_get_page_categories(self):
        result = self.api.get_page_categories('Théorème de Bayes')
        print ("Result: " + str(result))
        self.assertTrue ( len(result) > 5 )

class Test_1_Links( unittest.TestCase ):
    def setUp(self):
        self.api = MwApiInterface.MwApiInterface('http://fr.wikipedia.org/w/api.php', "tmp_test.db")
    def tearDown(self):
        import os
        os.remove("tmp_test.db")
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

if __name__ == '__main__':
    unittest.main(verbosity=2)

