from dataclasses import dataclass, field
from typing import List, Optional
from .bpmn_elements import BPMNElement, StartEvent, EndEvent, Task, ExclusiveGateway, SequenceFlow


@dataclass
class ProcessModel:
    id: str = "process_1"
    name: str = "Process"
    elements: List[BPMNElement] = field(default_factory=list)
    flows: List[SequenceFlow] = field(default_factory=list)
    
    def add_element(self, element: BPMNElement) -> None:
        self.elements.append(element)
    
    def add_flow(self, flow: SequenceFlow) -> None:
        self.flows.append(flow)
    
    def connect(self, source: BPMNElement, target: BPMNElement, label: str = "") -> SequenceFlow:
        flow = SequenceFlow(source_ref=source.id, target_ref=target.id, condition_label=label)
        self.add_flow(flow)
        return flow
    
    def get_start_event(self) -> Optional[StartEvent]:
        for elem in self.elements:
            if isinstance(elem, StartEvent):
                return elem
        return None
    
    def get_end_events(self) -> List[EndEvent]:
        return [elem for elem in self.elements if isinstance(elem, EndEvent)]
    
    def get_tasks(self) -> List[Task]:
        return [elem for elem in self.elements if isinstance(elem, Task)]
    
    def get_gateways(self) -> List[ExclusiveGateway]:
        return [elem for elem in self.elements if isinstance(elem, ExclusiveGateway)]
