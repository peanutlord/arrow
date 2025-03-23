from arrow.scanner import Scanner, Tokens
from arrow.ast import ArgumentNode, ArrowNode, LiteralNode, NumberNode, StringNode

DEBUG = False

def _minus(args):
    start = args[0]
    for n in args[1:]:
        start = start - n

    return start


variables = {}
func_map = {
    "print": print,
    "+": sum,
    "-": _minus
}


def main():
    with open("scripts/test.arrow") as f:
        scanner: Scanner = Scanner(f)
        tokens = scanner.scan_tokens()

    if DEBUG:
        for i, (token, value) in enumerate(tokens):
            print(i, token, value)

    # Let's start again...
    # TODO for later: when we make functions, each function could return a new version of the tree
    root = []
    tree = None

    # TODO find something more elegant
    i = 0
    while i < len(tokens):
        token, value = tokens[i]

        if token == Tokens.STRING:
            node = StringNode(value)
            if not tree:
                tree = node
            else:
                tree.right = node

        if token == Tokens.NUMBER:
            # First we need to figure out if it's assignment or an argument - so let's peek
            last_token, last_value = tokens[i - 1]
            if last_token == Tokens.LEFT_ARROW:  # most likely assignment
                node = NumberNode(value)
                if not tree:
                    tree = node
                else:
                    tree.right = node

            next_token, next_value = tokens[i + 1]
            if next_token == Tokens.NUMBER:
                args = []

                # Now we need to advance the tokens until we hit the arrow
                while pair := tokens[i]:
                    next_token, next_value = pair
                    if next_token in (Tokens.LEFT_ARROW, Tokens.RIGHT_ARROW):
                        i = i - 1  # go back one step
                        break

                    args.append(next_value)
                    i = i + 1

                # Verify
                tree = ArgumentNode(args)

        # Assigning
        if token == Tokens.LEFT_ARROW:
            node = ArrowNode(value)
            node.left = tree

            tree = node

        # Pipeline
        if token == Tokens.RIGHT_ARROW:
            node = ArrowNode(value)
            node.left = tree

            tree = node

        if token == Tokens.LITERAL or token == Tokens.OPERATOR:
            literal = LiteralNode(value)
            if not tree:
                tree = literal
            else:
                tree.right = literal

        if tree and token == Tokens.NEWLINE or token == Tokens.EOF:
            root.append(tree)
            tree = None

        # Next token
        i = i + 1

    # Parse the tree
    def parse(leaf_or_node):
        if isinstance(leaf_or_node, ArrowNode):
            if leaf_or_node.direction == "<-":  # left
                name = parse(leaf_or_node.left)
                value = parse(leaf_or_node.right)

                variables[name] = value
            elif leaf_or_node.direction == "->":
                arg = parse(leaf_or_node.left)
                func = parse(leaf_or_node.right)

                f = func_map[func]
                return f(arg)

        elif isinstance(leaf_or_node, NumberNode):
            return leaf_or_node.number
        elif isinstance(leaf_or_node, LiteralNode):
            # return leaf_or_node.literal
            name = leaf_or_node.literal
            if name in variables:
                return variables[name]

            return name
        elif isinstance(leaf_or_node, ArgumentNode):
            return leaf_or_node.args
        elif isinstance(leaf_or_node, StringNode):
            return leaf_or_node.string

    for tree in root:
        parse(tree)


if __name__ == "__main__":
    main()
