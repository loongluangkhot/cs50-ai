import nltk
import sys
import re
import os

nltk.download('punkt_tab', quiet=True)

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP | S Conj S | S Conj VP
VP -> V | VP NP | Adv VP | VP Adv
NP -> FQN | P NP | NP Conj NP
CN -> N | N CN
QN -> CN | Adj QN 
FQN -> QN | Det QN | FQN Adv
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    tokens = nltk.tokenize.word_tokenize(sentence.lower())
    pattern = r"[a-z]+"

    def filter_func(i):
        return re.match(pattern, i) is not None
    
    filtered_tokens = list(filter(filter_func, tokens))
    return filtered_tokens


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    def is_np_tree(t):
        return t.label() == "NP"

    def is_np_chunk_tree(t): 
        return is_np_tree(t) and list(t.subtrees(is_np_tree))
    
    return list(tree.subtrees(is_np_chunk_tree))


def test(s):
    print(s)
    s = preprocess(s)
    trees = list(parser.parse(s))
    if not trees:
        raise Exception("Could not parse sentence.")
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def test_all_files():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    for i in range(10):
        file_path = os.path.join(current_dir, "sentences", f"{i+1}.txt")
        print(file_path)
        with open(file_path, "r") as f:
            s = f.read()
        test(s)


if __name__ == "__main__":
    main()
