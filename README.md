# Random Graph Generator with Resource Constraints

`gen_graph.py` generates **connected undirected graphs** with weighted vertices and edges, where **vertex weight is treated as resource\[0]**, and supports **multiple resource constraints across partitions**. Capacities are automatically derived from vertex usage and user-defined **resource utilization rates**.

---

## Features

* Random connected graph generation
* Automatic resource capacity calculation per partition
* Flexible CLI inputs with sensible defaults:

  * Number of vertices
  * Number of partitions
  * Number of resources (in addition to weight)
  * Resource utilization rate (per resource)
  * Resource allocation ratios among partitions
  * Weight and edge range customization
* Graph output (`.txt`), partition parameters (k partition, m resources, and resource capacities) (`_part.txt`)
* Optional visualization if vertex count < 20 (`.png`)
* Prints full graph summary after generation

---

## Usage Example

```bash
python gen_graph2.py \
  --num_vertices 10 \
  --num_resources 2 \
  --k_partitions 3 \
  --partition_max_resources_ratio 0.3 0.4 0.3 \
  --resource_util_rate 0.9 0.2 0.5 \
  --output demo_graph.txt
```

---

## ⚙️ CLI Arguments

| Argument                          | Description                                                               |
| --------------------------------- | ------------------------------------------------------------------------- |
| `--num_vertices`                  | Number of vertices                                                        |
| `--num_resources`                 | Number of *additional* resources (not including weight)                   |
| `--k_partitions`                  | Number of partitions                                                      |
| `--partition_max_resources_ratio` | List of k floats that sum to 1.0; determines each partition’s share       |
| `--resource_util_rate`            | Utilization rate **per resource** (including weight as resource\[0])      |
| `--vertex_weight_range`           | Min and max weight of vertex (default: 1 10)                              |
| `--edge_weight_range`             | Min and max edge weight (default: 1 5)                                    |
| `--resource_weight_range`         | Min and max value for each additional resource (default: 1 10)            |
| `--output`                        | Base filename (e.g. `graph.txt`, generates `graph_part.txt`, `graph.png`) |

---

## Output Format

### `graph.txt`

```
<num_vertices> <num_edges>
<weight> <resource1> <resource2> ... <neighbor> <edge_weight> ...
```

### `graph_part.txt`

```
<k_partitions>
<num_resources (including weight)>
<resource_0 partition_1 capacity> ... <partition_k>
<resource_1 partition_1 capacity> ... <partition_k>
...
```

---

## Visualization

If `num_vertices < 20`, the graph will be visualized as:

```
graph.png
```

Each node is labeled with its index; edge weights are displayed.

---

## Printed Graph Summary

After generation, you will see:

* Total vertices and edges
* Average vertex degree
* For each resource:

  * Total used
  * Partition capacity
  * Target utilization
  * Actual utilization

---

## Dependencies

Install with:

```bash
pip install networkx matplotlib
```

---
