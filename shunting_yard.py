from typing import Callable, TypeVar, Generic, List, Dict, FrozenSet, Deque, Tuple
from collections import deque
from abc import ABCMeta
from enum import Enum


class InvalidSyntax (SyntaxError):
    pass


class InvalidName (NameError):
    pass


class InvalidArguments (SyntaxError):
    pass


T = TypeVar("T")


class Token (metaclass=ABCMeta):
    def __repr__(self):
        return f"<{self.__class__.__name__}>"


class OpenBrace (Token):
    pass


class CloseBrace (Token):
    pass


class ArgsSeparator (Token):
    pass


class Number (Generic[T], Token):
    value: T

    def __init__(self, value: T):
        self.value = value

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.value}>"


class Variable (Generic[T], Token):
    name: str

    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>"


class Evaluator (Generic[T], Token):
    func: Callable[..., T]

    def __init__(self, func: Callable[..., T]):
        super().__init__()
        self.func = func

    def __call__(self, *args: Number) -> Number:
        return Number(self.func(*[x.value for x in args]))


class Operator (Evaluator):
    class Ary (Enum):
        UNARY = 0
        BINARY = 1

    class Associativity(Enum):
        LEFT = 0
        RIGHT = 1

    char: str
    priority: int
    assoc: Associativity = Associativity.LEFT
    ary: Ary = Ary.BINARY

    def __init__(self, char: str, func: Callable[..., T], priority: int = 1,
                 assoc: Associativity = Associativity.LEFT,
                 ary: Ary = Ary.BINARY):
        super(Operator, self).__init__(func)
        self.char = char
        self.priority = priority
        self.assoc = assoc
        self.ary = ary

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.char}>"


class Function (Evaluator):
    name: str
    argc: int

    def __init__(self, name: str, func: Callable[..., T], argc: int = 1):
        super(Function, self).__init__(func)
        self.name = name
        self.argc = argc

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>"


class Expression (Generic[T]):
    class Type (Enum):
        Parsed = 0
        RPN = 1

    def __init__(self):
        self.type: Expression.Type = Expression.Type.Parsed
        self.tokens: Deque[Token] = deque()
        self.variables: List[str] = []

    def push(self, token: Token):
        self.tokens.append(token)

    def register_variable(self, name: str):
        self.variables.append(name)

    def eval(self, variables: Dict[str, T] = None) -> T:
        if not variables:
            variables = {}
        if self.type != Expression.Type.RPN:
            raise TypeError("Expression must be in RPN")
        tokens = self.tokens.copy()
        stack = []
        while tokens:
            top = tokens.popleft()
            if isinstance(top, Number):
                stack.append(top)
            elif isinstance(top, Variable):
                if top.name not in variables:
                    raise InvalidName(f"Variable value is not defined for '{top.name}'")
                stack.append(Number(variables[top.name]))
            elif isinstance(top, Operator):
                if top.ary == Operator.Ary.BINARY:
                    b, a = stack.pop(), stack.pop()
                    stack.append(top(a, b))
                elif top.ary == Operator.Ary.UNARY:
                    a = stack.pop()
                    stack.append(top(a))
                else:
                    raise TypeError("Operator ary not match UNARY or BINARY")
            elif isinstance(top, Function):
                if len(stack) < top.argc:
                    raise InvalidArguments(f"Not enough arguments for function '{top.name}'")
                args = [stack.pop() for _ in range(top.argc)]
                stack.append(top(*args[::-1]))
            else:
                raise TypeError(f"Met not allowed token in RPN: {top}")
        if len(stack) > 1:
            raise InvalidSyntax("Stack size greater than 1 after evaluation")
        return stack[0].value

    def __repr__(self):
        return repr(self.tokens)


class ShuntingYard (Generic[T]):
    def __init__(self, operators: List[Operator], functions: List[Function],
                 whitespaces: FrozenSet[str] = frozenset((" ", "\t", "\n")),
                 variables: bool = False,
                 converter: Callable[[str], T] = int,
                 args_separator: str = ",",
                 braces: Tuple[str, str] = ("(", ")")):
        self.unary_operators = {op.char: op for op in operators if op.ary == Operator.Ary.UNARY}
        self.binary_operators = {op.char: op for op in operators if op.ary == Operator.Ary.BINARY}
        self.functions = {f.name: f for f in functions}
        self.whitespaces = whitespaces
        self.variables = variables
        self.converter = converter
        self.args_separator = args_separator
        self.open_brace, self.close_brace = braces

    def parse(self, string: str) -> Expression:
        if not string:
            raise InvalidSyntax("String is empty, nothing to parse")
        input = deque(string)
        ary_state = Operator.Ary.UNARY
        expr = Expression()
        position = 0
        while input:
            char = input.popleft()
            if char in self.whitespaces:
                pass
            elif char in self.unary_operators and ary_state == Operator.Ary.UNARY:
                expr.push(self.unary_operators[char])
            elif char in self.binary_operators and ary_state == Operator.Ary.BINARY:
                expr.push(self.binary_operators[char])
                ary_state = Operator.Ary.UNARY
            elif char.isalpha():
                name = char
                while input and input[0].isalnum():
                    char = input.popleft()
                    position += 1
                    name += char
                if name in self.functions:
                    expr.push(self.functions[name])
                    ary_state = Operator.Ary.UNARY
                else:
                    if not self.variables:
                        raise InvalidName(f"Invalid name '{name}' at pos {position}")
                    expr.register_variable(name)
                    expr.push(Variable(name))
                    ary_state = Operator.Ary.BINARY
            elif char.isdigit():
                number = char
                while input and (input[0].isdigit() or input[0] == "."):
                    char = input.popleft()
                    position += 1
                    number += char
                expr.push(Number(self.converter(number)))
                ary_state = Operator.Ary.BINARY
            elif char == self.args_separator:
                expr.push(ArgsSeparator())
                ary_state = Operator.Ary.UNARY
            elif char == self.open_brace:
                expr.push(OpenBrace())
                ary_state = Operator.Ary.UNARY
            elif char == self.close_brace:
                expr.push(CloseBrace())
                ary_state = Operator.Ary.BINARY
            else:
                raise InvalidSyntax(f"Invalid character '{char}' at pos {position}")
            position += 1
        return expr

    def shunt(self, expr: Expression) -> Expression:
        stack = []
        output = deque()
        for token in expr.tokens:
            if isinstance(token, Number):
                output.append(token)
            elif isinstance(token, Variable):
                output.append(token)
            elif isinstance(token, Function):
                stack.append(token)
            elif isinstance(token, ArgsSeparator):
                args_check = False
                while stack:
                    if isinstance(stack[-1], OpenBrace):
                        args_check = True
                        break
                    output.append(stack.pop())
                if not args_check:
                    raise InvalidSyntax("Missing argument separator or left brace in expression")
            elif isinstance(token, Operator):
                while stack:
                    top = stack[-1]
                    if isinstance(top, Operator):
                        if (top.priority > token.priority and token.ary != Operator.Ary.UNARY) or \
                                (top.priority == token.priority and token.assoc == Operator.Associativity.LEFT):
                            output.append(stack.pop())
                        else:
                            break
                    elif isinstance(top, Function):
                        output.append(stack.pop())
                    else:
                        break
                stack.append(token)
            elif isinstance(token, OpenBrace):
                stack.append(token)
            elif isinstance(token, CloseBrace):
                braces_check = False
                while stack:
                    top = stack.pop()
                    if isinstance(top, OpenBrace):
                        braces_check = True
                        break
                    output.append(top)
                if not braces_check:
                    raise InvalidSyntax("Missing left brace in expression")
        while stack:
            top = stack.pop()
            if isinstance(top, OpenBrace):
                raise InvalidSyntax("Missing right brace in expression")
            output.append(top)
        expr.tokens = output
        expr.type = Expression.Type.RPN
        return expr


if __name__ == "__main__":
    sy = ShuntingYard(
        [
            Operator("+", lambda a, b: a + b, 1),
            Operator("-", lambda a, b: a - b, 1),
            Operator("*", lambda a, b: a * b, 2),
            Operator("/", lambda a, b: a / b, 2),
            Operator("//", lambda a, b: a // b, 2),
            Operator("%", lambda a, b: a % b, 2),
            Operator("-", lambda a: -a, 5, ary=Operator.Ary.UNARY),
            Operator("^", lambda a, b: a ** b, 10, assoc=Operator.Associativity.RIGHT),
        ],
        [
            Function("abs", lambda x: abs(x)),
            Function("mod", lambda a, b: a % b, argc=2)
        ],
        variables=True,
        converter=lambda x: float(x) if "." in x else int(x)
    )
    pexpr = sy.parse(input("> "))
    print(pexpr)
    pexpr = sy.shunt(pexpr)
    print(pexpr)
    print(pexpr.eval())
