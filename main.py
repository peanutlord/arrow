from arrow.scanner import Scanner, Tokens
from arrow.ast import ArgumentNode, ArrowNode, LiteralNode, NumberNode

DEBUG = False

def _minus(args):
    start = args[0]
    for n in args[1:]:
        start = start - n

    return start

variable_map = {}
map = {
    "print": print,
    "+": sum,
    "-": _minus
}


def main():
    with open("scripts/variable.arrow") as f:
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
            try:
                # Don't automatically assume it's a arg
                args = [value]

                i = i + 1
                # Can I make this more elegant? I don't like how it looks...
                while tokens[i][0] not in (Tokens.RIGHT_ARROW, Tokens.LEFT_ARROW):
                    token, value = tokens[i]
                    if token == Tokens.NUMBER:
                        args.append(value)

                    i = i + 1

                tree = ArgumentNode(args)
                continue
            except:
                tree.right = NumberNode(args.pop())
                continue

        if token == Tokens.RIGHT_ARROW or token == Tokens.LEFT_ARROW:  # ->
            node = ArrowNode(value)
            if tree:
                node.left = tree

            tree = node

        if token == Tokens.LITERAL or token == Tokens.OPERATOR:  # + / print
            # tree.right = LiteralNode(value)
            if tree:
                tree.right = LiteralNode(value)
            else:
                tree = LiteralNode(value)

        i = i + 1

    # Parse the tree
    def parse(leaf_or_node):
        # Separate the node for function calls and variables?
        if isinstance(leaf_or_node, ArgumentNode):
            return leaf_or_node.args
        elif isinstance(leaf_or_node, ArrowNode):
            if leaf_or_node.direction == "->":
                args = parse(leaf_or_node.left)
                func = parse(leaf_or_node.right)

                if callable(map[func]):
                    return map[func](args)
            elif leaf_or_node.direction == "<-":
                variable = parse(leaf_or_node.left)
                content = parse(leaf_or_node.right)
                variable_map[variable] = content
            else:
                # Unknown direction
                pass
        elif isinstance(leaf_or_node, LiteralNode):
            return leaf_or_node.literal
        elif isinstance(leaf_or_node, NumberNode):
            return leaf_or_node.number

    parse(tree)
    print(variable_map)


if __name__ == "__main__":
    main()
