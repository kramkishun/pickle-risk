import os
import tempfile

import unittest, pprint, json
import logging
from pickle_risk import create_app

class TestEndpoints(unittest.TestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.app = create_app()
        self.client = self.app.test_client()
        self.ERROR_NO_SUCH_SYMBOL = b'{"error": "NoSuchSymbol"}'
    
    def tearDown(self):
        logging.disable(logging.NOTSET)

    def test_root(self):
        rsp = self.client.get('/')
        self.assertEqual(rsp.data, b'Check out /history')

    def test_history_error(self):
        rsp = self.client.get('/history/')
        self.assertEqual(rsp.data, self.ERROR_NO_SUCH_SYMBOL)
        rsp = self.client.get('/history')
        self.assertEqual(rsp.status_code, 301)

    def test_history_aapl(self):
        rsp = self.client.get('/history/AAPL')
        all_data = json.loads(rsp.data)
        self.assertAlmostEqual(all_data['2018-11-13'], 192.22999572753906, places=4)

    def test_multihistory_error(self):
        rsp = self.client.get('/multihistory/')
        self.assertEqual(rsp.data, self.ERROR_NO_SUCH_SYMBOL)
        rsp = self.client.get('/multihistory')
        self.assertEqual(rsp.status_code, 301)
        rsp = self.client.get('/multihistory?notdefined')
        self.assertEqual(rsp.status_code, 301)
        rsp = self.client.get('/multihistory?notdefined=badparameter')
        self.assertEqual(rsp.status_code, 301)
        rsp = self.client.get('/multihistory?symbols=AAPL,MSFT,badparameter')
        self.assertEqual(rsp.status_code, 301)
        rsp = self.client.get('/multihistory/?symbols=AAPL,MSFT,badparameter')
        self.assertEqual(rsp.data, self.ERROR_NO_SUCH_SYMBOL)
        
    def test_multihistory_aapl_msft(self):
        rsp = self.client.get('/multihistory/?symbols=AAPL,MSFT')
        all_data = json.loads(rsp.data)
        dates = all_data[0]
        closes = all_data[1]
        indexOfDate = dates.index('2018-11-13')
        self.assertAlmostEqual(closes[indexOfDate][0], 192.22999572753906, places = 4)
        self.assertAlmostEqual(closes[indexOfDate][1], 106.94000244140625, places = 4)

if __name__ == '__main__':
    unittest.main()


