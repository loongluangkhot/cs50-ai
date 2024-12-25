import os
import random
import re
import sys
from collections import Counter

DAMPING = 0.85
SAMPLES = 10000

import random

def sample_from_distribution(distribution):
    """
    Sample from a discrete probability distribution.

    :param distribution: A dictionary where keys are outcomes and values are probabilities.
    :return: A sampled outcome.
    """
    # Create a list of cumulative probabilities
    outcomes = list(distribution.keys())
    probabilities = list(distribution.values())
    cdf = [sum(probabilities[:i+1]) for i in range(len(probabilities))]

    # Generate a random number
    random_number = random.random()

    # Find the interval in the CDF that contains the random number
    for i, threshold in enumerate(cdf):
        if random_number <= threshold:
            return outcomes[i]

def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    model = {}
    all_pages = dict.keys(corpus)
    linked_pages = corpus[page] if page in corpus else set()
    random_prob = (1 - damping_factor) / len(all_pages)
    linked_prob = damping_factor / len(linked_pages) if len(linked_pages) > 0 else 0
    for page in all_pages:
        if page in linked_pages:
            model[page] = random_prob + linked_prob
        else:
            model[page] = random_prob
    return model


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    page = None
    trace = []
    while n > 0:
        model = transition_model(corpus, page, damping_factor)
        page = sample_from_distribution(model)
        trace.append(page)
        n -= 1
    page_count_map = Counter(trace)
    for i in page_count_map:
        page_count_map[i] = page_count_map[i] / n
    prob_dist = dict(page_count_map)
    return prob_dist


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    raise NotImplementedError

def pr_formula(corpus, page, damping_factor, prob_dist):
    all_pages = dict.keys(corpus)
    incoming_pages = get_incoming_pages(corpus, page)
    random_prob = (1-damping_factor) / len(all_pages)
    linked_prob = damping_factor * sum([prob_dist[i] / len(corpus[i]) for i in incoming_pages])
    return random_prob + linked_prob

def get_incoming_pages(corpus, page):
    return set([i for i in corpus if page in corpus[i]])


if __name__ == "__main__":
    main()
