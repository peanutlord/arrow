from arrow.scanner import Scanner, Tokens
from arrow.ast import ArgumentNode, ArrowNode, LiteralNode

DEBUG = False

map = {
    "print": print,
    "+": sum,
}


def main():
    with open("scripts/calculator.arrow") as f:
        scanner: Scanner = Scanner(f)
        tokens = scanner.scan_tokens()

    if DEBUG:
        for i, (token, value) in enumerate(tokens):
            print(i, token, value)

    r"""
    10 10 -> + -> print
    
    AST should look like this?
    
            ->
           /  \
          ->  print
         / \
     10 10  +
    """

    r"""
    x <- 20
    
        <-
       /  \
      x   20 
    """
    tree = None
    # Enumerate will throw RuntimeError due to mutation of the deque
    i = 0
    while i < len(tokens):
        token, value = tokens[i]
        if token == Tokens.NUMBER:  # Could also be literal?
            args = [value]
            while True:
                # Move i forward as we already have
                i = i + 1

                if tokens[i][0] in (Tokens.RIGHT_ARROW, Tokens.LEFT_ARROW):
                    break

                if tokens[i][0] == Tokens.NUMBER:
                    args.append(tokens[i][1])

            tree = ArgumentNode(args)
            continue

        if token == Tokens.RIGHT_ARROW or token == Tokens.LEFT_ARROW:  # ->
            node = ArrowNode(value)
            if tree:
                node.left = tree

            tree = node

        if token == Tokens.LITERAL or token == Tokens.OPERATOR:  # + / print
            tree.right = LiteralNode(value)

        i = i + 1

    # Parse the tree
    def parse(leaf_or_node):
        if isinstance(leaf_or_node, ArgumentNode):
            return leaf_or_node.args
        elif isinstance(leaf_or_node, ArrowNode):
            args = parse(leaf_or_node.left)
            func = parse(leaf_or_node.right)

            if callable(map[func]):
                return map[func](args)

        elif isinstance(leaf_or_node, LiteralNode):
            return leaf_or_node.literal

    parse(tree)

    # How the tree should look like:
    """
    # The first arrow sets the direction of the pipeline
    # TODO idea: with a round parentheses you can have different directions (foo <- "Hello") -> lower
    direction, _ = tokens[2]

    # TODO to the direction by pipeline, we need to split via newline (loop with yield at newline)
    if direction == Tokens.RIGHT_ARROW:
        result = None

        # Now move forward
        for i, (token, value) in enumerate(tokens):
            if token == Tokens.RIGHT_ARROW or token == Tokens.LEFT_ARROW:  # skip for now, we only support one direction
                continue

            # TODO does the parse parse newline successfully? Unknown atm
            if token == Tokens.NEWLINE:
                # Reset result and start fresh
                result = None
                continue

            if token == Tokens.STRING:
                result = value

            if token == Tokens.LITERAL:
                if callable(map[value]):
                    if isinstance(result, tuple):
                        result = map[value](*result)
                    else:
                        result = map[value](result)
                else:
                    result = map[value]

            # The arguments
            if i == 0:
                arg1, arg2 = token, tokens[1]
                result = (value, arg2[1])
                continue
    """


if __name__ == "__main__":
    main()
