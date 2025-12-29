from typing import List, Tuple
from models.sop_elements import SOPElement, SOPStep, SOPDecision
from models.bpmn_elements import StartEvent, EndEvent, Task, ExclusiveGateway
from models.process_model import ProcessModel


class SOPToBPMNConverter:
    START_X = 150
    START_Y = 200
    HORIZONTAL_SPACING = 150
    VERTICAL_SPACING = 100
    
    def __init__(self):
        self._current_x = self.START_X
        self._current_y = self.START_Y
    
    def convert(self, sop_elements: List[SOPElement], process_name: str = "SOP Process") -> ProcessModel:
        model = ProcessModel(name=process_name)
        self._reset_position()
        
        start = self._create_start_event()
        model.add_element(start)
        last_elements = [start]
        
        for sop_elem in sop_elements:
            if isinstance(sop_elem, SOPStep):
                task, last_elements = self._process_step(sop_elem, last_elements, model)
            elif isinstance(sop_elem, SOPDecision):
                last_elements = self._process_decision(sop_elem, last_elements, model)
        
        end = self._create_end_event()
        model.add_element(end)
        
        for elem in last_elements:
            model.connect(elem, end)
        
        return model
    
    def _reset_position(self) -> None:
        self._current_x = self.START_X
        self._current_y = self.START_Y
    
    def _advance_x(self) -> int:
        self._current_x += self.HORIZONTAL_SPACING
        return self._current_x
    
    def _create_start_event(self) -> StartEvent:
        return StartEvent(name="Process Started", x=self._current_x, y=self._current_y)
    
    def _create_end_event(self) -> EndEvent:
        return EndEvent(name="Process Completed", x=self._advance_x(), y=self._current_y)
    
    def _process_step(self, step: SOPStep, last_elements: List, model: ProcessModel) -> Tuple[Task, List]:
        task = Task(name=step.text, x=self._advance_x(), y=self._current_y)
        model.add_element(task)
        
        for elem in last_elements:
            model.connect(elem, task)
        
        return task, [task]
    
    def _process_decision(self, decision: SOPDecision, last_elements: List, model: ProcessModel) -> List:
        gateway = ExclusiveGateway(name=decision.condition + "?", x=self._advance_x(), y=self._current_y)
        model.add_element(gateway)
        
        for elem in last_elements:
            model.connect(elem, gateway)
        
        branch_ends = []
        base_y = self._current_y
        
        if decision.yes_branch and decision.yes_branch.steps:
            yes_y = base_y - self.VERTICAL_SPACING // 2
            for step in decision.yes_branch.steps:
                if isinstance(step, SOPStep):
                    task = Task(name=step.text, x=self._advance_x(), y=yes_y)
                    model.add_element(task)
                    model.connect(gateway, task, "Yes")
                    branch_ends.append(task)
            self._current_x -= self.HORIZONTAL_SPACING
        else:
            branch_ends.append(gateway)
        
        if decision.no_branch and decision.no_branch.steps:
            no_y = base_y + self.VERTICAL_SPACING // 2
            for step in decision.no_branch.steps:
                if isinstance(step, SOPStep):
                    task = Task(name=step.text, x=self._advance_x(), y=no_y)
                    model.add_element(task)
                    model.connect(gateway, task, "No")
                    branch_ends.append(task)
        
        self._current_y = base_y
        return branch_ends if branch_ends else [gateway]
