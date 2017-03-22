import xml.etree.ElementTree as ET
import hashlib

first = {}  # RS_ViaOW.xml
result = {}  # Result

def compare(obj, hash, key, value):
    obj['__hash__'] += hash
    obj['__values__'][key] = value

    global first
    if first.get(hash, False):
        obj['__values_mutated__'][key] = False
    else:
        obj['__is_changed__'] = True
        obj['__values_mutated__'][key] = True

    return obj


def iter(filename, is_first):
    tree = ET.parse(filename)
    root = tree.getroot()

    for i, flights in enumerate(root.find('PricedItineraries')):
        flight_wrapper = {}

        if not is_first:
            flight_wrapper['__is_changed__'] = False
            flight_wrapper['__hash__'] = ''
            flight_wrapper['__values_mutated__'] = {}
            flight_wrapper['__values__'] = {}

        if flights.find('OnwardPricedItinerary'):
            for j, _flights in enumerate(flights.find('OnwardPricedItinerary')):
                for k, flight in enumerate(_flights):
                    # flight_wrapper['flight'] = flight

                    for property in flight:
                        # make hash address to have quick access to this property and compare
                        key = str(i) + ':' + str(j) + ':' + str(k) + ':' + str(property.tag) + str(property.text)
                        hash = hashlib.sha1(key.encode('utf-8')).hexdigest()

                        if (is_first):
                            # if this is the first iteration, push every property into `first` key:value store
                            global first
                            first[hash] = True
                        else:
                            flight_wrapper = compare(flight_wrapper, hash, str(property.tag), property.text)

        if flights.find('ReturnPricedItinerary'):
            for j, _flights in enumerate(flights.find('ReturnPricedItinerary')):
                for k, flight in enumerate(_flights):

                    for property in flight:
                        # make hash address to have quick access to this property and compare
                        key = str(i) + ':' + str(j) + ':' + str(k) + ':' + str(property.tag) + str(property.text)
                        hash = hashlib.sha1(key.encode('utf-8')).hexdigest()

                        if (is_first):
                            # if this is the first iteration, push every property into `first` key:value store
                            global first
                            first[hash] = True
                        else:
                            flight_wrapper = compare(flight_wrapper, hash, str(property.tag), property.text)

        if flights.find('Pricing'):
            for j, service_charges in enumerate(flights.find('Pricing')):
                item_key = service_charges.attrib['ChargeType'] + ':' + service_charges.attrib['type']

                key = str(i) + str(j) + item_key
                hash = hashlib.sha1(key.encode('utf-8')).hexdigest()

                if is_first:
                    global first
                    first[hash] = True
                else:
                    flight_wrapper = compare(flight_wrapper, hash, item_key, service_charges.text)

        if not is_first and flight_wrapper['__is_changed__']:
            flight_wrapper['__hash__'] = hashlib.sha1(flight_wrapper['__hash__'].encode('utf-8')).hexdigest()
            result[flight_wrapper['__hash__']] = flight_wrapper


iter('RS_ViaOW.xml', True)
iter('RS_Via-3.xml', False)


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# здесь я уже сильно устал и написал не самую гибкую функцию, знаю =), на один раз пойдет, если бы я
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
            curr += len(text2.replace(bcolors.OKGREEN, '').replace(bcolors.ENDC, '')[:50 - (len(bcolors.ENDC * 2)) - 1])
        elif text1 or text2:
            res += ' '
            curr += 1
        else:
            res += '-'
            curr += 1

    print(res)


for hash, flight in result.items():
    print('\n')
    print_row('', '')
    print_row('Property', 'Value')
    print_row('', '')

    for key, value in flight['__values__'].items():
        if flight['__values_mutated__'][key]:
            if value:
                print_row(key.lstrip(), bcolors.OKGREEN + value.lstrip() + bcolors.ENDC)
                print_row('', '')
        else:
            if value:
                print_row(key.lstrip(), value.lstrip())
                print_row('', '')
