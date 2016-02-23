#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys
import argparse
import subprocess
import urllib2
from lxml import html


def main(argv=None):
    """
    Main routine which is not called, if this module is loaded via `import`.

    Arguments:
    - `argv`: Command line arguments passed to the script.
    """
    parser = argparse.ArgumentParser(description='Get your publication list.')
    parser.add_argument(dest='authors', metavar='AUTHORS', nargs='+',
                        help=("Name of the author(s) for which a publication "
                              "list shall be generated. At least one name must "
                              "be provided."))
    args = parser.parse_args(sys.argv[1:])

    authors = [re.sub(r"\s+", '+', author.strip()) for author in args.authors]
    jump_size = 250

    url = ("http://inspirehep.net/search?ln=en&ln=en&"
           "jrec={{begin:d}}&"
           "p=f+a+{authors:s}&"
           "rg={jump:d}&"
           "of=hx&action_search=Search&sf=earliestdate&so=d&rm=&sc=0")
    url = url.format(authors = "+or+a+".join(authors), jump = jump_size)

    entries = []
    jump = 1
    while True:
        request = urllib2.urlopen(url.format(begin = jump)).read()
        tree = html.fromstring(request)
        next_entries = tree.xpath('//pre/text()')
        if len(next_entries) == 0: break
        entries.extend(next_entries)
        jump += jump_size

    pub_list = "publication-list"
    with open(pub_list+".bib", "w") as bib:
        map(lambda x: bib.write(x.encode("utf-8").strip()+"\n\n"), entries)

    generate_pub_list(pub_list)
    generate_pub_list("important-publications")
    merge_pub_lists("important-publications", pub_list)
    clean_up()


def generate_pub_list(name):
    """
    Creates pdf containing the publications attached to `name`.

    Arguments:
    - `name`: ID to create the publication list
    """

    subprocess.call(["pdflatex", name+".tex"])
    subprocess.call(["bibtex",   name+".aux"])
    subprocess.call(["pdflatex", name+".tex"])
    subprocess.call(["pdflatex", name+".tex"])


def merge_pub_lists(*id_list):
    """
    Merges pdf files indicated by the list of basenames in `id_list`.

    Arguments:
    - `id_list`: list of basenames to merge
    """

    cmd = ["pdftk"]
    cmd.extend([base+".pdf" for base in id_list])
    cmd.extend(["output", "publications.pdf"])
    subprocess.call(cmd)


def clean_up():
    """
    Remove temporary files.
    """
    
    subprocess.call("rm -f *.aux *.bbl *.blg *.log *.out *~", shell = True)



################################################################################
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
