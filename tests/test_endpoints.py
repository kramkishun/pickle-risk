import os
import tempfile

import unittest, pprint, json

from pickle_risk import create_app

class TestEndpoints(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_root(self):
        rsp = self.client.get('/')
        self.assertEqual(rsp.data, b'Check out /history')

    def test_history_error(self):
        rsp = self.client.get('/history/')
        self.assertEqual(rsp.data, b'{"error": "NoSuchSymbol"}')

    def test_history_aapl(self):
        rsp = self.client.get('/history/AAPL')
        all_data = json.loads(rsp.data)
        self.assertAlmostEqual(all_data['2018-11-13'], 192.22999572753906, places=4)

if __name__ == '__main__':
    unittest.main()


