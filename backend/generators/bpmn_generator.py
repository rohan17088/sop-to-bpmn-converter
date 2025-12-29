from lxml import etree
from models.process_model import ProcessModel
from models.bpmn_elements import BPMNElement, StartEvent, EndEvent, Task, ExclusiveGateway, SequenceFlow


class BPMNGenerator:
    NAMESPACES = {
        'bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL',
        'bpmndi': 'http://www.omg.org/spec/BPMN/20100524/DI',
        'dc': 'http://www.omg.org/spec/DD/20100524/DC',
        'di': 'http://www.omg.org/spec/DD/20100524/DI',
    }
    
    def __init__(self):
        self._nsmap = {None: self.NAMESPACES['bpmn']}
        self._nsmap.update(self.NAMESPACES)
    
    def generate(self, model: ProcessModel) -> str:
        root = self._create_definitions(model)
        process = self._create_process(model, root)
        
        for element in model.elements:
            self._add_element(element, process)
        
        for flow in model.flows:
            self._add_flow(flow, process)
        
        self._add_diagram(model, root)
        
        return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8').decode('utf-8')
    
    def _create_definitions(self, model: ProcessModel) -> etree.Element:
        return etree.Element('definitions', nsmap=self._nsmap, id='Definitions_1', targetNamespace='http://bpmn.io/schema/bpmn')
    
    def _create_process(self, model: ProcessModel, parent: etree.Element) -> etree.Element:
        return etree.SubElement(parent, 'process', id=model.id, name=model.name, isExecutable='true')
    
    def _add_element(self, element: BPMNElement, parent: etree.Element) -> None:
        if isinstance(element, StartEvent):
            etree.SubElement(parent, 'startEvent', id=element.id, name=element.name or 'Start')
        elif isinstance(element, EndEvent):
            etree.SubElement(parent, 'endEvent', id=element.id, name=element.name or 'End')
        elif isinstance(element, Task):
            etree.SubElement(parent, 'task', id=element.id, name=element.name)
        elif isinstance(element, ExclusiveGateway):
            etree.SubElement(parent, 'exclusiveGateway', id=element.id, name=element.name)
    
    def _add_flow(self, flow: SequenceFlow, parent: etree.Element) -> None:
        attrs = {'id': flow.id, 'sourceRef': flow.source_ref, 'targetRef': flow.target_ref}
        if flow.name:
            attrs['name'] = flow.name
        
        flow_elem = etree.SubElement(parent, 'sequenceFlow', **attrs)
        if flow.condition_label:
            flow_elem.set('name', flow.condition_label)
    
    def _add_diagram(self, model: ProcessModel, root: etree.Element) -> None:
        bpmndi = '{' + self.NAMESPACES['bpmndi'] + '}'
        dc = '{' + self.NAMESPACES['dc'] + '}'
        
        diagram = etree.SubElement(root, f'{bpmndi}BPMNDiagram', id='BPMNDiagram_1')
        plane = etree.SubElement(diagram, f'{bpmndi}BPMNPlane', id='BPMNPlane_1', bpmnElement=model.id)
        
        for element in model.elements:
            shape = etree.SubElement(plane, f'{bpmndi}BPMNShape', id=f'{element.id}_di', bpmnElement=element.id)
            etree.SubElement(shape, f'{dc}Bounds', x=str(element.x), y=str(element.y), width=str(element.width), height=str(element.height))
        
        for flow in model.flows:
            etree.SubElement(plane, f'{bpmndi}BPMNEdge', id=f'{flow.id}_di', bpmnElement=flow.id)
