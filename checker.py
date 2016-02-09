import logging
import os
import StringIO
import xml.sax

import requests

logging.basicConfig(
    format='[%(asctime)s] [%(process)d] [%(name)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S +0000', level=logging.DEBUG
    )
logger = logging.getLogger(__name__)

_REQUIRED_OPTS = ['WATCHES_URL', 'EVECENTRAL_URL', 'SYSTEM_ID', 'PRICES_URL']


def system_id():
    return os.environ.get('SYSTEM_ID')


class EveCentralMarketStatHandler(xml.sax.ContentHandler):
    def __init__(self):
        # Initialize the flag to false
        self.mode = None
        self.capturing = None
        self.data = {'buy': {}, 'sell': {}, 'system_id': system_id()}

    def startElement(self, name, attrs):
        if name in ['buy', 'sell']:
            self.mode = name
        if self.mode and name in ['min', 'max', 'avg', 'median', 'stddev']:
            self.capturing = name
            self.data[self.mode][name] = ''

    def endElement(self, name):
        if name in ['buy', 'sell']:
            self.mode = None
        if self.mode and name in ['min', 'max', 'avg', 'median', 'stddev']:
            self.capturing = None

    def characters(self, content):
        if self.mode and self.capturing:
            partial = self.data[self.mode][self.capturing]
            self.data[self.mode][self.capturing] = partial + content

    def data(self):
        return self.data


def verify_parameters():
    missing = [n for n in _REQUIRED_OPTS if not os.environ.get(n, None)]
    if len(missing) > 0:
        logging.critical('Missing options in environment: %s' % missing)
        exit(1)


def watched_ids():
    try:
        wurl = os.environ.get('WATCHES_URL')
        w = requests.get(url=wurl)
    except Exception as e:
        logger.exception(e)
        exit(1)
    return [watched['id'] for watched in w.json()]


def record_price(by_id, payload):
    try:
        purl = '/'.join([os.environ.get('PRICES_URL'), str(by_id)])
        logger.info('recording price')
        requests.post(url=purl, json=payload)
    except Exception as e:
        logger.exception(e)
        exit(1)


def translate(content):
    try:
        parser = xml.sax.make_parser()
        handler = EveCentralMarketStatHandler()
        parser.setContentHandler(handler)
        source = StringIO.StringIO(content)
        logger.info('translating price')
        parser.parse(source)
        payload = handler.data
    except Exception as e:
        logger.exception(e)
        exit(1)
    return payload


def fetch_price(by_id):
    try:
        params = {'typeid': by_id, 'usesystem': system_id()}
        ecurl = os.environ.get('EVECENTRAL_URL')
        logger.info('fetching price')
        ec_body = requests.get(url=ecurl, params=params).content
    except Exception as e:
        logger.exception(e)
        exit(1)
    return ec_body


def main():
    verify_parameters()

    for by_id in watched_ids():
        logger.info('checking price for type_id %s', by_id)
        ec_body = fetch_price(by_id)
        payload = translate(ec_body)
        record_price(by_id, payload)

if __name__ == "__main__":
    main()