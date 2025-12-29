from abc import ABC, abstractmethod
from typing import List, Tuple
import re
from models.sop_elements import SOPElement, SOPStep, SOPDecision, SOPFlow


class BaseSOPParser(ABC):
    DECISION_KEYWORDS = ['if', 'check', 'verify', 'determine', 'evaluate', 'assess', 'review', 'confirm', 'validate']
    YES_KEYWORDS = ['if yes', 'if true', 'yes:', 'if so', 'when yes']
    NO_KEYWORDS = ['if no', 'if not', 'if false', 'no:', 'otherwise', 'else']
    
    @abstractmethod
    def extract_text(self, source: str) -> str:
        pass
    
    def parse(self, source: str) -> List[SOPElement]:
        text = self.extract_text(source)
        lines = self._split_into_lines(text)
        steps = self._extract_numbered_steps(lines)
        return self._identify_elements(steps)
    
    def _split_into_lines(self, text: str) -> List[str]:
        lines = text.strip().split('\n')
        return [line.strip() for line in lines if line.strip()]
    
    def _extract_numbered_steps(self, lines: List[str]) -> List[Tuple[int, str]]:
        steps = []
        step_patterns = [
            r'^(\d+)\.\s*(.+)$',
            r'^(\d+)\)\s*(.+)$',
            r'^Step\s*(\d+)[:\.]?\s*(.+)$',
        ]
        
        for line in lines:
            for pattern in step_patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    step_num = int(match.group(1))
                    step_text = match.group(2).strip()
                    steps.append((step_num, step_text))
                    break
        
        return steps
    
    def _identify_elements(self, steps: List[Tuple[int, str]]) -> List[SOPElement]:
        elements = []
        i = 0
        
        while i < len(steps):
            step_num, text = steps[i]
            
            if self._is_decision(text):
                decision, consumed = self._parse_decision(steps, i)
                elements.append(decision)
                i += consumed
            else:
                step = SOPStep(text=text, step_number=step_num, order=len(elements))
                elements.append(step)
                i += 1
        
        return elements
    
    def _is_decision(self, text: str) -> bool:
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.DECISION_KEYWORDS)
    
    def _is_yes_branch(self, text: str) -> bool:
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.YES_KEYWORDS)
    
    def _is_no_branch(self, text: str) -> bool:
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.NO_KEYWORDS)
    
    def _parse_decision(self, steps: List[Tuple[int, str]], start_idx: int) -> Tuple[SOPDecision, int]:
        step_num, condition_text = steps[start_idx]
        
        decision = SOPDecision(
            text=condition_text,
            condition=self._extract_condition(condition_text),
            order=start_idx
        )
        
        consumed = 1
        yes_flow = SOPFlow(label="Yes")
        no_flow = SOPFlow(label="No")
        
        i = start_idx + 1
        while i < len(steps):
            _, text = steps[i]
            
            if self._is_yes_branch(text):
                action = self._extract_branch_action(text)
                if action:
                    yes_flow.add_step(SOPStep(text=action, step_number=steps[i][0]))
                consumed += 1
                i += 1
            elif self._is_no_branch(text):
                action = self._extract_branch_action(text)
                if action:
                    no_flow.add_step(SOPStep(text=action, step_number=steps[i][0]))
                consumed += 1
                i += 1
            else:
                break
        
        decision.yes_branch = yes_flow if yes_flow.steps else None
        decision.no_branch = no_flow if no_flow.steps else None
        
        return decision, consumed
    
    def _extract_condition(self, text: str) -> str:
        text = re.sub(r'^(check|verify|determine|evaluate)\s+(if\s+)?', '', text, flags=re.IGNORECASE)
        return text.strip().rstrip('.')
    
    def _extract_branch_action(self, text: str) -> str:
        patterns = [
            r'^if\s+(yes|no|true|false)[,:]?\s*',
            r'^(yes|no)[,:]?\s*',
            r'^(otherwise|else)[,:]?\s*'
        ]
        
        result = text
        for pattern in patterns:
            result = re.sub(pattern, '', result, flags=re.IGNORECASE)
        
        return result.strip()
