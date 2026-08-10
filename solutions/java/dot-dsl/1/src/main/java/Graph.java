import java.util.ArrayList;
import java.util.Collections;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Graph {
    private final Map<String, String> attributes;
    private final List<Node> nodes;
    private final List<Edge> edges;

    public Graph() {
        this(new HashMap<>());
    }

    public Graph(Map<String, String> attributes) {
        this.attributes = new HashMap<>(attributes);
        this.nodes = new ArrayList<>();
        this.edges = new ArrayList<>();
    }

    public Collection<Node> getNodes() {
        return Collections.unmodifiableList(nodes);
    }

    public Collection<Edge> getEdges() {
        return Collections.unmodifiableList(edges);
    }

    public Graph node(String name) {
        return node(name, new HashMap<>());
    }

    public Graph node(String name, Map<String, String> attributes) {
        nodes.add(new Node(name, attributes));
        return this;
    }

    public Graph edge(String start, String end) {
        return edge(start, end, new HashMap<>());
    }

    public Graph edge(String start, String end, Map<String, String> attributes) {
        edges.add(new Edge(start, end, attributes));
        return this;
    }

    public Map<String, String> getAttributes() {
        return Collections.unmodifiableMap(attributes);
    }
}