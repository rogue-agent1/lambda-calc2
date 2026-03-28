#!/usr/bin/env python3
"""Lambda calculus — parser, reducer, Church numerals, combinators."""
import sys, re

class Var:
    def __init__(self, name): self.name = name
    def __repr__(self): return self.name
    def subst(self, var, val): return val if self.name == var else self
    def reduce(self): return self
    def free(self): return {self.name}

class Lam:
    def __init__(self, var, body): self.var, self.body = var, body
    def __repr__(self): return f"(λ{self.var}.{self.body})"
    def subst(self, var, val):
        if var == self.var: return self
        return Lam(self.var, self.body.subst(var, val))
    def reduce(self): return Lam(self.var, self.body.reduce())
    def free(self): return self.body.free() - {self.var}

class App:
    def __init__(self, fn, arg): self.fn, self.arg = fn, arg
    def __repr__(self): return f"({self.fn} {self.arg})"
    def subst(self, var, val): return App(self.fn.subst(var, val), self.arg.subst(var, val))
    def reduce(self):
        if isinstance(self.fn, Lam): return self.fn.body.subst(self.fn.var, self.arg)
        fn2 = self.fn.reduce()
        if repr(fn2) != repr(self.fn): return App(fn2, self.arg)
        return App(self.fn, self.arg.reduce())
    def free(self): return self.fn.free() | self.arg.free()

def church(n):
    body = Var("x")
    for _ in range(n): body = App(Var("f"), body)
    return Lam("f", Lam("x", body))

def unchurch(expr, max_steps=100):
    for _ in range(max_steps):
        r = expr.reduce()
        if repr(r) == repr(expr): break
        expr = r
    count = 0; e = expr
    if isinstance(e, Lam) and isinstance(e.body, Lam):
        inner = e.body.body
        while isinstance(inner, App): count += 1; inner = inner.arg
    return count

COMBINATORS = {
    "I": Lam("x", Var("x")),
    "K": Lam("x", Lam("y", Var("x"))),
    "S": Lam("x", Lam("y", Lam("z", App(App(Var("x"), Var("z")), App(Var("y"), Var("z")))))),
    "SUCC": Lam("n", Lam("f", Lam("x", App(Var("f"), App(App(Var("n"), Var("f")), Var("x")))))),
    "PLUS": Lam("m", Lam("n", Lam("f", Lam("x", App(App(Var("m"), Var("f")), App(App(Var("n"), Var("f")), Var("x"))))))),
}

def normalize(expr, max_steps=200):
    for _ in range(max_steps):
        r = expr.reduce()
        if repr(r) == repr(expr): return expr
        expr = r
    return expr

def cli():
    if len(sys.argv) < 2:
        print("Usage: lambda_calc2 <cmd> [args]"); print("  church N | add M N | succ N | combinator NAME"); sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "church":
        n = int(sys.argv[2]); print(f"Church({n}) = {church(n)}")
    elif cmd == "add":
        m, n = int(sys.argv[2]), int(sys.argv[3])
        plus = COMBINATORS["PLUS"]
        result = normalize(App(App(plus, church(m)), church(n)))
        print(f"{m} + {n} = {unchurch(result)}"); print(f"Term: {result}")
    elif cmd == "succ":
        n = int(sys.argv[2]); succ = COMBINATORS["SUCC"]
        result = normalize(App(succ, church(n)))
        print(f"succ({n}) = {unchurch(result)}")
    elif cmd == "combinator":
        name = sys.argv[2].upper()
        if name in COMBINATORS: print(f"{name} = {COMBINATORS[name]}")
        else: print(f"Known: {list(COMBINATORS.keys())}")

if __name__ == "__main__": cli()
