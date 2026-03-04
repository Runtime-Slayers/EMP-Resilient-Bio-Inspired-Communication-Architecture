"""
EMP-Resilient Bio-Inspired Communication Architecture
Hybrid Fibre-Optic-Ionic-Acoustic Mesh with Self-Healing Routing
"""
import numpy as np
import heapq

def generate_mesh_network(n_nodes=50, connectivity=0.15, seed=42):
    np.random.seed(seed)
    adj = np.random.rand(n_nodes, n_nodes) < connectivity
    adj = ((adj + adj.T) > 0).astype(float)
    np.fill_diagonal(adj, 0)
    # Assign link types: 0=fibre, 1=ionic, 2=acoustic
    link_type = (np.random.rand(n_nodes, n_nodes) * 3).astype(int)
    link_type = np.triu(link_type) + np.triu(link_type, 1).T
    return adj, link_type

def emp_event(adj, link_type, emp_radius=0.3, seed=1):
    """Kill electronic links within EMP radius; optical/ionic survive."""
    np.random.seed(seed)
    damaged = adj.copy()
    # Electronic nodes fail with probability proportional to EMP
    node_fail = np.random.rand(adj.shape[0]) < emp_radius
    for i in np.where(node_fail)[0]:
        # Only electronic links fail (type 0 = fibre ok, type 2 acoustic partial)
        for j in range(adj.shape[1]):
            if damaged[i, j] and link_type[i, j] == 0:  # fibre survives EMP
                pass
            elif damaged[i, j] and link_type[i, j] == 2:  # acoustic survives
                pass
            else:
                damaged[i, j] = damaged[j, i] = 0
    return damaged, node_fail

def dijkstra(adj, src, dst):
    n = adj.shape[0]
    dist = [np.inf] * n
    dist[src] = 0
    pq = [(0, src)]
    prev = [-1] * n
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v in range(n):
            if adj[u, v] and dist[u] + 1 < dist[v]:
                dist[v] = dist[u] + 1
                prev[v] = u
                heapq.heappush(pq, (dist[v], v))
    if dist[dst] == np.inf:
        return None, np.inf
    path = []
    cur = dst
    while cur != -1:
        path.append(cur)
        cur = prev[cur]
    return list(reversed(path)), dist[dst]

def self_healing_route(adj_original, adj_damaged, src=0, dst=49):
    path_orig, hops_orig = dijkstra(adj_original, src, dst)
    path_heal, hops_heal = dijkstra(adj_damaged, src, dst)
    return path_orig, hops_orig, path_heal, hops_heal

if __name__ == "__main__":
    print("Generating bio-inspired mesh network (50 nodes)...")
    adj, link_type = generate_mesh_network(50)
    print(f"  Total links: {int(adj.sum()//2)}")
    adj_dmg, failed = emp_event(adj, link_type)
    print(f"  EMP failed nodes: {int(failed.sum())}")
    p_orig, h_orig, p_heal, h_heal = self_healing_route(adj, adj_dmg)
    print(f"  Pre-EMP path  : {h_orig} hops")
    if p_heal:
        print(f"  Post-EMP path : {h_heal} hops (self-healed)")
    else:
        print("  Post-EMP path : DISCONNECTED")
    print("EMP resilient comms simulation complete.")
