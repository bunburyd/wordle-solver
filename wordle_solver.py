import argparse

from collections import Counter
from functools import lru_cache

MATCHING_LETTER = "Y"
WRONG_POSITION = "S"
WRONG_LETTER = "N"

WINNING_PATTERN = MATCHING_LETTER * 5

MAX_ATTEMPTS = 6

FAILED = 999

BEST_STARTING_GUESS_DEFAULT = "raise"


class TreeNode:

    def __init__(self, word=None):
        self.word = word
        self.guesses = {}

    def get_next_node(self, comparison):
        if comparison not in self.guesses:
            self.guesses[comparison] = TreeNode()
        return self.guesses[comparison]


class DecisionTree:

    def __init__(self, answers, start_word):
        self.root_node = TreeNode(start_word)
        self.current_node = self.root_node
        self.answers = answers
        self.remaining_answers = answers

    def reset(self):
        self.current_node = self.root_node
        self.remaining_answers = self.answers

    def set_comparison(self, comparison):

        guess = self.current_node.word

        self.remaining_answers = [
            answer for answer in self.remaining_answers
            if wordle_compare(guess, answer) == comparison
        ]

        self.current_node = self.current_node.get_next_node(comparison)

        if not self.current_node.word:
            self.current_node.word = self.calculate_next_guess()

    def calculate_next_guess(self):

        best_guess = None
        lowest_score = None

        for guess in self.answers:
            score = distribution_score(guess, self.remaining_answers, lowest_score)

            if (not lowest_score
                    or score < lowest_score
                    or (score == lowest_score
                        and guess in self.remaining_answers
                        and best_guess not in self.remaining_answers)):
                best_guess = guess
                lowest_score = score

        return best_guess

    def get_next_guess(self):
        return self.current_node.word


@lru_cache(maxsize=None)
def wordle_compare(guess, answer):
    response = ""
    cross_match_counter = Counter()

    for guess_letter, answer_letter in zip(guess, answer):
        # Only count letters that are not direct matches
        if guess_letter != answer_letter:
            cross_match_counter.update(answer_letter)

    for guess_letter, answer_letter in zip(guess, answer):
        if guess_letter == answer_letter:
            response += MATCHING_LETTER
        elif guess_letter in cross_match_counter and cross_match_counter[guess_letter] > 0:
            response += WRONG_POSITION
            cross_match_counter.subtract(guess_letter)
        else:
            response += WRONG_LETTER

    return response


def distribution_score(guess, answers, lowest_score):
    # A low distribution score means this guess distributes
    # the remaining possible answers evenly over a large
    # number of distinct colour patterns.
    comparisons = Counter()
    matches = 0

    for answer in answers:
        comparison = wordle_compare(guess, answer)
        comparisons.update([comparison])
        matches += comparisons[comparison]

        if lowest_score and matches > lowest_score:
            break

    return matches


def iterate_over_attempts(comparison_func, decision_tree: DecisionTree, answer=None):
    for attempt in range(1, MAX_ATTEMPTS + 1):

        next_guess = decision_tree.get_next_guess()

        comparison = comparison_func(attempt, next_guess, answer)

        if comparison == WINNING_PATTERN:
            print(f"Correct on {attempt}")
            results.update(str(attempt))
            return attempt

        decision_tree.set_comparison(comparison)

    print(f"Failed!")

    return 999


def compare_guess_to_answer(attempt, guess, answer):
    comparison = wordle_compare(guess, answer)
    print(f"Guess {attempt}: {guess}; Pattern: {comparison}")
    return comparison


def get_user_input(attempt, guess, answer):
    print(f"\nGuess {attempt}: {guess}\n")
    # print("Input colour pattern:")
    return input("Input colour pattern: ").upper()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--word-file", type=str)
    parser.add_argument("--word", type=str)

    args = parser.parse_args()

    word_file = args.word_file
    word = args.word

    with open(word_file, "r") as word_file_handle:
        words = [line.strip() for line in word_file_handle.readlines()]

    decision_tree = DecisionTree(words, BEST_STARTING_GUESS_DEFAULT)

    results = Counter()
    aggregate = 0

    if word:
        if word == "all":
            tests = words
        else:
            if word not in words:
                print(f"Requested word ({word}) is not in the answer list")
                exit(-1)
            tests = [word]

        for ai, answer in enumerate(tests):
            print(f"\n{ai}: Answer: {answer}\n")

            decision_tree.reset()

            attempt = iterate_over_attempts(compare_guess_to_answer, decision_tree, answer)

            results.update(str(attempt))
            aggregate += attempt

        print(f"\n\nResults: {sorted(results.items())}")
        print(f"Average: {round(aggregate / len(tests), 2)}")

    else:
        print("For each guess enter 5 characters representing the colour pattern\n")
        print("Y = match in right position (green)")
        print("S = match in wrong position (yellow)")
        print("N = no match (grey)\n\n")

        iterate_over_attempts(get_user_input, decision_tree)
