#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
calculator.py
基于栈和优先级表实现字符串计算器。
支持 + - * / ^ 以及一元 +-，并扩展支持 math 库单目函数（sin/cos/tan/log/ln/sqrt…）。
"""
import math
import re

class ArrayStack:
    def __init__(self):
        self._s = []
    def push(self, e):      self._s.append(e)
    def pop(self):          return self._s.pop()
    def top(self):          return self._s[-1]
    def empty(self):        return len(self._s) == 0

class Calculator:
    priority = {'+': 1, '-': 1, '*': 2, '/': 2, '^': 3,
                'u+': 4, 'u-': 4, 'func': 5}
    right_assoc = {'^', 'func'}
    func_map = {name: obj for name, obj in math.__dict__.items()
                if callable(obj) and name != 'pow'}
    @classmethod
    def tokenize(cls, expr: str):
        pattern = re.compile(r"\d+(?:\.\d+)?|[a-zA-Z_]\w*(?= $)|[()+\-*/^]|.")
        tokens = [t.strip() for t in pattern.findall(expr) if t.strip()]
        res, prev = [], '('
        for tok in tokens:
            if tok in '+-' and prev in '(@^':
                res.append('u' + tok)
            else:
                res.append(tok)
            prev = tok
        return res
    @classmethod
    def infix_to_postfix(cls, tokens):
        out, ops = [], ArrayStack()
        for t in tokens:
            if t == '(':
                ops.push(t)
            elif t == ')':
                while not ops.empty() and ops.top() != '(':
                    out.append(ops.pop())
                if ops.empty(): raise ValueError("Mismatched )")
                ops.pop()
                if not ops.empty() and ops.top() == 'func':
                    out.append(ops.pop())
            elif t in cls.priority or t == 'func':
                while not ops.empty() and ops.top() != '(':
                    top = ops.top()
                    if (top in cls.priority and
                        (cls.priority[top] > cls.priority[t] or
                         (cls.priority[top] == cls.priority[t] and t not in cls.right_assoc))):
                        out.append(ops.pop())
                    else:
                        break
                ops.push(t)
            else:
                out.append(t)
        while not ops.empty():
            if ops.top() == '(':
                raise ValueError("Mismatched (")
            out.append(ops.pop())
        return out
    @classmethod
    def eval_postfix(cls, post):
        st = ArrayStack()
        for t in post:
            if t in cls.priority:
                if t.startswith('u'):
                    a = st.pop()
                    st.push(-a if t == 'u-' else a)
                elif t == 'func':
                    fn, arg = st.pop(), st.pop()
                    st.push(cls.func_map[fn](arg))
                else:
                    b, a = st.pop(), st.pop()
                    if t == '+': st.push(a + b)
                    elif t == '-': st.push(a - b)
                    elif t == '*': st.push(a * b)
                    elif t == '/': st.push(a / b)
                    elif t == '^': st.push(a ** b)
            else:
                st.push(float(t))
        return st.pop()
    @classmethod
    def calculate(cls, expr: str):
        tokens = cls.tokenize(expr)
        post = cls.infix_to_postfix(tokens)
        return cls.eval_postfix(post)

def demo():
    print("=== 字符串计算器演示 ===")
    cases = [
        "3+4*2/(1-5)^2",
        "-3 + -4 * (2 + 5)",
        "sin(30*3.1415926/180)*2 + log(100)",
        "(1+2)*3^2"
    ]
    for c in cases:
        try:
            print(f"{c}  =  {Calculator.calculate(c)}")
        except Exception as e:
            print(f"{c}  ERROR: {e}")

if __name__ == "__main__":
    demo()
