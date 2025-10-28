#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
largest_rectangle.py
给定非负整数数组 heights，求柱状图能勾勒出的最大矩形面积。
单调栈 O(n) 实现，并随机生成 10 组数据演示。
"""
import random
from typing import List

class ArrayStack:
    def __init__(self):
        self._s = []
    def push(self, e):      self._s.append(e)
    def pop(self):          return self._s.pop()
    def top(self):          return self._s[-1]
    def empty(self):        return len(self._s) == 0

def largestRectangleArea(heights: List[int]) -> int:
    st = ArrayStack()
    st.push(-1)
    heights = heights + [0]          # 尾部哨兵
    max_a = 0
    for i, h in enumerate(heights):
        while st.top() != -1 and heights[st.top()] > h:
            H = heights[st.pop()]
            W = i - st.top() - 1
            max_a = max(max_a, H * W)
        st.push(i)
    return max_a

def demo():
    print("=== 柱状图最大矩形演示 ===")
    random.seed(0)
    for i in range(10):
        n = random.randint(1, 20)          # 可改 1e5
        h = [random.randint(0, 10) for _ in range(n)]
        area = largestRectangleArea(h)
        print(f"heights={h}  =>  maxArea={area}")

if __name__ == "__main__":
    demo()
