from typing import Callable, TypeVar, Generic, List, Dict, FrozenSet, Deque, Tuple
from collections import deque
from string import digits
from abc import ABCMeta
from enum import Enum


class InvalidInput (ValueError):
    pass


class InvalidSyntax (ValueError):
    pass


class InvalidName (ValueError):
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


class Evaluator (Generic[T], Token):
    func: Callable[..., T]

    def __init__(self, func: Callable[..., T]):
        super().__init__()
        self.func = func

    def __call__(self, *args: T) -> T:
        return self.func(*args)


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

    def __init__(self, char: str, func: Callable[..., T], priority: int = 1,
                 assoc: Associativity = Associativity.LEFT,
                 ary: Ary = Ary.BINARY):
        super(Operator, self).__init__(func)
        self.char = char
        self.priority = priority
        self.assoc = assoc
        self.ary = ary


class Function (Evaluator):
    name: str
    argc: int

    def __init__(self, name: str, func: Callable[..., T], argc: int = 1):
        super(Function, self).__init__(func)
        self.name = name
        self.argc = argc


class ParsedExpression (Generic[T]):
    def __init__(self):
        self.tokens: Deque[Token] = deque()
        self.variables: List[str] = []

    def push(self, token: Token):
        self.tokens.append(token)

    def add_variable(self, name: str):
        self.variables.append(name)

    def __repr__(self):
        return repr(self.tokens)


class ShuntingYard (Generic[T]):
    def __init__(self, operators: List[Operator], functions: List[Function],
                 digits_: FrozenSet[str] = frozenset(digits),
                 whitespaces: FrozenSet[str] = frozenset((" ", "\t", "\n")),
                 variables: bool = False,
                 converter: Callable[[str], T] = T,
                 args_separator: str = ",",
                 braces: Tuple[str, str] = ("(", ")")):
        self.unary_operators = {op.char: op for op in operators if op.ary == Operator.Ary.UNARY}
        self.binary_operators = {op.char: op for op in operators if op.ary == Operator.Ary.BINARY}
        self.functions = {f.name: f for f in functions}

        self.digits = digits_
        self.whitespaces = whitespaces
        self.variables = variables
        self.converter = converter
        self.args_separator = args_separator
        self.open_brace, self.close_brace = braces

        self.functions_first = frozenset((key[0] for key in self.functions))

    def parse(self, string: str) -> ParsedExpression:
        if not string:
            raise InvalidInput("String is empty, nothing to parse")
        input = deque(string)
        ary_state = Operator.Ary.UNARY
        pexpr = ParsedExpression()
        position = 0
        char = input.popleft()
        while input:
            print(pexpr)
            if char in self.whitespaces:
                continue
            elif char in self.unary_operators and ary_state == Operator.Ary.UNARY:
                pexpr.push(self.unary_operators[char])
            elif char in self.binary_operators and ary_state == Operator.Ary.BINARY:
                pexpr.push(self.binary_operators[char])
            elif char in self.functions_first:
                func_name = char
                while input:
                    char = input.popleft()
                    position += 1
                    if char in self.whitespaces: break
                    func_name += char
                if func_name in self.functions:
                    pexpr.push(self.functions[func_name])
                else:
                    pass  # do smth
            elif char in self.digits:
                number = char
                while input:
                    char = input.popleft()
                    position += 1
                    if char in self.whitespaces: break
                    if char not in self.digits:
                        raise InvalidInput(f"Invalid character inside number '{char}' at pos {position}")
                    number += char
                pexpr.push(Number(number))
            elif char == self.args_separator:
                pexpr.push(ArgsSeparator())
            elif char == self.open_brace:
                pexpr.push(OpenBrace())
            elif char == self.close_brace:
                pexpr.push(CloseBrace())
            else:
                raise InvalidInput(f"Invalid character '{char}' at pos {position}")
            char = input.popleft()
            position += 1

        return pexpr

    def shunt(self, pexpr: ParsedExpression) -> None:
        # self
        return None


if __name__ == "__main__":
    sy = ShuntingYard(
        [
            Operator("+", lambda a, b: a + b, 1),
            Operator("*", lambda a, b: a * b, 2),
        ],
        [
            Function("abs", lambda x: abs(x))
        ]
    )
    pexpr = sy.parse("5 + 8 * 3")
    print(pexpr)
