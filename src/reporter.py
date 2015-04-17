import re
import datetime
from dateutil import parser as date_parser


line_matcher = re.compile("^(?P<date>\d+-\d+-\d+ \d+:\d+:\d+),\d+ (?P<status>\w+)\s*\[(?P<who>.*)\] (?P<message>.*)")
syslog_matcher = re.compile("^\w+\s{1,2}\d+ \d+:\d+:\d+ .* (?P<date>\d+-\d+-\d+ \d+:\d+:\d+),\d+ (?P<status>\w+)\s*\[(?P<who>.*)\] (?P<message>.*)")
apache_error_matcher = re.compile("\[(?P<date>\w{3} \w{3} \d+ \d+:\d+:\d+ \d{4})\] \[(?P<status>error)\] \[client (?P<who>\d+\.\d+\.\d+\.\d+)\] (?P<message>.*)")
apache_matcher = re.compile("(?P<who>\d+\.\d+\.\d+.\d+) - - \[(?P<date>.*)\] \"(?P<message>.*)\" (?P<status>\d{3}) \d+ \".*\" \".*\"")
celeryd_matcher = re.compile("^\[(?P<date>\d+-\d+-\d+ \d+:\d+:\d+),\d+: (?P<status>\w+).*\] (?P<who>[^:]+): (?P<message>.*)")

def load_data(datadict):
    data = {"extra": ""}
    data['when'] = date_parser.parse(datadict.get('date'), fuzzy=True, ignoretz=True)
    data['level'] = datadict.get('status')
    data['who'] = datadict.get('who', '')
    data['message'] = datadict.get('message', '')
    data['appeared'] = 1
    return data

def check_log_file(f, matches=["ERROR", "error", "500"]):
    """ Loops through the file and checks each line for matches that we
        may be interested in and yields them to the caller """
    last = None
    while True:
        line = f.readline()
        if not line:
            break

        m = (line_matcher.match(line) or
             syslog_matcher.match(line) or
             apache_error_matcher.match(line) or
             apache_matcher.match(line) or
             celeryd_matcher.match(line))
        if m:
            if m.groupdict()['status'] in matches:
                if last:
                    yield last
                last = load_data(m.groupdict())
            elif last:
                yield last
                last = None
        else:
            # Not a match, but we potentially have a previous dict to add to
            if last:
                last['extra'] = last.get("extra","") + line
    if last:
        yield last

def filter_date(hours, now=datetime.datetime.now()):
    """ Returns a function (using the allowed date as a closure) suitable for
        use by filter() or ifilter() """
    allowed = now - datetime.timedelta(hours=hours if hours > 0 else 100000)
    def _filter(element):
        return element['when'] >= allowed
    return _filter
