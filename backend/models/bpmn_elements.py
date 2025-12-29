from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import uuid


@dataclass
class BPMNElement(ABC):
    id: str = field(default_factory=lambda: f"elem_{uuid.uuid4().hex[:8]}")
    name: str = ""
    x: int = 0
    y: int = 0
    width: int = 100
    height: int = 80
    
    @abstractmethod
    def element_type(self) -> str:
        pass


@dataclass
class StartEvent(BPMNElement):
    def __post_init__(self):
        self.width = 36
        self.height = 36
        if not self.id.startswith("start"):
            self.id = f"start_{uuid.uuid4().hex[:8]}"
    
    def element_type(self) -> str:
        return "startEvent"


@dataclass
class EndEvent(BPMNElement):
    def __post_init__(self):
        self.width = 36
        self.height = 36
        if not self.id.startswith("end"):
            self.id = f"end_{uuid.uuid4().hex[:8]}"
    
    def element_type(self) -> str:
        return "endEvent"


@dataclass
class Task(BPMNElement):
    def __post_init__(self):
        if not self.id.startswith("task"):
            self.id = f"task_{uuid.uuid4().hex[:8]}"
    
    def element_type(self) -> str:
        return "task"


@dataclass
class ExclusiveGateway(BPMNElement):
    def __post_init__(self):
        self.width = 50
        self.height = 50
        if not self.id.startswith("gateway"):
            self.id = f"gateway_{uuid.uuid4().hex[:8]}"
    
    def element_type(self) -> str:
        return "exclusiveGateway"


@dataclass
class SequenceFlow(BPMNElement):
    source_ref: str = ""
    target_ref: str = ""
    condition_label: str = ""
    
    def __post_init__(self):
        if not self.id.startswith("flow"):
            self.id = f"flow_{uuid.uuid4().hex[:8]}"
    
    def element_type(self) -> str:
        return "sequenceFlow"
