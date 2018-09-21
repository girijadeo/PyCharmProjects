import datetime
from unittest import TestLoader, TestSuite


from selenium import webdriver
import unittest

class TestRandomTests(unittest.TestCase):

    def test_01(self):
        # driver = webdriver.Chrome("C:\\Users\\GDeo\\Downloads\\chromedriver_win32_03202018\\chromedriver.exe")
        # driver.get("https://www.google.com")
        x= "OK"
        assert x=="OK","FAIL"

    def test_02(self):
        # driver = webdriver.Chrome("C:\\Users\\GDeo\\Downloads\\chromedriver_win32_03202018\\chromedriver.exe")
        # driver.get("https://www.google.com")
        x= "OK1"
        assert x=="OK","FAIL"

    def test_03(self):
        # driver = webdriver.Chrome("C:\\Users\\GDeo\\Downloads\\chromedriver_win32_03202018\\chromedriver.exe")
        # driver.get("https://www.google.com")
        x= "OK"
        assert x=="OK","FAIL"


if __name__ == '__main__':
    unittest.main()
    file_name = datetime.datetime.now().strftime("%Y_%m_%d_%H%M_report.html")

    output = open(file_name, "wb")

    loader = TestLoader()
    suite = TestSuite((
        loader.loadTestsFromTestCase(TestRandomTests)
    ))
    runner = HTMLTestRunner(stream=output, verbosity=1, title="Regression Suite")
    runner.run(suite)