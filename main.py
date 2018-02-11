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
    
    NOTE: currently this function implements the set equivalent
          of the Hamming distance metric
    '''

    return len(reference_set ^ other_set)

def compute_scores(reference, languages):
    '''
    given a reference language and a dictionary mapping each language to a
    list of langauge features (e.g. paradigm, domains, etc.), this function
    returns a MaxHeap object containing (score, language) pairs, where the
    score is computed using some kind of comparison function
    '''

    res = MaxHeap()

    # reference langauge does not exist
    if reference not in languages:

        return MaxHeap()

    # retrieve set of features for reference language
    ref_features = languages[reference]

    # compute "comparison score" for each programming language
    for name, features in languages.items():

        score = feature_diff(ref_features, features)

        res.push(score, name)

    return res

def print_scores(scores, limit=None):
    '''
    given a max-heap containing (score, language) pairs,
    this function prints out a list of suggested "learn next"
    languages, using the (optional) limit argument to limit results

    WARNING: this function modifies the passed-in scores max-heap
    '''

    limit = limit if (limit is not None) else 10

    print('\n-- suggested languages --\n')
    
    for i in range(limit):

        item = scores.pop()

        if item is None: break

        score, name = item

        print('{N}. {L} ({S})'.format(N=i+1, L=name, S=score))

    print()

# retrieve "programming language comparison" table from Wikipedia
r = requests.get('https://en.wikipedia.org/wiki/Comparison_of_programming_languages')

# construct parse tree based on Wikipedia page
soup = BeautifulSoup(r.text, 'html.parser')

# extract the (name, features) representation for each programming language
all_rows = soup.find('table', class_='wikitable').find_all('tr')[1:-1]

# convert the all_rows list into a dictionary mapping name to features
lang_info = {s[0] : s[1] for s in map(row_to_set, all_rows)}

# prompt user to enter reference language for feature comparisons
ref_lang = input('What is your primary programming language? ')

# create max-heap containing relative "comparison scores" between
# each stored language and the given reference language
scores = compute_scores(ref_lang, lang_info)

# print out list of "Top 10" suggested languages 
print_scores(scores)
