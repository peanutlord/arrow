class ASTNode:
    pass


class ArgumentNode(ASTNode):
    def __init__(self, args=None):
        self.args = args or []


class NumberNode(ASTNode):
    def __init__(self, number):
        self.number = number


class ArrowNode(ASTNode):
    def __init__(self, direction):
        self.direction = direction
        self.left = None
        self.right = None


class LiteralNode(ASTNode):
    def __init__(self, literal):
        self.literal = literal