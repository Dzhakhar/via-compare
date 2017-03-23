import xml.etree.ElementTree as ET
import hashlib
import json

first = {}
results = []


def compare_tickets(flights, nested_tag, i, is_first):
    for j, _flights in enumerate(flights.find(nested_tag)):
        # for <Flight/> in <Flights/>
        for k, flight in enumerate(_flights):
            payload = {}
            payload['updated'] = {}
            payload['properties'] = {}

            for property in flight:
                # make hash address to have quick access to this property and compare
                key = str(i) + ':' + str(j) + ':' + str(k) + ':' + str(property.tag) + str(property.text)
                hash = hashlib.sha1(key.encode('utf-8')).hexdigest()

                if is_first:
                    global first
                    first[hash] = True
                else:
                    payload['properties'][str(property.tag)] = property.text

                    if first.get(hash, False):
                        payload['updated'][str(property.tag)] = False
                    else:
                        payload['updated'][str(property.tag)] = True
                        results.append(payload)


def compare_pricing(flights, nested_tag, i, is_first):
    for j, service_charges in enumerate(flights.find('Pricing')):
        payload = {}
        payload['updated'] = {}
        payload['properties'] = {}
        item_key = service_charges.attrib['ChargeType'] + ':' + service_charges.attrib[
            'type'] + ':' + service_charges.text
        key = str(i) + str(j) + item_key
        hash = hashlib.sha1(key.encode('utf-8')).hexdigest()

        if is_first:
            global first
            first[hash] = True
        else:
            payload['properties'][item_key] = service_charges.text

            if first.get(hash, False):
                payload['updated'][item_key] = False
            else:
                payload['updated'][item_key] = True
                results.append(payload)


def iter(filename, is_first):
    tree = ET.parse(filename)
    root = tree.getroot()

    # for <Flights/> in <PricedItineraries>
    for i, flights in enumerate(root.find('PricedItineraries')):
        if flights.find('OnwardPricedItinerary'):
            compare_tickets(flights, 'OnwardPricedItinerary', i, is_first)

        if flights.find('ReturnPricedItinerary'):
            compare_tickets(flights, 'ReturnPricedItinerary', i, is_first)

        if flights.find('Pricing'):
            compare_pricing(flights, 'Pricing', i, is_first)


# colored output
# updated values are printed green
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# здесь я уже устал и написал не самую гибкую функцию, знаю =), на один раз пойдет, если бы я
# писал библиотеку или reusable функцию, то написал бы максимально гибко
# тут минимум конфигурируемости
def print_row(text1, text2):
    res = ''
    max_len = 106
    center = 40
    curr = 0

    for i in range(max_len):
        if curr == center or curr == 0 or curr == max_len - 1:
            res += '+'
            curr += 1
        elif text1 and curr == 3:
            res += text1[:50]
            curr += len(text1[:50])
        elif text2 and curr == center + 2:
            res += text2[:50 - len(bcolors.ENDC)] + bcolors.ENDC
            curr += len(
                text2.replace(bcolors.OKGREEN, '').replace(bcolors.ENDC, '')[:50 - (len(bcolors.ENDC * 2)) - 1])
        elif text1 or text2:
            res += ' '
            curr += 1
        else:
            res += '-'
            curr += 1

    print(res)


def render():
    # render output
    global results
    for flight in results:
        print('\n')
        print_row('', '')
        print_row('Property', 'Value')
        print_row('', '')

        for key, value in flight['properties'].items():
            if flight['updated'][key]:
                if value:
                    global bcolors
                    print_row(key.lstrip(), bcolors.OKGREEN + value.lstrip() + bcolors.ENDC)
                    print_row('', '')
            else:
                if value:
                    print_row(key.lstrip(), value.lstrip())
                    print_row('', '')


def run(old, new):
    iter(old, True)
    iter(new, False)
    render()


# run('RS_ViaOW.xml', 'RS_Via-3.xml')
run('OLD-fake-data.xml', 'NEW-fake-data.xml')

open('result.json', 'w').write(json.dumps(results))
