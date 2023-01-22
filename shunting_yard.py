# -*- coding: utf-8 -*-

# Copyright (C) 2021-2023 Ilya Bezrukov, Stepan Chizhov, Artem Grishin
#
# This file is part of math_bot.
#
# math_bot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# any later version.
#
# math_bot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from typing import Callable, TypeVar, Generic, List, Dict, Set, FrozenSet, Deque, Tuple, Optional
from collections import deque
from abc import ABCMeta
from enum import Enum


class InvalidSyntax (SyntaxError):
    pass


class InvalidName (NameError):
    pass


class InvalidArguments (SyntaxError):
    pass


class CalculationLimitError (ValueError):
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
    LimiterFunc = Callable[[List[T]], bool]

    func: Callable[..., T]
    argc: int
    limiter: Optional[LimiterFunc]

    def __init__(self, func: Callable[..., T], argc: int,
                 limiter: Optional[LimiterFunc] = None):
        super().__init__()
        self.func = func
        self.argc = argc
        self.limiter = limiter

    def eval(self, *args: Number) -> Number:
        values = [x.value for x in args]
        if self.limiter and not self.limiter(values):
            raise CalculationLimitError(f"Arguments failed limitations check in {self}")
        return Number(self.func(*values))

    @staticmethod
    def limit(union_limit: Optional[T], each_limit: Optional[T]) -> LimiterFunc:
        def inner_limiter(args):
            union = every = True
            if union_limit is not None:
                union = not all([x > union_limit for x in args])
            if each_limit is not None:
                every = not any([x > each_limit for x in args])
            return union and every
        return inner_limiter

    @staticmethod
    def no_limit():
        return lambda args: True


class Operator (Evaluator):
    class Ary (Enum):
        NONE = 0
        UNARY = 1
        BINARY = 2

    class Associativity(Enum):
        LEFT = 0
        RIGHT = 1

    char: str
    priority: int
    assoc: Associativity = Associativity.LEFT
    ary: Ary = Ary.BINARY

    def __init__(self, char: str, func: Callable[..., T], priority: int = 1,
                 assoc: Associativity = Associativity.LEFT,
                 ary: Ary = Ary.BINARY,
                 limiter: Optional[Evaluator.LimiterFunc] = None):
        argc = 2 if ary == Operator.Ary.BINARY else 1
        super(Operator, self).__init__(func, argc, limiter)
        self.char = char
        self.priority = priority
        self.assoc = assoc
        self.ary = ary

    def __repr__(self):
        return f"<{self.__class__.__name__} {'U' if self.ary == Operator.Ary.UNARY else 'B'}: {self.char}>"


class Function (Evaluator):
    name: str

    def __init__(self, name: str, func: Callable[..., T], argc: int = 1,
                 limiter: Optional[Evaluator.LimiterFunc] = None):
        super(Function, self).__init__(func, argc, limiter)
        self.name = name

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>"


class Expression (Generic[T]):
    class Type (Enum):
        Parsed = 0
        RPN = 1

    def __init__(self, default_variables: Optional[Dict[str, T]] = None):
        self.type: Expression.Type = Expression.Type.Parsed
        self.tokens: Deque[Token] = deque()
        self.variables: Set[str] = set()
        self.default_variables = default_variables if default_variables else {}

    def push(self, token: Token):
        self.tokens.append(token)

    def register_variable(self, name: str):
        self.variables.add(name)

    def eval(self, variables: Optional[Dict[str, T]] = None) -> T:
        vars_ = self.default_variables.copy()
        if variables:
            vars_.update(variables)
        if self.variables - set(vars_.keys()):
            raise KeyError("Not all variables values are given to evaluate this expression")
        if self.type != Expression.Type.RPN:
            raise TypeError("Expression must be in RPN")
        tokens = self.tokens.copy()
        stack = []
        while tokens:
            top = tokens.popleft()
            if isinstance(top, Number):
                stack.append(top)
            elif isinstance(top, Variable):
                if top.name not in vars_:
                    raise InvalidName(f"Variable value is not defined for '{top.name}'")
                stack.append(Number(vars_[top.name]))
            elif isinstance(top, Evaluator):
                if len(stack) < top.argc:
                    raise InvalidArguments(f"Not enough arguments for evaluator")
                args = [stack.pop() for _ in range(top.argc)]
                args.reverse()
                stack.append(top.eval(*args))
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
                 use_variables: bool = False,
                 default_variables: Optional[Dict[str, T]] = None,
                 converter: Callable[[str], T] = int,
                 args_separator: str = ",",
                 braces: Tuple[str, str] = ("(", ")"),
                 default_limiter: Optional[Evaluator.LimiterFunc] = None):
        evaluators: List[Evaluator] = operators.copy()
        evaluators += functions.copy()
        for ev in evaluators:
            if not ev.limiter:
                ev.limiter = default_limiter
        self.unary_operators = {op.char: op for op in operators if op.ary == Operator.Ary.UNARY}
        self.binary_operators = {op.char: op for op in operators if op.ary == Operator.Ary.BINARY}
        self.functions = {f.name: f for f in functions}
        self.whitespaces = whitespaces
        self.use_variables = use_variables
        self.default_variables = default_variables if default_variables else {}
        self.converter = converter
        self.args_separator = args_separator
        self.open_brace, self.close_brace = braces

    def parse(self, string: str) -> Expression:
        if not string:
            raise InvalidSyntax("String is empty, nothing to parse")
        input = deque(string)
        ary_state = Operator.Ary.UNARY
        expr = Expression(self.default_variables)
        position = 0
        while input:
            char = input.popleft()
            if char in self.whitespaces:
                pass
            elif char in self.unary_operators and ary_state == Operator.Ary.UNARY:
                expr.push(self.unary_operators[char])
                ary_state = Operator.Ary.NONE
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
                    ary_state = Operator.Ary.NONE
                else:
                    if not self.use_variables and name not in self.default_variables:
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
