from dataclasses import dataclass, field
from typing import Optional, List
from abc import ABC
import uuid


@dataclass
class SOPElement(ABC):
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    text: str = ""
    order: int = 0


@dataclass
class SOPStep(SOPElement):
    step_number: int = 0
    
    def __str__(self) -> str:
        return f"Step {self.step_number}: {self.text}"


@dataclass
class SOPDecision(SOPElement):
    condition: str = ""
    yes_branch: Optional['SOPFlow'] = None
    no_branch: Optional['SOPFlow'] = None
    
    def __str__(self) -> str:
        return f"Decision: {self.condition}?"


@dataclass  
class SOPFlow:
    label: str = ""
    steps: List[SOPElement] = field(default_factory=list)
    
    def add_step(self, step: SOPElement) -> None:
        self.steps.append(step)
