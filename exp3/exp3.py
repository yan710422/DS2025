import sys
from collections import deque

class Graph:
    def __init__(self, num_vertices, is_directed=False):
        """初始化图：num_vertices-顶点数，is_directed-是否有向图"""
        self.num_vertices = num_vertices
        self.is_directed = is_directed
        self.adj_matrix = [[0] * num_vertices for _ in range(num_vertices)]  # 邻接矩阵
        self.adj_list = [[] for _ in range(num_vertices)]  # 邻接表（优化遍历效率）

    def add_edge(self, u, v, weight=1):
        """添加边：u、v为顶点编号，weight为权值（默认1，无权图用）"""
        self.adj_matrix[u][v] = weight
        self.adj_list[u].append((v, weight))
        if not self.is_directed:  # 无向图双向添加
            self.adj_matrix[v][u] = weight
            self.adj_list[v].append((u, weight))

    def print_adj_matrix(self, vertex_labels):
        """输出邻接矩阵（vertex_labels为顶点名称列表，如['A','B',...]）"""
        print("邻接矩阵：")
        print("  " + " ".join(vertex_labels))
        for i in range(self.num_vertices):
            row = [str(self.adj_matrix[i][j]) for j in range(self.num_vertices)]
            print(f"{vertex_labels[i]} " + " ".join(row))

    # ------------------------------ （2）BFS和DFS ------------------------------
    def bfs(self, start_idx, vertex_labels):
        """从start_idx（起点编号）出发的BFS遍历"""
        visited = [False] * self.num_vertices
        queue = deque([start_idx])
        visited[start_idx] = True
        bfs_order = []

        while queue:
            u = queue.popleft()
            bfs_order.append(vertex_labels[u])
            # 按顶点编号排序，保证遍历顺序一致
            for v, _ in sorted(self.adj_list[u], key=lambda x: x[0]):
                if not visited[v]:
                    visited[v] = True
                    queue.append(v)
        return bfs_order

    def dfs_recursive(self, u, visited, dfs_order, vertex_labels):
        """DFS递归辅助函数"""
        visited[u] = True
        dfs_order.append(vertex_labels[u])
        # 按顶点编号排序
        for v, _ in sorted(self.adj_list[u], key=lambda x: x[0]):
            if not visited[v]:
                self.dfs_recursive(v, visited, dfs_order, vertex_labels)

    def dfs(self, start_idx, vertex_labels):
        """从start_idx出发的DFS遍历（递归实现）"""
        visited = [False] * self.num_vertices
        dfs_order = []
        self.dfs_recursive(start_idx, visited, dfs_order, vertex_labels)
        return dfs_order

    # ------------------------------ （3）最短路径和最小支撑树 ------------------------------
    def dijkstra(self, start_idx, vertex_labels):
        """Dijkstra算法：从start_idx出发的最短路径（带权图，权值非负）"""
        INF = float('inf')
        dist = [INF] * self.num_vertices  # 起点到各顶点的最短距离
        dist[start_idx] = 0
        visited = [False] * self.num_vertices

        for _ in range(self.num_vertices):
            # 选距离最小的未访问顶点
            min_dist = INF
            u = -1
            for i in range(self.num_vertices):
                if not visited[i] and dist[i] < min_dist:
                    min_dist = dist[i]
                    u = i
            if u == -1:
                break  # 无可达顶点
            visited[u] = True

            # 松弛操作
            for v, weight in self.adj_list[u]:
                if not visited[v] and dist[u] + weight < dist[v]:
                    dist[v] = dist[u] + weight

        # 格式化输出
        print("\nDijkstra最短路径（起点：{}）：".format(vertex_labels[start_idx]))
        for i in range(self.num_vertices):
            if dist[i] == INF:
                print(f"{vertex_labels[start_idx]} -> {vertex_labels[i]}: 不可达")
            else:
                print(f"{vertex_labels[start_idx]} -> {vertex_labels[i]}: {dist[i]}")
        return dist

    def prim(self, start_idx, vertex_labels):
        """Prim算法：从start_idx出发的最小支撑树（MST）"""
        INF = float('inf')
        key = [INF] * self.num_vertices  # 各顶点到MST的最小权值
        parent = [-1] * self.num_vertices  # MST中各顶点的父节点
        visited = [False] * self.num_vertices

        key[start_idx] = 0

        for _ in range(self.num_vertices):
            # 选key最小的未访问顶点
            min_key = INF
            u = -1
            for i in range(self.num_vertices):
                if not visited[i] and key[i] < min_key:
                    min_key = key[i]
                    u = i
            if u == -1:
                break  # 图不连通，无法生成MST
            visited[u] = True

            # 更新邻接顶点的key
            for v, weight in self.adj_list[u]:
                if not visited[v] and weight < key[v]:
                    key[v] = weight
                    parent[v] = u

        # 输出MST
        print("\nPrim最小支撑树（起点：{}）：".format(vertex_labels[start_idx]))
        mst_weight = 0
        for i in range(self.num_vertices):
            if parent[i] != -1:
                print(f"{vertex_labels[parent[i]]} - {vertex_labels[i]} (权值：{key[i]})")
                mst_weight += key[i]
        print(f"MST总权值：{mst_weight}")
        return parent, mst_weight

    # ------------------------------ （4）双连通分量与关节点 ------------------------------
    def tarjan_bcc(self, start_idx, vertex_labels):
        """Tarjan算法：计算双连通分量（BCC）和关节点（割点）"""
        visited = [False] * self.num_vertices
        disc = [0] * self.num_vertices  # 发现时间
        low = [0] * self.num_vertices   # 能到达的最早发现时间的顶点
        parent = [-1] * self.num_vertices
        articulation_points = set()  # 关节点集合
        bcc = []  # 双连通分量列表（每个分量为边的集合）
        stack = []  # 存储当前边
        time = 0

        def dfs(u):
            nonlocal time
            children = 0
            visited[u] = True
            disc[u] = low[u] = time
            time += 1

            for v, _ in self.adj_list[u]:
                if not visited[v]:
                    parent[v] = u
                    children += 1
                    stack.append((u, v))
                    dfs(v)

                    # 更新low[u]
                    low[u] = min(low[u], low[v])

                    # 情况1：根节点且子节点数>=2
                    if parent[u] == -1 and children > 1:
                        articulation_points.add(u)
                        # 弹出当前BCC
                        component = []
                        while stack[-1] != (u, v):
                            component.append(stack.pop())
                        component.append(stack.pop())
                        bcc.append(component)

                    # 情况2：非根节点，low[v] >= disc[u]
                    if parent[u] != -1 and low[v] >= disc[u]:
                        articulation_points.add(u)
                        # 弹出当前BCC
                        component = []
                        while stack[-1] != (u, v):
                            component.append(stack.pop())
                        component.append(stack.pop())
                        bcc.append(component)

                elif v != parent[u] and disc[v] < disc[u]:  # 回边（避免重复处理父节点）
                    stack.append((u, v))
                    low[u] = min(low[u], disc[v])

        # 处理非连通图（本题图2为连通图，此处兼容一般情况）
        dfs(start_idx)
        # 处理栈_idx)
        # 处理栈中剩余的边（最后一个BCC）
        if stack:
            bcc.append(stack.copy())
            stack.clear()

        # 格式化输出
        print(f"\n起点{vertex_labels[start_idx]}的双连通分量（BCC）：")
        for i, component in enumerate(bcc, 1):
            edges = [(vertex_labels[u], vertex_labels[v]) for u, v in component]
            print(f"BCC{i}：{edges}")

        print(f"\n起点{vertex_labels[start_idx]}的关节点（割点）：")
        ap_labels = [vertex_labels[ap] for ap in articulation_points]
        print(ap_labels if ap_labels else "无关节点")

        return bcc, articulation_points

# ------------------------------ 测试代码 ------------------------------
if __name__ == "__main__":
    # ------------------------------ （1）图1：邻接矩阵 + （2）BFS/DFS + （3）最短路径/MST ------------------------------
    # 图1初始化
    vertex_labels1 = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    graph1 = Graph(num_vertices=8, is_directed=False)
    # 添加图1的边（u, v, weight）
    edges1 = [
        (0,1,2), (0,2,3), (1,3,4), (1,4,12), (2,4,1), (2,7,10),
        (3,4,13), (3,5,6), (4,5,5), (4,6,14), (5,6,11), (6,7,8), (1,5,9)
    ]
    for u, v, w in edges1:
        graph1.add_edge(u, v, w)

    # （1）输出图1邻接矩阵
    print("="*50)
    print("图1相关结果：")
    print("="*50)
    graph1.print_adj_matrix(vertex_labels1)

    # （2）BFS和DFS（起点A，编号0）
    bfs_order = graph1.bfs(start_idx=0, vertex_labels=vertex_labels1)
    print("\nBFS遍历顺序（起点A）：", " -> ".join(bfs_order))
    dfs_order = graph1.dfs(start_idx=0, vertex_labels=vertex_labels1)
    print("DFS遍历顺序（起点A）：", " -> ".join(dfs_order))

    # （3）最短路径（Dijkstra）和最小支撑树（Prim）
    graph1.dijkstra(start_idx=0, vertex_labels=vertex_labels1)
    graph1.prim(start_idx=0, vertex_labels=vertex_labels1)

    # ------------------------------ （4）图2：双连通分量与关节点（不同起点测试） ------------------------------
    # 图2初始化
    vertex_labels2 = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
    graph2 = Graph(num_vertices=12, is_directed=False)
    # 添加图2的边（u, v）（无权图）
    edges2 = [
        (0,1), (0,2), (1,2), (1,3), (2,3), (3,4), (4,5), (5,6),
        (6,7), (7,8), (8,9), (9,10), (10,11)
    ]
    for u, v in edges2:
        graph2.add_edge(u, v)

    # 测试不同起点（A=0、D=3、H=7）
    print("\n" + "="*50)
    print("图2相关结果（双连通分量+关节点）：")
    print("="*50)
    start_indices2 = [0, 3, 7]  # 起点A、D、H
    for idx in start_indices2:
        graph2.tarjan_bcc(start_idx=idx, vertex_labels=vertex_labels2)
        print("-"*30)