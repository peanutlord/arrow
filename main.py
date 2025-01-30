from arrow.scanner import Scanner, Tokens
import random
from string import ascii_letters

DEBUG = False

map = {
    "print": print,
    "upper": str.upper,
    "lower": str.lower,
    "random": lambda _: random.randint(0, 1_000_000),  # TODO if result is None, it will passed into lambda, thus the _,
    "ascii_letters": ascii_letters
}


def main():
    with open("hello.arrow") as f:
        scanner: Scanner = Scanner(f)
        tokens = scanner.scan_tokens()

    if DEBUG:
        for i, (token, value) in enumerate(tokens):
            print(i, token, value)

    # The first arrow sets the direction of the pipeline
    # TODO idea: with a round parentheses you can have different directions (foo <- "Hello") -> lower
    direction, _ = tokens[1]

    # TODO to the direction by pipeline, we need to split via newline (loop with yield at newline)
    if direction == Tokens.RIGHT_ARROW:
        result = None

        # Now move forward
        for (token, value) in tokens:
            if token == Tokens.RIGHT_ARROW or token == Tokens.LEFT_ARROW:  # skip for now, we only support one direction
                continue

            # TODO code doesn't work because Token.NEWLINE is not being read properly, but the programm itself works due to LITERAL check at the bottom of the loop
            if token == Tokens.NEWLINE:
                # Reset result and start fresh
                result = None
                continue

            if token == Tokens.STRING:
                result = value

            if token == Tokens.LITERAL:
                if callable(map[value]):
                    result = map[value](result)
                else:
                    result = map[value]


if __name__ == "__main__":
    main()
