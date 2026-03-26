import sys
from collections import defaultdict
from heapq import heappush, heappop

def solve():
    input_data = sys.stdin.buffer.read().split()
    ptr = 0
    def rd():
        nonlocal ptr
        v = int(input_data[ptr]); ptr += 1; return v

    n = rd()
    grid = []
    for i in range(n):
        row = [int(input_data[ptr + j]) for j in range(n)]
        ptr += n
        grid.append(row)
    m = rd()

    if grid[0][0] == -1 or grid[n-1][n-1] == -1:
        sys.stdout.write("0\n"); return

    # Collect metro stations
    station_pos = {}
    for i in range(n):
        gi = grid[i]
        for j in range(n):
            if gi[j] <= -2:
                station_pos[gi[j]] = (i, j)

    # Union-Find for metro branches
    parent = {s: s for s in station_pos}
    def find(x):
        r = x
        while parent[r] != r: r = parent[r]
        while parent[x] != r: parent[x], x = r, parent[x]
        return r

    for _ in range(m):
        a, b = rd(), rd()
        ra, rb = find(a), find(b)
        if ra != rb: parent[ra] = rb

    branches = defaultdict(list)
    for s in station_pos:
        branches[find(s)].append(s)

    # Graph as flat arrays with linked-list adjacency
    NN = 2 * n * n + 2
    S = 2 * n * n
    T = S + 1
    n2 = 2 * n

    # Estimate max edges needed
    max_edges = 7 * n * n + 10000
    me2 = max_edges * 2

    # Use lists for speed
    eto = [0] * me2
    ecap = [0] * me2
    ecost = [0] * me2
    erev = [0] * me2
    enxt = [0] * me2  # will fill with -1 effectively via head
    head = [-1] * NN
    ec = 0

    # Inline edge addition for speed
    # ae(u, v, cap, cost): adds forward edge u->v and reverse v->u
    for i in range(n):
        gi = grid[i]
        base_i = n2 * i
        for j in range(n):
            v = gi[j]
            if v == -1:
                continue
            inn = base_i + (j << 1)
            out = inn + 1

            # IN -> OUT
            if v > 0:
                # edge 1: cap=1, cost=-v
                eto[ec] = out; ecap[ec] = 1; ecost[ec] = -v; erev[ec] = ec+1
                enxt[ec] = head[inn]; head[inn] = ec
                eto[ec+1] = inn; ecap[ec+1] = 0; ecost[ec+1] = v; erev[ec+1] = ec
                enxt[ec+1] = head[out]; head[out] = ec+1
                ec += 2
                # edge 2: cap=1, cost=0
                eto[ec] = out; ecap[ec] = 1; ecost[ec] = 0; erev[ec] = ec+1
                enxt[ec] = head[inn]; head[inn] = ec
                eto[ec+1] = inn; ecap[ec+1] = 0; ecost[ec+1] = 0; erev[ec+1] = ec
                enxt[ec+1] = head[out]; head[out] = ec+1
                ec += 2
            else:
                eto[ec] = out; ecap[ec] = 2; ecost[ec] = 0; erev[ec] = ec+1
                enxt[ec] = head[inn]; head[inn] = ec
                eto[ec+1] = inn; ecap[ec+1] = 0; ecost[ec+1] = 0; erev[ec+1] = ec
                enxt[ec+1] = head[out]; head[out] = ec+1
                ec += 2

            # Right: OUT(i,j) -> IN(i,j+1)
            if j + 1 < n and gi[j+1] != -1:
                nv = inn + 2
                eto[ec] = nv; ecap[ec] = 2; ecost[ec] = 0; erev[ec] = ec+1
                enxt[ec] = head[out]; head[out] = ec
                eto[ec+1] = out; ecap[ec+1] = 0; ecost[ec+1] = 0; erev[ec+1] = ec
                enxt[ec+1] = head[nv]; head[nv] = ec+1
                ec += 2

            # Down: OUT(i,j) -> IN(i+1,j)
            if i + 1 < n and grid[i+1][j] != -1:
                nv = inn + n2
                eto[ec] = nv; ecap[ec] = 2; ecost[ec] = 0; erev[ec] = ec+1
                enxt[ec] = head[out]; head[out] = ec
                eto[ec+1] = out; ecap[ec+1] = 0; ecost[ec+1] = 0; erev[ec+1] = ec
                enxt[ec+1] = head[nv]; head[nv] = ec+1
                ec += 2

    # S -> IN(0,0)
    eto[ec] = 0; ecap[ec] = 2; ecost[ec] = 0; erev[ec] = ec+1
    enxt[ec] = head[S]; head[S] = ec
    eto[ec+1] = S; ecap[ec+1] = 0; ecost[ec+1] = 0; erev[ec+1] = ec
    enxt[ec+1] = head[0]; head[0] = ec+1
    ec += 2

    # OUT(n-1,n-1) -> T
    outn = n2*(n-1) + ((n-1)<<1) + 1
    eto[ec] = T; ecap[ec] = 2; ecost[ec] = 0; erev[ec] = ec+1
    enxt[ec] = head[outn]; head[outn] = ec
    eto[ec+1] = outn; ecap[ec+1] = 0; ecost[ec+1] = 0; erev[ec+1] = ec
    enxt[ec+1] = head[T]; head[T] = ec+1
    ec += 2

    # Metro edges
    for br, sts in branches.items():
        ls = len(sts)
        if ls < 2: continue
        for ai in range(ls):
            a = sts[ai]
            ra, ca = station_pos[a]
            outa = n2*ra + (ca<<1) + 1
            for bi in range(ls):
                if ai == bi: continue
                b = sts[bi]
                rb, cb = station_pos[b]
                if ra <= rb and ca <= cb:
                    inb = n2*rb + (cb<<1)
                    eto[ec] = inb; ecap[ec] = 2; ecost[ec] = 0; erev[ec] = ec+1
                    enxt[ec] = head[outa]; head[outa] = ec
                    eto[ec+1] = outa; ecap[ec+1] = 0; ecost[ec+1] = 0; erev[ec+1] = ec
                    enxt[ec+1] = head[inb]; head[inb] = ec+1
                    ec += 2

    INF = float('inf')

    # ========== Pass 1: DAG shortest path ==========
    dist = [INF] * NN
    pve = [-1] * NN
    dist[S] = 0

    # Relax from S
    e = head[S]
    while e != -1:
        if ecap[e] > 0:
            nd = ecost[e]
            tv = eto[e]
            if nd < dist[tv]:
                dist[tv] = nd
                pve[tv] = e
        e = enxt[e]

    # Process anti-diagonals
    for s in range(2*n - 1):
        lo = s - n + 1
        if lo < 0: lo = 0
        hi = s
        if hi >= n: hi = n - 1
        for i in range(lo, hi + 1):
            j = s - i
            if grid[i][j] == -1:
                continue
            # Relax IN(i,j)
            u = n2*i + (j<<1)
            du = dist[u]
            if du < INF:
                e = head[u]
                while e != -1:
                    if ecap[e] > 0:
                        nd = du + ecost[e]
                        tv = eto[e]
                        if nd < dist[tv]:
                            dist[tv] = nd
                            pve[tv] = e
                    e = enxt[e]
            # Relax OUT(i,j)
            u += 1
            du = dist[u]
            if du < INF:
                e = head[u]
                while e != -1:
                    if ecap[e] > 0:
                        nd = du + ecost[e]
                        tv = eto[e]
                        if nd < dist[tv]:
                            dist[tv] = nd
                            pve[tv] = e
                    e = enxt[e]

    if dist[T] >= INF:
        sys.stdout.write("0\n"); return

    # Augment
    bn = 2
    v = T
    while v != S:
        e = pve[v]
        c = ecap[e]
        if c < bn: bn = c
        v = eto[erev[e]]
    v = T
    while v != S:
        e = pve[v]
        ecap[e] -= bn
        ecap[erev[e]] += bn
        v = eto[erev[e]]

    flow = bn
    cost_total = bn * dist[T]

    if flow >= 2:
        sys.stdout.write(f"{-cost_total}\n"); return

    # ========== Pass 2: Dijkstra with Johnson potentials ==========
    h = dist  # potentials
    dist2 = [INF] * NN
    pve2 = [-1] * NN
    vis = bytearray(NN)
    dist2[S] = 0

    heap = [(0, S)]
    while heap:
        d, u = heappop(heap)
        if vis[u]: continue
        vis[u] = 1
        if u == T: break
        hu = h[u]
        if hu >= INF: continue
        e = head[u]
        while e != -1:
            if ecap[e] > 0:
                tv = eto[e]
                if not vis[tv]:
                    hv = h[tv]
                    if hv < INF:
                        nd = d + ecost[e] + hu - hv
                        if nd < dist2[tv]:
                            dist2[tv] = nd
                            pve2[tv] = e
                            heappush(heap, (nd, tv))
            e = enxt[e]

    if dist2[T] >= INF:
        sys.stdout.write("0\n"); return

    v = T
    while v != S:
        e = pve2[v]
        ecap[e] -= 1
        ecap[erev[e]] += 1
        v = eto[erev[e]]

    cost_total += dist2[T] + h[T]
    sys.stdout.write(f"{-cost_total}\n")

solve()