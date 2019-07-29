#!/usr/bin/env python
# -*- encoding: utf8 -*-
"""Prettify HTML report files from gnucash

The default reports from gnucash contains a lot of unnecessary data, e.g. about
VAT. I want an easier report, to be more valid for an idealistic, Norwegian
organization.

Most of this could be changed inside gnucash, but it has to be changed at each
invoice, manually. Automating is good, but I don't know how to do it inside
GnuCash.

What it does:

- Strip away TAX fields
- Change CSS: full width
- Change default footer text

TODO:

- Convert end report to PDF

"""

import argparse
from bs4 import BeautifulSoup
import os


def tweak_file(f, footer_text=None):
    soup = BeautifulSoup(f, features="html.parser")

    # Change the default footer from "Thank's for the patrionage!"
    if footer_text:
        div = soup.find(attrs={'class': 'invoice-notes'})
        div.string = footer_text

    # Remove tax fields:
    # 1. The row with the MVA
    soup.find('td', text='MVA').parent.extract()
    # Remove one of the total fields
    soup.find('td', text='Total Price').parent.extract()
    # Change language on last total field
    soup.find('td', text='Å betale').string = 'Totalt'

    # TODO: more text to translate? Then I hopefully don't have to starta
    # gnucash per language

    # Fix CSS:
    soup.html.style.string = '\ntable { width: 100% }' + soup.html.style.string
    return soup


def main():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
            '--footer', default='Med venleg helsing Bryggekomitéen',
            help="The footer text, instead of 'Thanks for the patrionage'"
            )
    parser.add_argument(
            'files', nargs='+', type=argparse.FileType('r'),
            help="Report files, as exported as HTML from inside GnuCash"
            )

    args = parser.parse_args()

    i = 0
    for f in args.files:
        soup = tweak_file(f)
        outname = '{}.clean.html'.format(f.name)
        # TODO: Don't overwrite, for now!
        out = open(outname, 'w')
        out.write(soup.prettify())
        out.close()
        print("Wrote {} to {}".format(os.path.basename(f.name),
                                      os.path.basename(outname)))
        i += 1
    print("{} files tweaked".format(i))


if __name__ == '__main__':
    main()
