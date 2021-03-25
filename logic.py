from collections import deque

OPS = {
    '~': (0, 1, lambda x: not x),
    '&': (1, 2, lambda x, y: x and y),
    '|': (2, 2, lambda x, y: x or y),
    '>': (3, 2, lambda x, y: not x or y),
    '^': (4, 2, lambda x, y: x != y),
    '=': (4, 2, lambda x, y: x == y)
}


def shunting_yard(s):
    variables = []
    right = deque(s.replace(' ', ''))
    stack = []
    out = []
    while right:
        t = right.popleft()
        if t in variables:
            out.append(t)
        elif t.isdigit():
            out.append(bool(t))
        elif t in OPS:
            while len(stack) > 0 and stack[-1] in OPS and OPS[stack[-1]][0] <= OPS[t][0]:
                out.append(stack.pop())
            stack.append(t)
        elif t == '(':
            stack.append(t)
        elif t == ')':
            while stack[-1] != '(':
                out.append(stack.pop())
            stack.pop()
        else:
            if t not in variables:
                variables.append(t)
            out.append(t)
    while stack:
        out.append(stack.pop())
    return out, variables


def calculate(tokens, variables):
    stack = []
    for t in tokens:
        if t in OPS:
            operands = deque()
            for i in range(OPS[t][1]):
                if len(stack) == 0:
                    raise SyntaxError('Incorrect logic expression')
                operands.appendleft(stack.pop())
            stack.append(OPS[t][2](*operands))
        elif t.isalpha():
            if t in variables:
                stack.append(bool(variables[t]))
            else:
                raise NameError(f'Variable "{t}" not defined!')
        else:
            stack.append(t)

    if not stack or len(stack) > 1:
        raise SyntaxError('Incorrect logic expression')
    return stack[-1]


if __name__ == '__main__':
    s = input('Expression: ')

    out, variables = shunting_yard(s)
    n = len(variables)

    print(*variables, 'F', sep='\t')

    for i in range(2 ** n):
        values = [int(x) for x in bin(i)[2:].rjust(n, '0')]
        d = {variables[k]: values[k] for k in range(n)}
        print(*values, int(calculate(out, d)), sep='\t')