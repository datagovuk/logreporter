from nose.tools import assert_equal

import reporter as r

apache_custom_line = '54.220.230.147 - - [14/Apr/2015:17:37:05 +0100] "GET /csw?request=GetRecordById&service=CSW&version=2.0.2&outputSchema=http%3A%2F%2Fwww.isotc211.org%2F2005%2Fgmd&elementSetName=full&id=13e23dc9-4e44-3f3e-8eb2-0e3d8461da9b HTTP/1.1" 200 17390 "-" "Jakarta Commons-HttpClient/3.0.1"'
apache_error_line = '[Sat Sep 28 10:50:14 2013] [error] [client 81.102.118.195] Traceback (most recent call last):'
#apache_error_line = '[Sat Sep 28 16:38:28 2013] [error] 2013-09-28 16:38:28,187 ERROR [root] Could not find resource 8e344515-bc90-4bd1-823d-554c92a19651'
ckan_line = 'Nov 10 07:57:52 co-prod3 2014-11-10 07:57:52,860 ERROR [ckan.controllers.api] Bad request data: No request body data'
celeryd_line = '[2015-04-13 12:20:10,743: ERROR/PoolWorker-72] archiver.update[archaeological-notification-areas-anas-for-east-sussex-and-brighton-and-hove2/ecca/cc21]: Error occurred during archiving resource: taxonomy'
fetch_line = '2015-04-13 14:31:02,201 INFO  [ckanext.spatial.validation.validation] Validation passed'
gather_line = '2014-09-19 11:12:14,286 DEBUG [ckanext.harvest.queue] Sent object 28d1b746-6f3c-4244-95b5-358b4f48331f to the fetch queue'
syslog_line_cron = 'Apr 17 05:30:01 co-prod3 CRON[4754]: (www-data) CMD ( /home/co/ckan/bin/paster --plugin=ckanext-harvest harvester run --config=/var/ckan/ckan.ini)'
syslog_line_ckan = 'Aug  6 05:27:33 co-prod3 2014-08-06 05:27:33,370 ERROR [ckan.lib.base] Foo'

def _match(line):
    return (r.line_matcher.match(line) or
            r.syslog_matcher.match(line) or
            r.apache_error_matcher.match(line) or
            r.apache_matcher.match(line) or
            r.celeryd_matcher.match(line))

def test_match_apache_custom():
    res = _match(apache_custom_line)
    expected = {'date': '14/Apr/2015:17:37:05 +0100', 'status': '200', 'message': 'GET /csw?request=GetRecordById&service=CSW&version=2.0.2&outputSchema=http%3A%2F%2Fwww.isotc211.org%2F2005%2Fgmd&elementSetName=full&id=13e23dc9-4e44-3f3e-8eb2-0e3d8461da9b HTTP/1.1', 'who': '54.220.230.147'}
    assert_equal(expected, res.groupdict())

def test_match_apache_error():
    res = _match(apache_error_line)
    expected = {'date': 'Sat Sep 28 10:50:14 2013', 'status': 'error', 'message': 'Traceback (most recent call last):', 'who': '81.102.118.195'}
    assert_equal(expected, res.groupdict())

def test_match_ckan():
    res = _match(ckan_line)
    expected = {'date': '2014-11-10 07:57:52', 'status': 'ERROR', 'message': 'Bad request data: No request body data', 'who': 'ckan.controllers.api'}
    assert_equal(expected, res.groupdict())

def test_match_celeryd():
    res = _match(celeryd_line)
    expected = {'date': '2015-04-13 12:20:10', 'message': 'Error occurred during archiving resource: taxonomy', 'who': 'archiver.update[archaeological-notification-areas-anas-for-east-sussex-and-brighton-and-hove2/ecca/cc21]', 'status': 'ERROR'}
    assert_equal(expected, res.groupdict())

def test_match_fetch():
    res = _match(fetch_line)
    expected = {'date': '2015-04-13 14:31:02', 'status': 'INFO', 'message': 'Validation passed', 'who': 'ckanext.spatial.validation.validation'}
    assert_equal(expected, res.groupdict())

def test_match_gather():
    res = _match(gather_line)
    expected = {'date': '2014-09-19 11:12:14', 'status': 'DEBUG', 'message': 'Sent object 28d1b746-6f3c-4244-95b5-358b4f48331f to the fetch queue', 'who': 'ckanext.harvest.queue'}
    assert_equal(expected, res.groupdict())

# not an error, so don't test
#def test_match_syslog_cron():
#    res = _match(syslog_line_cron)
#    expected = []
#    assert_equal(expected, res.groupdict())

def test_match_syslog_ckan():
    res = _match(syslog_line_ckan)
    expected = {'date': '2014-08-06 05:27:33', 'status': 'ERROR', 'message': 'Foo', 'who': 'ckan.lib.base'}
    assert_equal(expected, res.groupdict())
