#!/usr/bin/env python3
"""lambda_calc2 - Lambda calculus with beta reduction and Church encodings."""
import sys, argparse, re

class Var:
    def __init__(self, name): self.name = name
    def __repr__(self): return self.name
    def free_vars(self): return {self.name}
    def substitute(self, var, expr):
        return expr if self.name == var else self
    def __eq__(self, o): return isinstance(o, Var) and self.name == o.name

class Lam:
    def __init__(self, param, body): self.param = param; self.body = body
    def __repr__(self): return f"(\\{self.param}.{self.body})"
    def free_vars(self): return self.body.free_vars() - {self.param}
    def substitute(self, var, expr):
        if var == self.param: return self
        if self.param in expr.free_vars():
            new_param = self.param + "'"
            while new_param in expr.free_vars() | self.body.free_vars(): new_param += "'"
            body = self.body.substitute(self.param, Var(new_param))
            return Lam(new_param, body.substitute(var, expr))
        return Lam(self.param, self.body.substitute(var, expr))

class App:
    def __init__(self, func, arg): self.func = func; self.arg = arg
    def __repr__(self): return f"({self.func} {self.arg})"
    def free_vars(self): return self.func.free_vars() | self.arg.free_vars()
    def substitute(self, var, expr):
        return App(self.func.substitute(var, expr), self.arg.substitute(var, expr))

def beta_reduce(expr, max_steps=100):
    for _ in range(max_steps):
        reduced = _step(expr)
        if reduced is None: return expr
        expr = reduced
    return expr

def _step(expr):
    if isinstance(expr, App):
        if isinstance(expr.func, Lam):
            return expr.func.body.substitute(expr.func.param, expr.arg)
        r = _step(expr.func)
        if r: return App(r, expr.arg)
        r = _step(expr.arg)
        if r: return App(expr.func, r)
    if isinstance(expr, Lam):
        r = _step(expr.body)
        if r: return Lam(expr.param, r)
    return None

def to_church(n):
    body = Var("x")
    for _ in range(n): body = App(Var("f"), body)
    return Lam("f", Lam("x", body))

def from_church(expr, max_steps=200):
    expr = beta_reduce(expr, max_steps)
    if not isinstance(expr, Lam): return None
    if not isinstance(expr.body, Lam): return None
    f, x = expr.param, expr.body.param
    body = expr.body.body; count = 0
    while isinstance(body, App) and isinstance(body.func, Var) and body.func.name == f:
        count += 1; body = body.arg
    if isinstance(body, Var) and body.name == x: return count
    return None

CHURCH = {
    "SUCC": Lam("n", Lam("f", Lam("x", App(Var("f"), App(App(Var("n"), Var("f")), Var("x")))))),
    "PLUS": Lam("m", Lam("n", Lam("f", Lam("x", App(App(Var("m"), Var("f")), App(App(Var("n"), Var("f")), Var("x"))))))),
    "MULT": Lam("m", Lam("n", Lam("f", App(Var("m"), App(Var("n"), Var("f")))))),
    "TRUE": Lam("a", Lam("b", Var("a"))),
    "FALSE": Lam("a", Lam("b", Var("b"))),
    "AND": Lam("p", Lam("q", App(App(Var("p"), Var("q")), Var("p")))),
    "OR": Lam("p", Lam("q", App(App(Var("p"), Var("p")), Var("q")))),
    "NOT": Lam("p", Lam("a", Lam("b", App(App(Var("p"), Var("b")), Var("a"))))),
    "ISZERO": Lam("n", App(App(Var("n"), Lam("x", Lam("a", Lam("b", Var("b"))))), Lam("a", Lam("b", Var("a"))))),
}

def main():
    p = argparse.ArgumentParser(description="Lambda calculus interpreter")
    p.add_argument("--demo", action="store_true")
    args = p.parse_args()
    if args.demo:
        two, three = to_church(2), to_church(3)
        five = beta_reduce(App(App(CHURCH["PLUS"], two), three))
        print(f"2 + 3 = {from_church(five)}")
        six = beta_reduce(App(App(CHURCH["MULT"], two), three))
        print(f"2 * 3 = {from_church(six)}")
        succ_two = beta_reduce(App(CHURCH["SUCC"], two))
        print(f"succ(2) = {from_church(succ_two)}")
        zero = to_church(0)
        iz = beta_reduce(App(CHURCH["ISZERO"], zero))
        print(f"isZero(0) = {iz}")
        iz2 = beta_reduce(App(CHURCH["ISZERO"], two))
        print(f"isZero(2) = {iz2}")
        identity = Lam("x", Var("x"))
        result = beta_reduce(App(identity, Var("y")))
        print(f"(\\x.x) y = {result}")
    else: p.print_help()

if __name__ == "__main__":
    main()
