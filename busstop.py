import requests
from lxml import etree


BASE_URL = 'http://www.mybustracker.co.uk/update.php?module=BTTimeConsult&updateId=timesResult'


BASE_DATA = {
    'mode': 1,
    'openMap': 0,
    'refresh': 1,
    'autoRefreshCheck': '',
    'fullCheck': '',
    'busStopDay': 0,
    'journeyId': '',
    'journeyTimesDetails': '',
    'busStopService': 0,
    'busStopDest': 0,
    'nbDeparture': 2,
    'busStopTime':  '',
}


BASE_HEADERS = {
    'Cookie': 'PHPSESSID=qo4p3id2fapnfcemfut2jbqr74',
}


def fetch_feed(bus_stop_code):
    data = BASE_DATA
    data['busStopCode'] = bus_stop_code

    return requests.post(BASE_URL, data=data, headers=BASE_HEADERS).text


def parse_feed(feed_data):
    feed_data = feed_data.replace('<?xml version="1.0" encoding="UTF-8" ?>', '')
    outer_root = etree.fromstring(feed_data)
    root = etree.fromstring(outer_root.find('updateElement').text)

    arrivals = []

    for row in root.findall('.//tr'):
        if len(row) == 3:
            service = row[0].text
            service_due = row[2][0].text.strip()

            arrivals.append((service, service_due, ))

    return arrivals


def main():
    print parse_feed(fetch_feed(36232324))


if __name__ == '__main__':
    main()
