#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
complex_vector.py
实现复数类、无序向量及其置乱、查找、插入、删除、唯一化；
支持按模+实部起泡/归并排序并计时对比；
支持已序向量区间查询 [m1,m2)。
"""
import random
import math
import time
from typing import List, Optional

class Complex:
    __slots__ = ("re", "im")
    def __init__(self, re: float, im: float):
        self.re, self.im = re, im
    @property
    def mod(self):
        return math.hypot(self.re, self.im)
    def __eq__(self, other):
        return self.re == other.re and self.im == other.im
    def __lt__(self, other):
        return (self.mod, self.re) < (other.mod, other.re)
    def __repr__(self):
        return f"({self.re}{self.im:+.1f}j)"

class ComplexVector:
    def __init__(self, data: Optional[List[Complex]] = None):
        self._data = data if data is not None else []
    def shuffle(self):
        random.shuffle(self._data)
    def find(self, target: Complex) -> int:
        for i, c in enumerate(self._data):
            if c == target:
                return i
        return -1
    def insert(self, idx: int, c: Complex):
        self._data.insert(idx, c)
    def remove(self, idx: int) -> Complex:
        return self._data.pop(idx)
    def uniquify(self):
        seen = set()
        new_data = []
        for c in self._data:
            key = (c.re, c.im)
            if key not in seen:
                seen.add(key)
                new_data.append(c)
        self._data = new_data
    def bubble_sort(self):
        a = self._data
        n = len(a)
        for i in range(n - 1):
            swapped = False
            for j in range(n - 1 - i):
                if a[j + 1] < a[j]:
                    a[j], a[j + 1] = a[j + 1], a[j]
                    swapped = True
            if not swapped:
                break
    def merge_sort(self):
        def merge(l, r):
            res, i, j = [], 0, 0
            while i < len(l) and j < len(r):
                if l[i] < r[j]:
                    res.append(l[i]); i += 1
                else:
                    res.append(r[j]); j += 1
            res.extend(l[i:]); res.extend(r[j:])
            return res
        def ms(a):
            if len(a) <= 1: return a
            mid = len(a) // 2
            return merge(ms(a[:mid]), ms(a[mid:]))
        self._data = ms(self._data)
    def range_query(self, m1: float, m2: float) -> "ComplexVector":
        tmp = [c for c in self._data if m1 <= c.mod < m2]
        tmp.sort()
        return ComplexVector(tmp)
    def __repr__(self):
        return "ComplexVector" + str(self._data)

def demo():
    print("=== ComplexVector 功能演示 ===")
    n = 20
    data = [Complex(random.randint(-10, 10), random.randint(-10, 10)) for _ in range(n)]
    vec = ComplexVector(data)
    print("初始:", vec)
    vec.shuffle()
    print("置乱:", vec)
    target = vec._data[5]
    print("查找", target, "结果下标:", vec.find(target))
    vec.insert(0, Complex(3, 4))
    print("插入(3+4j):", vec)
    vec.remove(0)
    print("删除头:", vec)
    vec.uniquify()
    print("唯一化后长度:", len(vec._data))

    # 排序效率对比
    for name, order in [("顺序", 0), ("乱序", 1), ("逆序", 2)]:
        test = [Complex(random.randint(-50, 50), random.randint(-50, 50)) for _ in range(200)]
        if order == 0:      test.sort()
        elif order == 2:    test.sort(reverse=True)
        v1, v2 = ComplexVector(test.copy()), ComplexVector(test.copy())
        t0 = time.perf_counter(); v1.bubble_sort(); t1 = time.perf_counter()
        t2 = time.perf_counter(); v2.merge_sort(); t3 = time.perf_counter()
        print(f"{name}: 起泡{t1-t0:.4f}s  归并{t3-t2:.4f}s")

    vec_sorted = ComplexVector(data); vec_sorted.merge_sort()
    sub = vec_sorted.range_query(5, 10)
    print("模[5,10)区间:", sub)

if __name__ == "__main__":
    demo()
