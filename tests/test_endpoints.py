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
        dates = all_data['X Axis Labels']
        closes = all_data['Y Axis Data']
        indexOfDate = dates.index('2018-11-13')
        self.assertAlmostEqual(closes[0][indexOfDate], 192.22999572753906, places = 4)
        self.assertAlmostEqual(closes[1][indexOfDate], 106.94000244140625, places = 4)
        self.assertEqual(len(closes[0]), len(dates))
        self.assertEqual(len(closes[1]), len(dates))

    def test_consistency_single_multi(self):
        """ Data received from a single /history query and a /multihistory query for
        a given symbol should be the same. """
        # TODO: Clean up
        def compare_single_to_multi (single, multi, idx):    
            i = 0
            for key in single:
                self.assertEqual(single[key], multi['Y Axis Data'][idx][i])
                i += 1

        rsp_single_AAPL = json.loads(self.client.get('/history/AAPL').data)
        rsp_single_MSFT = json.loads(self.client.get('/history/MSFT').data)
        rsp_single_GE = json.loads(self.client.get('/history/GE').data)
        rsp_multi = json.loads(self.client.get('/multihistory/?symbols=AAPL,MSFT,GE').data)

        compare_single_to_multi(rsp_single_AAPL, rsp_multi, 0)
        compare_single_to_multi(rsp_single_MSFT, rsp_multi, 1)
        compare_single_to_multi(rsp_single_GE, rsp_multi, 2)

    def test_multi_order_agnostic(self):
        rsp_multi_1 = json.loads(self.client.get('/multihistory/?symbols=AAPL,MSFT').data)
        rsp_multi_2 = json.loads(self.client.get('/multihistory/?symbols=MSFT,AAPL').data)

        self.assertSequenceEqual(rsp_multi_1['Y Axis Data'][0], rsp_multi_2['Y Axis Data'][1])
        self.assertSequenceEqual(rsp_multi_1['Y Axis Data'][1], rsp_multi_2['Y Axis Data'][0])
        self.assertSequenceEqual(rsp_multi_1['X Axis Labels'], rsp_multi_2['X Axis Labels'])

if __name__ == '__main__':
    unittest.main()


