import unittest

from .reporter import check_log_file
from StringIO import StringIO
import datetime

class ReporterTest(unittest.TestCase):
    def test_line_matcher(self):
        line = '2013-10-04 12:43:10,401 ERROR  [ckanext.importlib.loader] Foo'
        results = list(check_log_file(StringIO(line), ['ERROR']))
        self.assertEqual(1, len(results))
        self.assertEqual(datetime.datetime(2013, 10, 4, 12, 43, 10), results[0]['when'])
        self.assertEqual('ckanext.importlib.loader', results[0]['who'])
        self.assertEqual('Foo', results[0]['message'])

    def test_syslog_ignore_debug(self):
        line = 'Aug  6 05:27:33 co-prod3 2014-08-06 05:27:33,370 DEBUG [ckan.lib.base] Foo'
        self.assertEqual(0, len(list(check_log_file(StringIO(line), ['ERROR']))))

    def test_syslog_matcher(self):
        line = 'Aug  6 05:27:33 co-prod3 2014-08-06 05:27:33,370 ERROR [ckan.lib.base] Foo'
        results = list(check_log_file(StringIO(line), ['ERROR']))
        self.assertEqual(1, len(results))
        self.assertEqual(datetime.datetime(2014, 8, 6, 5, 27, 33), results[0]['when'])
        self.assertEqual('ckan.lib.base', results[0]['who'])
        self.assertEqual('Foo', results[0]['message'])

    def test_apache_error_matcher(self):
        line = '[Tue Aug 05 06:17:12 2014] [error] [client 127.0.0.1] Foo'
        results = list(check_log_file(StringIO(line), ['error']))
        self.assertEqual(1, len(results))
        self.assertEqual(datetime.datetime(2014, 8, 5, 6, 17, 12), results[0]['when'])
        self.assertEqual('127.0.0.1', results[0]['who'])
        self.assertEqual('Foo', results[0]['message'])

    def test_apache_ignore_200(self):
        line = '127.0.0.1 - - [03/Aug/2014:22:22:56 +0100] "GET / HTTP/1.1" 200 1140 "-" "-"'
        self.assertEqual(0, len(list(check_log_file(StringIO(line), ['500']))))

    def test_apache_500(self):
        line = '127.0.0.1 - - [03/Aug/2014:22:22:56 +0100] "GET / HTTP/1.1" 500 1140 "-" "-"'
        results = list(check_log_file(StringIO(line), ['500']))
        self.assertEqual(1, len(results))
        self.assertEqual(datetime.datetime(2014, 8, 3, 22, 22, 56), results[0]['when'])
        self.assertEqual('127.0.0.1', results[0]['who'])
        self.assertEqual('GET / HTTP/1.1', results[0]['message'])
