import sys
from collections import defaultdict
from heapq import heappush, heappop

def main():
    data = sys.stdin.buffer.read().split()
    p = 0
    n = int(data[p]); p += 1
    g = []
    for i in range(n):
        row = [int(data[p + j]) for j in range(n)]
        p += n
        g.append(row)
    m = int(data[p]); p += 1

    if g[0][0] == -1 or g[n - 1][n - 1] == -1:
        print(0); return

    sp = {}
    for i in range(n):
        for j in range(n):
            if g[i][j] <= -2:
                sp[g[i][j]] = (i, j)

    par = {s: s for s in sp}
    def find(x):
        r = x
        while par[r] != r: r = par[r]
        while x != r: par[x], x = r, par[x]
        return r

    for _ in range(m):
        a, b = int(data[p]), int(data[p + 1]); p += 2
        ra, rb = find(a), find(b)
        if ra != rb: par[ra] = rb

    branches = defaultdict(list)
    for s in sp:
        branches[find(s)].append(s)

    NN = 2 * n * n + 2; S = NN - 2; T = NN - 1; n2 = 2 * n
    me2 = (8 * n * n + 20000) * 2
    eto = [0]*me2; ecap = [0]*me2; ecost = [0]*me2; erev = [0]*me2; enxt = [0]*me2
    head = [-1]*NN; ec = 0

    for i in range(n):
        gi = g[i]; bi = n2 * i
        for j in range(n):
            v = gi[j]
            if v == -1: continue
            inn = bi + (j << 1); out = inn + 1
            if v > 0:
                eto[ec]=out;ecap[ec]=1;ecost[ec]=-v;erev[ec]=ec+1;enxt[ec]=head[inn];head[inn]=ec
                eto[ec+1]=inn;ecap[ec+1]=0;ecost[ec+1]=v;erev[ec+1]=ec;enxt[ec+1]=head[out];head[out]=ec+1;ec+=2
                eto[ec]=out;ecap[ec]=1;ecost[ec]=0;erev[ec]=ec+1;enxt[ec]=head[inn];head[inn]=ec
                eto[ec+1]=inn;ecap[ec+1]=0;ecost[ec+1]=0;erev[ec+1]=ec;enxt[ec+1]=head[out];head[out]=ec+1;ec+=2
            else:
                eto[ec]=out;ecap[ec]=2;ecost[ec]=0;erev[ec]=ec+1;enxt[ec]=head[inn];head[inn]=ec
                eto[ec+1]=inn;ecap[ec+1]=0;ecost[ec+1]=0;erev[ec+1]=ec;enxt[ec+1]=head[out];head[out]=ec+1;ec+=2
            if j+1<n and gi[j+1]!=-1:
                nv=inn+2
                eto[ec]=nv;ecap[ec]=2;ecost[ec]=0;erev[ec]=ec+1;enxt[ec]=head[out];head[out]=ec
                eto[ec+1]=out;ecap[ec+1]=0;ecost[ec+1]=0;erev[ec+1]=ec;enxt[ec+1]=head[nv];head[nv]=ec+1;ec+=2
            if i+1<n and g[i+1][j]!=-1:
                nv=inn+n2
                eto[ec]=nv;ecap[ec]=2;ecost[ec]=0;erev[ec]=ec+1;enxt[ec]=head[out];head[out]=ec
                eto[ec+1]=out;ecap[ec+1]=0;ecost[ec+1]=0;erev[ec+1]=ec;enxt[ec+1]=head[nv];head[nv]=ec+1;ec+=2

    eto[ec]=0;ecap[ec]=2;ecost[ec]=0;erev[ec]=ec+1;enxt[ec]=head[S];head[S]=ec
    eto[ec+1]=S;ecap[ec+1]=0;ecost[ec+1]=0;erev[ec+1]=ec;enxt[ec+1]=head[0];head[0]=ec+1;ec+=2
    outn=n2*(n-1)+((n-1)<<1)+1
    eto[ec]=T;ecap[ec]=2;ecost[ec]=0;erev[ec]=ec+1;enxt[ec]=head[outn];head[outn]=ec
    eto[ec+1]=outn;ecap[ec+1]=0;ecost[ec+1]=0;erev[ec+1]=ec;enxt[ec+1]=head[T];head[T]=ec+1;ec+=2

    for _, sts in branches.items():
        if len(sts) < 2: continue
        for a in sts:
            ra, ca = sp[a]; oa = n2*ra+(ca<<1)+1
            for b in sts:
                if a != b:
                    rb, cb = sp[b]
                    if ra <= rb and ca <= cb:
                        ib = n2*rb+(cb<<1)
                        eto[ec]=ib;ecap[ec]=2;ecost[ec]=0;erev[ec]=ec+1;enxt[ec]=head[oa];head[oa]=ec
                        eto[ec+1]=oa;ecap[ec+1]=0;ecost[ec+1]=0;erev[ec+1]=ec;enxt[ec+1]=head[ib];head[ib]=ec+1;ec+=2

    INF = float('inf')
    dist = [INF]*NN; pve = [-1]*NN; dist[S] = 0
    e = head[S]
    while e != -1:
        if ecap[e] > 0:
            nd = ecost[e]; tv = eto[e]
            if nd < dist[tv]: dist[tv] = nd; pve[tv] = e
        e = enxt[e]
    for s in range(2*n-1):
        lo = max(0, s-n+1); hi = min(s, n-1)
        for i in range(lo, hi+1):
            j = s-i
            if g[i][j] == -1: continue
            u = n2*i+(j<<1); du = dist[u]
            if du < INF:
                e = head[u]
                while e != -1:
                    if ecap[e] > 0:
                        nd = du+ecost[e]; tv = eto[e]
                        if nd < dist[tv]: dist[tv] = nd; pve[tv] = e
                    e = enxt[e]
            u += 1; du = dist[u]
            if du < INF:
                e = head[u]
                while e != -1:
                    if ecap[e] > 0:
                        nd = du+ecost[e]; tv = eto[e]
                        if nd < dist[tv]: dist[tv] = nd; pve[tv] = e
                    e = enxt[e]
    if dist[T] >= INF: print(0); return
    bn = 2; v = T
    while v != S:
        e = pve[v]
        if ecap[e] < bn: bn = ecap[e]
        v = eto[erev[e]]
    v = T
    while v != S:
        e = pve[v]; ecap[e] -= bn; ecap[erev[e]] += bn; v = eto[erev[e]]
    flow = bn; ct = bn * dist[T]
    if flow >= 2: print(-ct); return

    h = dist; d2 = [INF]*NN; pv2 = [-1]*NN; vis = bytearray(NN); d2[S] = 0
    hp = [(0, S)]
    while hp:
        d, u = heappop(hp)
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
                        nd = d+ecost[e]+hu-hv
                        if nd < d2[tv]: d2[tv] = nd; pv2[tv] = e; heappush(hp, (nd, tv))
            e = enxt[e]
    if d2[T] >= INF: print(0); return
    v = T
    while v != S:
        e = pv2[v]; ecap[e] -= 1; ecap[erev[e]] += 1; v = eto[erev[e]]
    ct += d2[T]+h[T]
    print(-ct)

main()