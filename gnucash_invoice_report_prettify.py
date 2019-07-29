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
import pdfkit


def soup_rm_tr(soup, td_text, attrs={}):
    td = soup.find('td', text=td_text, attrs=attrs)
    if td:
        td.parent.extract()


def tweak_file(f, footer_text=None):
    soup = BeautifulSoup(f, features="html.parser")

    # Change the default footer from "Thank's for the patrionage!"
    if footer_text:
        div = soup.find(attrs={'class': 'invoice-notes'})
        div.string = footer_text

    # Remove tax fields:
    # 1. The row with the MVA
    soup_rm_tr(soup, 'MVA', attrs={'class': 'total-label-cell'})
    # Remove one of the total fields
    soup_rm_tr(soup, 'Total Price')
    soup_rm_tr(soup, 'Net Price')
    # Change language on last total field
    soup.find('td', text='Å betale').string = 'Totalt'

    # Remove the Terms element
    div = soup.find('div', attrs={'class': 'invoice-details-table'})
    for tr in div.find_all('tr'):
        if tr.find('td').text == 'Terms:':
            tr.extract()

    # Remove unnecessary columns:
    div = soup.find('div', attrs={'class': 'entries-table'})
    to_remove = []
    for i, th in enumerate(div.find_all('th')):
        if th.text in ('Handling', 'Antall', 'Stykkpris', 'Rabatt',
                       'MVA-pliktig', 'Totalt'):
            to_remove.append(i)
            th.extract()

    tbody = div.find('tbody')
    for tr in tbody.find_all('tr'):
        tds = tr.find_all('td')
        if tds[0].text == 'Totalt':
            break
        for i in to_remove:
            tds[i].extract()

    # TODO: more text to translate? Then I hopefully don't have to starta
    # gnucash per language

    # Fix CSS:
    soup.html.style.string = '''
        table { width: 100% }
        .main-table { margin-top: 5em }
        .main-table > table > tbody > tr > td { padding-top: 2em }
        .client-table { margin-top: 5em }
        ''' + soup.html.style.string
    return soup


def main():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
            '--footer', default='Med venleg helsing Bryggekomitéen',
            help="The footer text, instead of 'Thanks for the patrionage'. "
                 "Default: '%(default)s'"
            )
    parser.add_argument(
            '--format', choices=('pdf', 'html'), default='pdf',
            help="What format to export to. Default: %(default)s"
            )
    parser.add_argument(
            'files', nargs='+', type=argparse.FileType('r'),
            help="Report files, as exported as HTML from inside GnuCash"
            )

    args = parser.parse_args()

    i = 0
    for f in args.files:
        soup = tweak_file(f, footer_text=args.footer)
        outname = '{}.clean.html'.format(f.name)
        if args.format == 'html':
            out = open(outname, 'w')
            out.write(soup.prettify())
            out.close()
            print("Wrote {} to {}".format(os.path.basename(f.name),
                                          os.path.basename(outname)))
        elif args.format == 'pdf':
            pdfkit.from_string(str(soup), f.name + '.pdf')
        i += 1
    print("{} files tweaked".format(i))


if __name__ == '__main__':
    main()
