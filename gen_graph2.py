import argparse
import random
import networkx as nx
import matplotlib.pyplot as plt

def generate_connected_random_weighted_graph(num_vertices, max_edges_per_vertex=6,
                                              vertex_weight_range=(1, 10), edge_weight_range=(1, 5),
                                              num_resources=0, resource_weight_range=(1, 10)):
    edges = set()
    adjacency = [[] for _ in range(num_vertices)]
    vertex_weights = [random.randint(*vertex_weight_range) for _ in range(num_vertices)]
    vertex_extra_resources = [
        [random.randint(*resource_weight_range) for _ in range(num_resources)]
        for _ in range(num_vertices)
    ]
    vertex_resources = [[vertex_weights[i]] + vertex_extra_resources[i] for i in range(num_vertices)]

    vertices = list(range(num_vertices))
    random.shuffle(vertices)
    for i in range(1, num_vertices):
        u, v = vertices[i], random.choice(vertices[:i])
        weight = random.randint(*edge_weight_range)
        edges.add((min(u, v), max(u, v), weight))
        adjacency[u].append((v, weight))
        adjacency[v].append((u, weight))

    for u in range(num_vertices):
        current_neighbors = {v for v, _ in adjacency[u]}
        possible_edges = set(range(num_vertices)) - {u} - current_neighbors
        while len(adjacency[u]) < random.randint(2, max_edges_per_vertex) and possible_edges:
            v = random.choice(list(possible_edges))
            possible_edges.remove(v)
            weight = random.randint(*edge_weight_range)
            if (min(u, v), max(u, v), weight) not in edges:
                edges.add((min(u, v), max(u, v), weight))
                adjacency[u].append((v, weight))
                adjacency[v].append((u, weight))

    return vertex_resources, adjacency, len(edges)

def compute_partition_caps_v2(vertex_resources, num_resources, k_partitions,
                               partition_max_resources_ratio, resource_util_rates):
    assert abs(sum(partition_max_resources_ratio) - 1.0) < 1e-6, "partition_max_resources_ratio must sum to 1"
    total_resources = num_resources + 1
    assert len(resource_util_rates) == total_resources, "You must provide a utilization rate for each resource"

    total_usage = [0] * total_resources
    for res in vertex_resources:
        for i in range(total_resources):
            total_usage[i] += res[i]

    total_capacity = [int(total_usage[r] / resource_util_rates[r]) for r in range(total_resources)]
    partition_caps = []
    for r in range(total_resources):
        caps = [int(total_capacity[r] * ratio) for ratio in partition_max_resources_ratio]
        delta = total_capacity[r] - sum(caps)
        caps[0] += delta
        partition_caps.append(caps)
    return partition_caps

def save_graph_file(filename, vertex_resources, adjacency, num_edges):
    with open(filename, "w") as f:
        f.write(f"{len(vertex_resources)} {num_edges}\n")
        for u, res in enumerate(vertex_resources):
            line = list(map(str, res))
            for v, w in adjacency[u]:
                line += [str(v + 1), str(w)]
            f.write(" ".join(line) + "\n")

def save_partition_file(filename, k, partition_caps):
    with open(filename, "w") as f:
        f.write(f"{k}\n")
        f.write(f"{len(partition_caps)}\n")
        for r in partition_caps:
            f.write(" ".join(map(str, r)) + "\n")

def visualize_graph(vertex_resources, adjacency, output_path):
    if len(vertex_resources) >= 20:
        print("Graph has >= 20 vertices. Skipping visualization.")
        return
    G = nx.Graph()
    for u in range(len(vertex_resources)):
        G.add_node(u, label=str(u), weight=vertex_resources[u][0])
    for u, neighbors in enumerate(adjacency):
        for v, w in neighbors:
            if u < v:
                G.add_edge(u, v, weight=w)
    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(8, 6))
    nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=500)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G, 'weight'))
    plt.title("Graph Visualization")
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Graph image saved to: {output_path}")

def print_graph_summary(vertex_resources, adjacency, partition_caps, resource_util_rates):
    num_vertices = len(vertex_resources)
    num_edges = sum(len(n) for n in adjacency) // 2
    num_resources = len(vertex_resources[0])
    total_usage = [0] * num_resources

    for res in vertex_resources:
        for i in range(num_resources):
            total_usage[i] += res[i]

    avg_degree = sum(len(n) for n in adjacency) / num_vertices

    print("\nGraph Summary:")
    print(f"- Vertices: {num_vertices}")
    print(f"- Edges: {num_edges}")
    print(f"- Average vertex degree: {avg_degree:.2f}")
    for i in range(num_resources):
        total_cap = sum(partition_caps[i])
        utilization = total_usage[i] / total_cap if total_cap > 0 else 0
        print(f"  o Resource {i}:")
        print(f"    - Total used: {total_usage[i]}")
        print(f"    - Total capacity: {total_cap}")
        print(f"    - Target utilization rate: {resource_util_rates[i]}")
        print(f"    - Actual utilization: {utilization:.2%}")

def main():
    parser = argparse.ArgumentParser(description="Generate graph and partition files with resource-based utilization.")
    parser.add_argument("--num_vertices", type=int, required=True)
    parser.add_argument("--num_resources", type=int, required=True)
    parser.add_argument("--k_partitions", type=int, required=True)
    parser.add_argument("--partition_max_resources_ratio", type=float, nargs='+', required=True)
    parser.add_argument("--resource_util_rate", type=float, nargs='+', required=True,
                        help="Utilization rate per resource (must include vertex weight as resource[0])")
    parser.add_argument("--vertex_weight_range", type=int, nargs=2, default=[1, 10],
                        help="Min and max vertex weight (default: 1 10)")
    parser.add_argument("--edge_weight_range", type=int, nargs=2, default=[1, 5],
                        help="Min and max edge weight (default: 1 5)")
    parser.add_argument("--resource_weight_range", type=int, nargs=2, default=[1, 10],
                        help="Min and max resource weight (default: 1 10)")
    parser.add_argument("--output", type=str, default="graph.txt")
    args = parser.parse_args()

    vertex_resources, adjacency, num_edges = generate_connected_random_weighted_graph(
        num_vertices=args.num_vertices,
        num_resources=args.num_resources,
        vertex_weight_range=tuple(args.vertex_weight_range),
        edge_weight_range=tuple(args.edge_weight_range),
        resource_weight_range=tuple(args.resource_weight_range)
    )

    partition_caps = compute_partition_caps_v2(
        vertex_resources,
        num_resources=args.num_resources,
        k_partitions=args.k_partitions,
        partition_max_resources_ratio=args.partition_max_resources_ratio,
        resource_util_rates=args.resource_util_rate
    )

    save_graph_file(args.output, vertex_resources, adjacency, num_edges)
    save_partition_file(args.output.replace(".txt", "_part.txt"), args.k_partitions, partition_caps)

    if args.num_vertices < 20:
        visualize_graph(vertex_resources, adjacency, output_path=args.output.replace(".txt", ".png"))

    print_graph_summary(vertex_resources, adjacency, partition_caps, args.resource_util_rate)

if __name__ == "__main__":
    main()
