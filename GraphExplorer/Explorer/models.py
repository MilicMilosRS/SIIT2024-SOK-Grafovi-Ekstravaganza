from django.db import models

class Node(models.Model):
    id = models.IntegerField(primary_key=True)  # custom ID
    properties = models.JSONField(default=dict)

    def __str__(self):
        return f"Node {self.id} - {self.properties.get('Name', '')}"

class Edge(models.Model):
    id = models.IntegerField(primary_key=True)
    properties = models.JSONField(default=dict)
    source = models.ForeignKey(Node, related_name="outgoing_edges", on_delete=models.CASCADE)
    target = models.ForeignKey(Node, related_name="incoming_edges", on_delete=models.CASCADE)

    def __str__(self):
        return f"Edge {self.id} - {self.properties.get('Name', '')}"