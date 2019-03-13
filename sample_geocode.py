import time
import prettyprinter

from geode.dispatcher import Dispatcher

prettyprinter.install_extras(include=['dataclasses'])


def main():
    client = Dispatcher()

    s = time.time()
    res = client.geocode(
        '500 Rutherford Ave, Charlestown MA',
        provider='google'
    )

    t = time.time() - s
    prettyprinter.pprint(res)
    print('Duration: %dms' % (t * 1000))


if __name__ == '__main__':
    main()
