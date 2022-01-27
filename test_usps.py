#!/usr/bin/python

"""
Copyright

The information contained herein is confidential property of Vecima Networks
Inc. The use, copying, transfer or disclosure of such information is prohibited
except by express written agreement with Vecima Networks Inc.
"""

import csv
import shutil
from tempfile import NamedTemporaryFile

import requests
from lxml import etree

USERID = '741VECIM1509'
INPUT_FILE = 'Python Quiz Input - Sheet1.csv'

BASE_URL = 'https://secure.shippingapis.com/ShippingAPI.dll?API='
VALIDATION_URL = 'Verify&XML={}'

KEY_MAPPING = {
    'Company' : 'FirmName',
    'Street' : 'Address1',
    'City'  : 'City',
    'St' : 'State',
    'ZIPCode' : 'Zip5',
}

def validate_address(addr_info):
    '''
    Construct the xml string for validation.

    Args:
        addr_info (dict): extracted line from the csv file in the dict format

    Returns:
        bool: True if the address is valid, otherwise False
    '''
    xml = etree.Element('AddressValidateRequest', {'USERID': USERID})
    xml_address = etree.SubElement(xml, 'Address', {'ID': '0'})

    for tag, value in addr_info.items():
        etree.SubElement(xml_address, KEY_MAPPING[tag]).text = value
        if 'Address1' in tag:
            etree.SubElement(xml_address, 'Address2').text = ''
        elif 'Zip5' in tag:
            etree.SubElement(xml_address, 'Zip4').text = ''

    xml = etree.tostring(xml, encoding='iso-8859-1', pretty_print=True).decode()
    url = BASE_URL + VALIDATION_URL.format(xml)

    xml_response = requests.get(url).content.decode('iso-8859-1')

    if 'Error' in xml_response:
        return False
    return True

def main():
    '''
    Go through the input csv file line by line to extract info and construct the xml for
    the validation, and append the result of validation into new file.
    '''
    try:
        tempfile = NamedTemporaryFile(mode='w', delete=False)

        with open(INPUT_FILE, 'r') as csv_file, tempfile:

            header_exit = False
            for row in csv.DictReader(csv_file):

                result = validate_address(row)
                row.update({'Valid' : result})

                # generate new header to append the column for address validation result,
                # and only run once
                if not header_exit:
                    writer = csv.DictWriter(tempfile, fieldnames=list(row.keys()))
                    writer.writeheader()
                    header_exit = True

                writer.writerow(row)

        shutil.move(tempfile.name, INPUT_FILE)

    except Exception as err:
        print(f"Exception is {err}")

if __name__ == "__main__":
    main()
