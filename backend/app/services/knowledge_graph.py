from typing import List, Dict, Any
from collections import deque

class KnowledgeGraphService:
    def __init__(self):
        self.adj = {}
        self._build_graph()

    def _add_edge(self, u: str, v: str):
        if u not in self.adj:
            self.adj[u] = []
        self.adj[u].append(v)

    def _build_graph(self):
        edges = [
            ("HTML/CSS", "JavaScript"),
            ("JavaScript", "TypeScript"),
            ("JavaScript", "React"),
            ("React", "Next.js"),
            ("React", "Redux"),
            ("JavaScript", "Node.js"),
            ("Node.js", "Express.js"),
            ("Node.js", "REST APIs"),
            ("SQL", "PostgreSQL"),
            ("SQL", "MongoDB"),
            ("Python", "Pandas"),
            ("Pandas", "Machine Learning"),
            ("Machine Learning", "Deep Learning"),
            ("Machine Learning", "Data Visualization"),
            ("Python", "Statistics"),
            ("Linux", "Docker"),
            ("Docker", "Kubernetes"),
            ("Docker", "CI/CD"),
            ("AWS", "Terraform"),
            ("JavaScript", "React Native"),
            ("Kotlin", "Android SDK"),
            ("Swift", "iOS Development")
        ]
        for u, v in edges:
            self._add_edge(u, v)

    def find_shortest_learning_path(self, start_skill: str, target_skill: str) -> List[str]:
        if start_skill == target_skill:
            return [start_skill]
            
        queue = deque([[start_skill]])
        visited = {start_skill}

        while queue:
            path = queue.popleft()
            node = path[-1]

            if node == target_skill:
                return path

            for neighbor in self.adj.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(path + [neighbor])

        return [start_skill, target_skill]

knowledge_graph_service = KnowledgeGraphService()
