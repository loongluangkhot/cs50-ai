import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    prob_map = {}
    for person_name in people:
        person = people[person_name]
        mother = person["mother"]
        father = person["father"]
        has_parents = mother is not None and father is not None
        has_trait = person_name in have_trait
        num_of_genes = get_num_of_genes(person_name, one_gene, two_genes)
        if has_parents:
            mother_num_of_genes = get_num_of_genes(mother, one_gene, two_genes)
            father_num_of_genes = get_num_of_genes(father, one_gene, two_genes)
            prob_map[person_name] = get_prob_for_person_with_parents(
                num_of_genes, has_trait, mother_num_of_genes, father_num_of_genes)
        else:
            prob_map[person_name] = get_prob_for_person_with_no_parents(num_of_genes, has_trait)
    joint_probability = 1
    for person_name in prob_map:
        joint_probability *= prob_map[person_name]
    return joint_probability


def get_num_of_genes(person_name, one_gene, two_genes):
    if person_name in one_gene:
        return 1
    elif person_name in two_genes:
        return 2
    else:
        return 0


def get_prob_for_person_with_no_parents(num_of_genes: int, has_trait: bool):
    return PROBS["gene"][num_of_genes] * PROBS["trait"][num_of_genes][has_trait]


def get_prob_for_person_with_parents(num_of_genes: int, has_trait: bool, mother_num_of_genes: int, father_num_of_genes: int):
    prob_of_getting_from_father = get_prob_of_person_getting_gene_from_parent(father_num_of_genes)
    prob_of_getting_from_mother = get_prob_of_person_getting_gene_from_parent(mother_num_of_genes)
    prob_of_not_getting_from_father = 1 - prob_of_getting_from_father
    prob_of_not_getting_from_mother = 1 - prob_of_getting_from_mother
    
    if num_of_genes == 0:
        prob_of_person_with_num_of_genes = prob_of_not_getting_from_father * prob_of_not_getting_from_mother
    elif num_of_genes == 1:
        prob_of_person_with_num_of_genes = prob_of_getting_from_father * prob_of_not_getting_from_mother + \
            prob_of_not_getting_from_father * prob_of_getting_from_mother
    else:
        prob_of_person_with_num_of_genes = prob_of_getting_from_father * prob_of_getting_from_mother

    return prob_of_person_with_num_of_genes * PROBS["trait"][num_of_genes][has_trait]


def get_prob_of_person_getting_gene_from_parent(parent_num_of_genes: int):
    if parent_num_of_genes == 0:
        return PROBS["mutation"]
    elif parent_num_of_genes == 1:
        return 0.5
    else:
        return 1 - PROBS["mutation"]


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person_name in probabilities:
        num_of_genes = get_num_of_genes(person_name, one_gene, two_genes)
        has_trait = person_name in have_trait
        probabilities[person_name]["gene"][num_of_genes] += p
        probabilities[person_name]["trait"][has_trait] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person_name in probabilities:
        for field in probabilities[person_name]:
            normalize_distribution(probabilities[person_name][field])


def normalize_distribution(distribution):
    total = sum(distribution.values())
    for value in distribution:
        distribution[value] /= total


if __name__ == "__main__":
    main()
