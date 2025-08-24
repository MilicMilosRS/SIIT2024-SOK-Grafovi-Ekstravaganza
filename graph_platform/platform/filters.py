from abc import ABC, abstractmethod

from operator import eq, ne, gt, lt, ge, le

class Filter(ABC):
    @abstractmethod
    def apply(self, vertices: dict) -> dict:
        pass

    @abstractmethod
    def serialize(self) -> dict:
        pass

class SearchFilter(Filter):
    def __init__(self, attribute: str):
        self.attribute = attribute
        self.type = "search"

    def apply(self, vertices: dict) -> dict:
        return { key: node for key, node in vertices.items()
                    if any(self.attribute in str(k) or self.attribute in str(v)
                        for k, v in node._attributes.items()) }
    
    def serialize(self):
        return {"type": self.type, "attribute": self.attribute}

class FilterFilter(Filter):
    def __init__(self, attribute: str, type: str, value: str):
        self.attribute = attribute
        self.type = type
        self.value = value
        match self.type:
            case ">":
                self.operand = gt
            case "<":
                self.operand = lt
            case ">=":
                self.operand = ge
            case "<=":
                self.operand = le
            case "==":
                self.operand = eq
            case "!=":
                self.operand = ne
                
    def apply(self, vertices: dict) -> dict:
        return { key: node for key, node in vertices.items()
                 if self.attribute in node._attributes and self.operand(node._attributes[self.attribute], self.value) }
    
    def serialize(self):
        return {"value": self.value, "type": self.type, "attribute": self.attribute}