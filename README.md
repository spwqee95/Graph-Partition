---

# Random Graph Generator with Resource Constraints

This tool generates **connected undirected graphs** with weighted vertices and edges, and supports **multiple resource constraints per partition**. It outputs two text files: one describing the graph and another describing partition limits. Optionally, it will also **visualize the graph** (if it's small enough).

---

## Features

* Random graph generation (ensures connectivity)
* Configurable:

  * Number of vertices
  * Edge weight and vertex resource ranges
  * Resource types and partition capacities
* **Vertex weight is treated as resource\[0]**
* Validation of total resource usage vs partition capacity
* Saves:

  * `graph.txt`: vertex + edge info
  * `graph_part.txt`: partition resource limits
  * `graph.png`: optional visualization if `< 20` vertices

---

## Usage

```bash
python gen_graph2.py \
  --num_vertices 6 \
  --max_edges_per_vertex 5 \
  --vertex_weight_range 1 10 \
  --edge_weight_range 1 5 \
  --num_resources 1 \
  --resource_weight_range 1 5 \
  --k_partitions 2 \
  --partition_max_resources 15 20  10 15 \
  --output demo_graph.txt
```

### Explanation:

| Argument                    | Description                                                  |
| --------------------------- | ------------------------------------------------------------ |
| `--num_vertices`            | Total number of nodes                                        |
| `--max_edges_per_vertex`    | Max random degree                                            |
| `--vertex_weight_range`     | Vertex weight range (used as resource\[0])                   |
| `--edge_weight_range`       | Edge weight range                                            |
| `--num_resources`           | Number of *additional* resources per vertex                  |
| `--resource_weight_range`   | Value range for each resource                                |
| `--k_partitions`            | Number of partitions                                         |
| `--partition_max_resources` | Flattened list of resource capacities per partition          |
| `--output`                  | Filename for output (creates `X.txt`, `X_part.txt`, `X.png`) |

---

## Output Format

### `demo_graph.txt`

```
<num_vertices> <num_edges>
<resource[0]=weight> <resource[1]> ... <neighbor_index> <edge_weight> ...
```

### `demo_graph_part.txt`

```
<k_partitions>
<num_resources_including_weight>
<resource_0 capacity for partition 1> <partition 2> ...
...
```

---

## Example Visualization

If your graph has < 20 vertices, it will save a plot as:

```
demo_graph.png
```

---

## Dependencies

Make sure to install:

```bash
pip install networkx matplotlib
```

---
