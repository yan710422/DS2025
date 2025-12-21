import random, time, math, csv, os, sys
from typing import List, Tuple, Dict, Callable

Box = Tuple[float, float, float, float, float]

def quick_sort(arr: List[Tuple[float, int]]) -> List[Tuple[float, int]]:
    if len(arr) <= 1:
        return arr[:]
    pivot = arr[len(arr)//2][0]
    left  = [x for x in arr if x[0] > pivot]
    mid   = [x for x in arr if x[0] == pivot]
    right = [x for x in arr if x[0] < pivot]
    return quick_sort(left) + mid + quick_sort(right)

def merge_sort(arr: List[Tuple[float, int]]) -> List[Tuple[float, int]]:
    if len(arr) <= 1:
        return arr[:]
    m = len(arr)//2
    left, right = merge_sort(arr[:m]), merge_sort(arr[m:])
    return _merge(left, right)

def _merge(left, right):
    res, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i][0] >= right[j][0]:
            res.append(left[i]); i += 1
        else:
            res.append(right[j]); j += 1
    res.extend(left[i:]); res.extend(right[j:])
    return res

def heap_sort(arr: List[Tuple[float, int]]) -> List[Tuple[float, int]]:
    import heapq
    h = [(-s, i) for s, i in arr]
    heapq.heapify(h)
    return [(-s, i) for s, i in [heapq.heappop(h) for _ in range(len(h))]]

def shell_sort(arr: List[Tuple[float, int]]) -> List[Tuple[float, int]]:
    a, n = arr[:], len(arr)
    gap = n // 2
    while gap:
        for i in range(gap, n):
            tmp, j = a[i], i
            while j >= gap and a[j-gap][0] < tmp[0]:
                a[j] = a[j-gap]; j -= gap
            a[j] = tmp
        gap //= 2
    return a

SORT_DICT: Dict[str, Callable] = {
    "quick": quick_sort,
    "merge": merge_sort,
    "heap":  heap_sort,
    "shell": shell_sort,
}

def random_boxes(n: int, size=500) -> List[Box]:
    boxes = []
    for _ in range(n):
        x1 = random.randint(0, size-20)
        y1 = random.randint(0, size-20)
        w  = random.randint(20, 80)
        h  = random.randint(20, 80)
        x2 = min(x1+w, size); y2 = min(y1+h, size)
        boxes.append((x1, y1, x2, y2, random.random()))
    return boxes

def cluster_boxes(n: int, clusters=5, size=500) -> List[Box]:
    boxes = []
    for _ in range(n):
        cx = random.randint(50, size-50)
        cy = random.randint(50, size-50)
        x1 = cx + random.randint(-30, 30)
        y1 = cy + random.randint(-30, 30)
        w  = random.randint(20, 60); h = random.randint(20, 60)
        x2 = min(x1+w, size); y2 = min(y1+h, size)
        boxes.append((x1, y1, x2, y2, random.random()))
    return boxes

def iou(a: Box, b: Box) -> float:
    x1 = max(a[0], b[0]); y1 = max(a[1], b[1])
    x2 = min(a[2], b[2]); y2 = min(a[3], b[3])
    inter = max(0, x2-x1) * max(0, y2-y1)
    area_a = (a[2]-a[0])*(a[3]-a[1])
    area_b = (b[2]-b[0])*(b[3]-b[1])
    return inter / (area_a+area_b-inter+1e-8)

def nms(boxes: List[Box], sort_func) -> List[Box]:
    if not boxes:
        return []
    si = [(boxes[i][4], i) for i in range(len(boxes))]
    order = [idx for _, idx in sort_func(si)]
    keep = []; suppressed = [False]*len(boxes)
    for i in order:
        if suppressed[i]: continue
        keep.append(boxes[i])
        for j in range(len(boxes)):
            if suppressed[j]: continue
            if iou(boxes[i], boxes[j]) > 0.5:
                suppressed[j] = True
    return keep

SIZES = [100, 500, 1000, 2000, 5000, 10000]
DIST  = ["random", "cluster"]
REPEAT = 5

def run_once(n, dist):
    gen = random_boxes if dist == "random" else cluster_boxes
    boxes = gen(n)
    times = {}
    for name, fn in SORT_DICT.items():
        t0 = time.perf_counter()
        nms(boxes, fn)
        t1 = time.perf_counter()
        times[name] = (t1-t0)*1000
    return times

def main():
    csv_path = "results.csv"
    with open(csv_path, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["dist", "n", "quick", "merge", "heap", "shell"])
        # 控制台表格
        print("----------- 不同排序算法在 NMS 中的性能对比（n=5000） -----------")
        base_line = {}
        for dist in DIST:
            print(f"[{dist} distribution]")
            for n in [5000]:
                t = run_once(n, dist)
                if dist == "random":
                    base_line = t
                print(f"n={n:5}  " + "  ".join(f"{k:>7}:{v:7.2f}ms" for k, v in t.items()))
        print("\n相对 quick (random) 的比值：")
        for k in SORT_DICT:
            print(f"{k:>7}: {base_line[k]/base_line['quick']:.2f}x")

        print("\n----------- 数据规模对性能的影响（random） -----------")
        for n in SIZES:
            t = run_once(n, "random")
            print(f"n={n:5}  " + "  ".join(f"{k:>7}:{v:7.2f}ms" for k, v in t.items()))
            writer.writerow(["random", n] + [t[k] for k in SORT_DICT])

        print("\n----------- 数据分布对性能的影响（n=5000） -----------")
        for dist in DIST:
            t = run_once(5000, dist)
            print(f"{dist:>7}  " + "  ".join(f"{k:>7}:{v:7.2f}ms" for k, v in t.items()))
            writer.writerow([dist, 5000] + [t[k] for k in SORT_DICT])

    print(f"\n原始数据已写入 {os.path.abspath(csv_path)}")

if __name__ == "__main__":
    main()
