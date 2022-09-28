from typing import Callable, TypeVar, Generic, Union, Dict, Optional, Deque
from collections import deque
from abc import ABCMeta, abstractmethod
from enum import Enum


class InvalidInput (ValueError):
    pass


class InvalidSyntax (ValueError):
    pass


class InvalidCalculatorParameter (ValueError):
    pass


class Associativity (Enum):
    LEFT = 0
    RIGHT = 1


T = TypeVar("T")


class ExprElement (Generic[T], metaclass=ABCMeta):
    sequence: str

    def __init__(self, sequence: str):
        self.sequence = sequence


class OpenBrace (ExprElement):
    pass


class CloseBrace (ExprElement):
    pass


class Number (ExprElement):
    value: Union[T, Variable]


class Calculator (ExprElement, metaclass=ABCMeta):
    BackendFunction = Callable[..., T]

    func: BackendFunction
    argc: int = 1

    def __init__(self, sequence: str, func: BackendFunction, argc: int = 1):
        super(Calculator, self).__init__(sequence)
        self.func = func
        self.argc = argc

    def __call__(self, *args):
        return self.func(*args)


class Operator (Calculator):
    priority: int
    associativity: Associativity

    def __init__(self, symbol: str, func: Calculator.BackendFunction, argc: int = 2,
                 priority: int = 1, assoc: Associativity = Associativity.LEFT):
        super(Operator, self).__init__(sequence=symbol, func=func, argc=argc)
        if self.argc > 2:
            raise InvalidCalculatorParameter("Operator argc must be 1 or 2 (unary or binary)")
        self.priority = priority
        self.associativity = assoc
        self.argc = argc


class Function (Calculator):
    def __init_(self, name: str, func: Calculator.BackendFunction, argc: int = 1):
        super(Function, self).__init__(sequence=name, func=func, argc=argc)


class Token:
    expr_element: ExprElement

    def __init__(self, expr_element: ExprElement):
        self.expr_element = expr_element


class Grammar:
    def __init__(self):
        self.operators: Dict[str, Operator] = {}
        self.functions: Dict[str, Function] = {}
        self.open_brace: OpenBrace = OpenBrace("(")
        self.close_brace: CloseBrace = CloseBrace(")")
        self.variables: Dict[str, Variable] = {}

    def add(self, el: ExprElement):
        if isinstance(el, Operator):
            self.operators[el.sequence] = el
        elif isinstance(el, Function):
            self.functions[el.sequence] = el
        elif isinstance(el, OpenBrace):
            self.open_brace = el
        elif isinstance(el, CloseBrace):
            self.close_brace = el
        elif isinstance(el, Variable):


    def parse(self) -> Deque[Token]:
        pass
