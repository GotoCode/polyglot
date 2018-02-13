#
# POLYGLOT
# 
# an interactive "advisor" for selecting the optimal programming
# language learning path, based on a variety of factors
# 

import re
import sys

import requests
from bs4 import BeautifulSoup

from max_heap import MaxHeap

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

def feature_diff(reference_set, other_set):
    '''
    given a reference and comparison set, this function computes
    a 'distance metric' between the two sets of features
    '''

    return len(other_set ^ reference_set)

def get_lang_info(rows, tiobe_only=False):
    '''
    given a list of rows (BS4 Tag objects) in the Wikipedia languages table,
    this function returns a dictionary mapping each programming language to
    a set of key features of that langauge (e.g. paradigm, use cases, etc.)

    if the tiobe_only flag is set, this function only returns information for
    languages which are contained in the top-50 list on the TIOBE index 
    '''

    tiobe_set = set()

    # extract set of top-50 programming languages on TIOBE index
    if tiobe_only:

        # retrieve TIOBE list and construct parse tree
        r = requests.get('https://www.tiobe.com/tiobe-index/')
        s = BeautifulSoup(r.text, 'html.parser')

        # retrieve all tables in webpage
        tables = s.find_all('table')

        top_20_rows = tables[0].tbody.find_all('tr')
        bottom_30_rows = tables[1].tbody.find_all('tr')

        # process table of top-20 TIOBE languages
        for row in top_20_rows:

            name = str(row.find_all('td')[3].string)

            tiobe_set.add(name)

        # process table of bottom-30 TIOBE languages
        for row in bottom_30_rows:

            name = str(row.find_all('td')[1].string)

            tiobe_set.add(name)

    info = {}

    # construct final dictionary containing (name, features) pairs
    for n, f in map(row_to_set, rows):

        # add only TIOBE-listed languages, if the tiobe_only flag is set
        if tiobe_only:

            if n in tiobe_set:

                info[n] = f

        else:
            
            info[n] = f

    return info #{s[0] : s[1] for s in map(row_to_set, rows)}

def compute_scores(references, languages):
    '''
    given a reference language and a dictionary mapping each language to a
    list of langauge features (e.g. paradigm, domains, etc.), this function
    returns a MaxHeap object containing (score, language) pairs, where the
    score is computed using some kind of comparison function
    '''

    res = MaxHeap()

    # retrieve set of features for reference language
    ref_features = set()

    # update the set of reference features to
    # be the union of all known languages
    for lang in references:

        if lang in languages:

            f = languages[lang]
            
            ref_features.update(f)
    
    # compute "comparison score" for each programming language
    for name, features in languages.items():

        score = feature_diff(ref_features, features)

        res.push(score, name)

    return res

def print_scores(scores, limit=None, refs=[]):
    '''
    given a max-heap containing (score, language) pairs,
    this function prints out a list of suggested "learn next"
    languages, using the (optional) limit argument to limit results

    WARNING: this function modifies the passed-in scores max-heap
    '''

    limit = limit if (limit is not None) else 10

    print('\n-- suggested languages --\n')

    i = 0
    
    while i < limit:

        item = scores.pop()

        if item is None: break

        score, name = item

        if name in refs: continue

        #print('{N}. {L} ({S})'.format(N=i+1, L=name, S=score))
        print('- {}'.format(name))

        i += 1

    print()

# retrieve "programming language comparison" table from Wikipedia
r = requests.get('https://en.wikipedia.org/wiki/Comparison_of_programming_languages')

# construct parse tree based on Wikipedia page
soup = BeautifulSoup(r.text, 'html.parser')

# extract the (name, features) representation for each programming language
all_rows = soup.find('table', class_='wikitable').find_all('tr')[1:-1]

# convert the all_rows list into a dictionary mapping name to features
lang_info = get_lang_info(all_rows, tiobe_only=True)

# list of reference languages for feature comparisons
ref_langs = []

# prompt user to enter main reference language
main_lang = input('What is your primary programming language? ')

ref_langs.append(main_lang)

# prompt user to enter additional reference langauges, if possible
has_next = input('Do you know another language? ')

while 'yes' in has_next.lower():

    lang = input('What is this language called? ')

    ref_langs.append(lang)

    has_next = input('Do you know another language? ')

# create max-heap containing relative "comparison scores" between
# each stored language and the given reference languages
scores = compute_scores(ref_langs, lang_info)

# print out list of "Top 10" suggested languages 
print_scores(scores, limit=10, refs=ref_langs)
