import argparse
import random
import networkx as nx
import matplotlib.pyplot as plt

def generate_connected_random_weighted_graph(num_vertices, max_edges_per_vertex=10,
                                              vertex_weight_range=(1, 10), edge_weight_range=(1, 10),
                                              num_resources=0, resource_weight_range=(1, 5)):
    edges = set()
    adjacency = [[] for _ in range(num_vertices)]

    vertex_weights = [random.randint(*vertex_weight_range) for _ in range(num_vertices)]
    vertex_extra_resources = [
        [random.randint(*resource_weight_range) for _ in range(num_resources)]
        for _ in range(num_vertices)
    ]

    # weight: resource[0]
    vertex_resources = [
        [vertex_weights[i]] + vertex_extra_resources[i] for i in range(num_vertices)
    ]

    # Spanning tree
    vertices = list(range(num_vertices))
    random.shuffle(vertices)
    for i in range(1, num_vertices):
        u = vertices[i]
        v = random.choice(vertices[:i])
        weight = random.randint(*edge_weight_range)
        edges.add((min(u, v), max(u, v), weight))
        adjacency[u].append((v, weight))
        adjacency[v].append((u, weight))

    # adding edge to target degree
    for u in range(num_vertices):
        current_neighbors = {v for v, _ in adjacency[u]}
        possible_edges = set(range(num_vertices)) - {u} - current_neighbors
        target_degree = random.randint(2, max_edges_per_vertex)
        while len(adjacency[u]) < target_degree and possible_edges:
            v = random.choice(list(possible_edges))
            possible_edges.remove(v)
            weight = random.randint(*edge_weight_range)
            edge = (min(u, v), max(u, v), weight)
            if edge not in edges:
                edges.add(edge)
                adjacency[u].append((v, weight))
                adjacency[v].append((u, weight))

    return vertex_resources, adjacency, len(edges)

def save_graph_file(graph_filename, vertex_resources, adjacency, num_edges):
    with open(graph_filename, "w") as f:
        num_vertices = len(vertex_resources)
        f.write(f"{num_vertices} {num_edges}\n")
        for u in range(num_vertices):
            line = list(map(str, vertex_resources[u]))
            for v, w in adjacency[u]:
                line += [str(v + 1), str(w)]
            f.write(" ".join(line) + "\n")

def save_partition_file(partition_filename, k_partitions, num_resources, partition_max_resources):
    with open(partition_filename, "w") as f:
        f.write(f"{k_partitions}\n")
        f.write(f"{num_resources + 1}\n")
        for r in range(num_resources + 1):
            f.write(" ".join(str(partition_max_resources[r][p]) for p in range(k_partitions)) + "\n")

def validate_resources(vertex_resources, partition_max_resources):
    valid = True
    num_resources = len(vertex_resources[0])
    total_resource_usage = [0] * num_resources
    for res_vec in vertex_resources:
        for r in range(num_resources):
            total_resource_usage[r] += res_vec[r]

    print("\nValidation Summary:")
    for r in range(num_resources):
        r_capacity = sum(partition_max_resources[r])
        if total_resource_usage[r] > r_capacity:
            print(f"Resource {r}: usage {total_resource_usage[r]} > capacity {r_capacity}")
            valid = False
        else:
            print(f"Resource {r}: usage {total_resource_usage[r]} <= capacity {r_capacity}")
    return valid

def visualize_graph(vertex_resources, adjacency, output_path="graph_visualization.png"):
    num_vertices = len(vertex_resources)
    if num_vertices >= 20:
        print("Graph has >= 20 vertices. Skipping visualization.")
        return

    G = nx.Graph()
    for u in range(num_vertices):
        G.add_node(u, label=str(u), weight=vertex_resources[u][0])

    for u, neighbors in enumerate(adjacency):
        for v, w in neighbors:
            if u < v:  # avoid duplicates
                G.add_edge(u, v, weight=w)

    pos = nx.spring_layout(G, seed=42)
    labels = {i: f"{i}" for i in G.nodes()}
    edge_labels = nx.get_edge_attributes(G, 'weight')

    plt.figure(figsize=(8, 6))
    nx.draw(G, pos, with_labels=True, labels=labels, node_size=500, node_color='skyblue', font_size=10)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
    plt.title("Graph Visualization (saved to file)")
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Graph image saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate graph and partition files with weight as resource[0].")
    parser.add_argument("--num_vertices", type=int, required=True)
    parser.add_argument("--max_edges_per_vertex", type=int, default=10)
    parser.add_argument("--vertex_weight_range", type=int, nargs=2, default=[1, 10])
    parser.add_argument("--edge_weight_range", type=int, nargs=2, default=[1, 10])
    parser.add_argument("--num_resources", type=int, default=0)
    parser.add_argument("--resource_weight_range", type=int, nargs=2, default=[1, 5])
    parser.add_argument("--k_partitions", type=int, required=True)
    parser.add_argument("--partition_max_resources", type=int, nargs='+', required=True)
    parser.add_argument("--output", type=str, default="test_graph.txt")
    args = parser.parse_args()

    total_resources = args.num_resources + 1
    expected = total_resources * args.k_partitions
    assert len(args.partition_max_resources) == expected, f"Expected {expected} values for partition_max_resources"

    partition_max_resources = [
        args.partition_max_resources[r * args.k_partitions:(r + 1) * args.k_partitions]
        for r in range(total_resources)
    ]

    vertex_resources, adjacency, num_edges = generate_connected_random_weighted_graph(
        num_vertices=args.num_vertices,
        max_edges_per_vertex=args.max_edges_per_vertex,
        vertex_weight_range=tuple(args.vertex_weight_range),
        edge_weight_range=tuple(args.edge_weight_range),
        num_resources=args.num_resources,
        resource_weight_range=tuple(args.resource_weight_range)
    )

    is_valid = validate_resources(vertex_resources, partition_max_resources)

    graph_file = args.output
    partition_file = args.output.replace(".txt", "_part.txt")

    save_graph_file(graph_file, vertex_resources, adjacency, num_edges)
    save_partition_file(partition_file, args.k_partitions, args.num_resources, partition_max_resources)

    print(f"\nGraph file saved to: {graph_file}")
    print(f"Partition file saved to: {partition_file}")
    if not is_valid:
        print("Warning: Resource constraints violated.")

    # Visualization if small
    if args.num_vertices < 20:
        img_file = args.output.replace(".txt", ".png")
        visualize_graph(vertex_resources, adjacency, output_path=img_file)

if __name__ == "__main__":
    main()
