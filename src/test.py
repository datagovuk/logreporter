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

    def test_fetch_error_multiline(self):
        lines = '''
2015-04-14 15:00:05,130 DEBUG [ckanext.spatial.harvesters] WMS check url: http://spatial.durham.gov.uk/arcgis/services/INSPIRE/I100/MapServer/WMSServer?request=GetCapabilities&service=wms&version=1.3
2015-04-14 15:00:15,208 ERROR [ckanext.spatial.harvesters] WMS check for http://spatial.durham.gov.uk/arcgis/services/INSPIRE/I100/MapServer/WMSServer?request=GetCapabilities&service=wms failed with uncaught exception: timed out
Traceback (most recent call last):
  File "/vagrant/src/ckanext-spatial/ckanext/spatial/harvesters.py", line 105, in _try_wms_url
    res = urllib2.urlopen(capabilities_url, None, 10)
  File "/usr/lib/python2.7/urllib2.py", line 126, in urlopen
    return _opener.open(url, data, timeout)
  File "/usr/lib/python2.7/urllib2.py", line 400, in open
    response = self._open(req, data)
  File "/usr/lib/python2.7/urllib2.py", line 418, in _open
    data = self._sock.recv(self._rbufsize)
timeout: timed out
2015-04-14 15:00:15,209 DEBUG [ckanext.spatial.harvesters] WMS check url: http://spatial.durham.gov.uk/arcgis/services/INSPIRE/I100/MapServer/WMSServer?request=GetCapabilities&service=wms&version=1.1.1
'''
        results = list(check_log_file(StringIO(lines), ['ERROR']))
        self.assertEqual(1, len(results))
        self.assertEqual(results[0]['message'], "WMS check for http://spatial.durham.gov.uk/arcgis/services/INSPIRE/I100/MapServer/WMSServer?request=GetCapabilities&service=wms failed with uncaught exception: timed out")
        print results[0]['extra']
        expected = """Traceback (most recent call last):
  File "/vagrant/src/ckanext-spatial/ckanext/spatial/harvesters.py", line 105, in _try_wms_url
    res = urllib2.urlopen(capabilities_url, None, 10)
  File "/usr/lib/python2.7/urllib2.py", line 126, in urlopen
    return _opener.open(url, data, timeout)
  File "/usr/lib/python2.7/urllib2.py", line 400, in open
    response = self._open(req, data)
  File "/usr/lib/python2.7/urllib2.py", line 418, in _open
    data = self._sock.recv(self._rbufsize)
timeout: timed out
"""
        self.assertEqual(results[0]['extra'], expected)

    def test_apache_error_multiline(self):
        lines = '''
[Sat Sep 28 10:50:14 2013] [error] [client 81.102.118.195] mod_wsgi (pid=16242): Target WSGI script '/var/ckan/wsgi_app.py' cannot be loaded as Python module.
[Sat Sep 28 10:50:14 2013] [error] [client 81.102.118.195] mod_wsgi (pid=16242): Exception occurred processing WSGI script '/var/ckan/wsgi_app.py'.
[Sat Sep 28 10:50:14 2013] [error] [client 81.102.118.195] Traceback (most recent call last):
[Sat Sep 28 10:50:14 2013] [error] [client 81.102.118.195]   File "/var/ckan/wsgi_app.py", line 8, in <module>
[Sat Sep 28 10:50:14 2013] [error] [client 81.102.118.195]     fileConfig(config_filepath)
[Sat Sep 28 10:50:14 2013] [error] [client 81.102.118.195]   File "/home/co/ckan/lib/python2.7/site-packages/paste/script/util/logging_config.py", line 85, in fileConfig
[Sat Sep 28 10:50:14 2013] [error] [client 81.102.118.195]     handlers = _install_handlers(cp, formatters)
[Sat Sep 28 10:50:14 2013] [error] [client 81.102.118.195]   File "/home/co/ckan/lib/python2.7/site-packages/paste/script/util/logging_config.py", line 158, in _install_handlers
[Sat Sep 28 10:50:14 2013] [error] [client 81.102.118.195]     h = apply(klass, args)
[Sat Sep 28 10:50:14 2013] [error] [client 81.102.118.195]   File "/usr/lib/python2.7/logging/handlers.py", line 118, in __init__
[Sat Sep 28 10:50:14 2013] [error] [client 81.102.118.195]     BaseRotatingHandler.__init__(self, filename, mode, encoding, delay)
[Sat Sep 28 10:50:14 2013] [error] [client 81.102.118.195]   File "/usr/lib/python2.7/logging/handlers.py", line 65, in __init__
[Sat Sep 28 10:50:14 2013] [error] [client 81.102.118.195]     logging.FileHandler.__init__(self, filename, mode, encoding, delay)
[Sat Sep 28 10:50:14 2013] [error] [client 81.102.118.195]   File "/usr/lib/python2.7/logging/__init__.py", line 897, in __init__
[Sat Sep 28 10:50:14 2013] [error] [client 81.102.118.195]     StreamHandler.__init__(self, self._open())
[Sat Sep 28 10:50:14 2013] [error] [client 81.102.118.195]   File "/usr/lib/python2.7/logging/__init__.py", line 916, in _open
[Sat Sep 28 10:50:14 2013] [error] [client 81.102.118.195]     stream = open(self.baseFilename, self.mode)
[Sat Sep 28 10:50:14 2013] [error] [client 81.102.118.195] IOError: [Errno 13] Permission denied: '/var/log/ckan/ckan.log'
[Sat Sep 28 10:53:31 2013] [error] 2013-09-28 10:53:31,358 WARNI [ckan.plugins.core] Plugin '<class 'ckanext.qa.plugin.QAPlugin'>' is using deprecated interface IGenshiStreamFilter
[Sat Sep 28 10:53:31 2013] [error] 2013-09-28 10:53:31,580 DEBUG [ckanext.spatial.model.package_extent] Spatial tables defined in memory'''
        results = list(check_log_file(StringIO(lines), ['error']))
        self.assertEqual(1, len(results))
        self.assertEqual(results[0]['message'], "mod_wsgi (pid=16242): Target WSGI script '/var/ckan/wsgi_app.py' cannot be loaded as Python module.")
        print results[0]['extra']
        expected = """mod_wsgi (pid=16242): Exception occurred processing WSGI script '/var/ckan/wsgi_app.py'.
Traceback (most recent call last):
  File "/var/ckan/wsgi_app.py", line 8, in <module>
    fileConfig(config_filepath)
  File "/home/co/ckan/lib/python2.7/site-packages/paste/script/util/logging_config.py", line 85, in fileConfig
    handlers = _install_handlers(cp, formatters)
  File "/home/co/ckan/lib/python2.7/site-packages/paste/script/util/logging_config.py", line 158, in _install_handlers
    h = apply(klass, args)
  File "/usr/lib/python2.7/logging/handlers.py", line 118, in __init__
    BaseRotatingHandler.__init__(self, filename, mode, encoding, delay)
  File "/usr/lib/python2.7/logging/handlers.py", line 65, in __init__
    logging.FileHandler.__init__(self, filename, mode, encoding, delay)
  File "/usr/lib/python2.7/logging/__init__.py", line 897, in __init__
    StreamHandler.__init__(self, self._open())
  File "/usr/lib/python2.7/logging/__init__.py", line 916, in _open
    stream = open(self.baseFilename, self.mode)
IOError: [Errno 13] Permission denied: '/var/log/ckan/ckan.log'
"""
        self.assertEqual(results[0]['extra'], expected)
