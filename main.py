#
# POLYGLOT
# 
# an interactive "advisor" for selecting the optimal programming
# language learning path, based on a variety of factors
# 

import re

import requests
from bs4 import BeautifulSoup

# types of programming paradigms
PARADIGMS = ['imperative', 'object-oriented', 'functional', 'procedural',
             'generic', 'reflective', 'event-driven']

# helper functions #
def is_footnote(s):
    '''
    given an input string, determines if it's a footnote or not
    '''

    return '[' in s and ']' in s

def row_to_set(row):
    '''
    given a row extracted from the parse tree, this function returns a pair
    containing the name of the associated programming language & a set of
    distinctive features (e.g. paradigm, use cases, etc.)
    '''
    
    # extract name of programming language
    name = ''.join(list(row.th.strings))

    # extract each (data) column from the given row
    cols = row.find_all('td')

    # set of "domains/use cases" for this language (filter out any "footnotes")
    domains = list(filter(lambda s: not is_footnote(s), cols[0].strings))
    domains = ''.join(domains).split(', ')
    domains = set(map(lambda s: s.lower(), domains))

    # set of "paradigms" used by this language
    paradigms = set()

    for i in range(1, len(PARADIGMS) + 1):

        if 'Yes' in cols[i].text:

            paradigms.add(PARADIGMS[i - 1])

    # set of "other paradigm(s)" for this language (filter out any "footnotes")
    other_paradigms = list(filter(lambda s: not is_footnote(s),
                                  cols[len(PARADIGMS) + 1].strings))
    other_paradigms = ''.join(other_paradigms).split(', ')
    other_paradigms = set(map(lambda s: s.lower(), other_paradigms))

    # construct the final set of language features
    features = domains | paradigms | other_paradigms
    
    return (name, features)

# retrieve "programming language comparison" table from Wikipedia
r = requests.get('https://en.wikipedia.org/wiki/Comparison_of_programming_languages')

# construct parse tree based on Wikipedia page
soup = BeautifulSoup(r.text, 'html.parser')

# extract the (name, features) representation for each programming language
all_rows = soup.find('table', class_='wikitable').find_all('tr')[1:-1]
