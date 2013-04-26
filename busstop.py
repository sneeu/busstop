from gevent.pywsgi import WSGIServer
from lxml import etree
import requests


BASE_URL = (
    'http://old.mybustracker.co.uk/getBusStopDepartures.php'
    '?refreshCount=0&clientType=b&busStopCode=%s&busStopDay=0&busStopService=0'
    '&numberOfPassage=2&busStopTime=&busStopDestination=0')


def fetch_feed(bus_stop_code):
    response = requests.post(BASE_URL % (bus_stop_code, ))
    return response.text


def parse_feed_data(feed_data):
    cleaned_data = feed_data\
        .replace('<?xml version="1.0" encoding="iso-8859-1"?>', '')\
        .replace('xmlns', 'xmlnamespace')
    root = etree.fromstring(cleaned_data)

    arrivals = []

    for row in root.findall('.//pre'):
        text = ''.join(row.xpath("./text()"))
        line = text.strip().split()
        service, time = line[0], line[-1]
        if time == 'DUE':
            time = '00'
        if len(time) == 1:
            time = '0' + time
        arrivals.append((service, time, ))

    return arrivals


def time_comparator(a, b):
    a = a.strip('*')
    b = b.strip('*')
    if ':' in a and ':' in b:
        return cmp(a, b)
    if ':' in a:
        return 1
    if ':' in b:
        return -1
    return cmp(a, b)


def format_arrivals(arrivals):
    r = []
    if arrivals:
        r.append('Serv,Time')

    for serv, time in sorted(
            arrivals, cmp=lambda a, b: time_comparator(a[1], b[1])):
        if ':' not in time:
            if time == '00':
                time = 'Due'
            else:
                time += 'mins'
        r.append(','.join([serv, time]))
    return '\n'.join(r)


def application(environ, start_response):
    status = '200 OK'

    headers = [
        ('Content-Type', 'text/html')
    ]

    start_response(status, headers)
    yield format_arrivals(
        #[('14', 7), ('7', 0), ('7', 12)])
        parse_feed_data(
            fetch_feed(
                environ.get('PATH_INFO').strip('/'))))


if __name__ == '__main__':
    server = WSGIServer(('', 8000, ), application)
    server.serve_forever()
