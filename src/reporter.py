import re
import datetime
from dateutil import parser as date_parser


fetch_gather_matcher = re.compile("^(?P<date>\d+-\d+-\d+ \d+:\d+:\d+),\d+ (?P<status>\w+)\s*\[(?P<who>.*)\] (?P<message>.*)")
syslog_and_ckan_matcher = re.compile("^\w+\s{1,2}\d+ \d+:\d+:\d+ .* (?P<date>\d+-\d+-\d+ \d+:\d+:\d+),\d+ (?P<status>\w+)\s*\[(?P<who>.*)\] (?P<message>.*)")
apache_error_re = "\[(?P<date>\w{3} \w{3} \d+ \d+:\d+:\d+ \d{4})\] \[(?P<status>error)\] \[client (?P<who>\d+\.\d+\.\d+\.\d+)\] (?P<message>.*)"
apache_error_matcher = re.compile(apache_error_re)
apache_matcher = re.compile("(?P<who>\d+\.\d+\.\d+.\d+) - - \[(?P<date>.*)\] \"(?P<message>.*)\" (?P<status>\d{3}) \d+ \".*\" \".*\"")
celeryd_matcher = re.compile("^\[(?P<date>\d+-\d+-\d+ \d+:\d+:\d+),\d+: (?P<status>\w+).*\] (?P<who>[^:]+): (?P<message>.*)")
all_matchers = (fetch_gather_matcher, syslog_and_ckan_matcher,
                apache_error_matcher, apache_matcher, celeryd_matcher)

def load_data(datadict):
    data = {"extra": ""}
    data['when'] = date_parser.parse(datadict.get('date'), fuzzy=True, ignoretz=True)
    data['level'] = datadict.get('status')
    data['who'] = datadict.get('who', '')
    data['message'] = datadict.get('message', '')
    data['appeared'] = 1
    return data

def check_log_file(f, matches=("ERROR", "error", "500")):
    """ Loops through the file and checks each line for matches that we
        may be interested in and yields them to the caller """
    matcher = None
    last = None
    while True:
        line = f.readline()
        if not line:
            break

        if matcher:
            m = matcher.match(line)
        else:
            for try_matcher in all_matchers:
                m = try_matcher.match(line)
                if m:
                    matcher = try_matcher
                    break

        # work out how the line relates to log messages (potentially multiline)
        if matcher == apache_error_matcher and last:
            # Apache error file is different to others because a multiline
            # error matches every line, so we group together lines to the
            # same person as one error.
            if m and m.groupdict()['who'] == last['who']:
                # same person, so assume it is same message
                line_type = 'append to message'
                # apache has all the headers, but we can strip them off
                msg = m.groupdict()['message'] + '\n'
            else:
                # different person, so assume it is the end of the message
                if m:
                    line_type = 'new message'
                else:
                    line_type = 'not part of message'
        else:
            if m:
                if m.groupdict()['status'] in matches:
                    line_type = 'new message'
                else:
                    line_type = 'not part of message'
            else:
                line_type = 'append to message'
                msg = line

        if line_type == 'new message':
            if last:
                yield last
            last = load_data(m.groupdict())
        elif line_type in 'append to message':
            if not last:
                continue
            last['extra'] = last.get("extra", "") + msg
        elif line_type in 'not part of message':
            if last:
                yield last
                last = None
    if last:
        yield last


def filter_date(hours, now=datetime.datetime.now()):
    """ Returns a function (using the allowed date as a closure) suitable for
        use by filter() or ifilter() """
    allowed = now - datetime.timedelta(hours=hours if hours > 0 else 100000)
    def _filter(element):
        return element['when'] >= allowed
    return _filter
