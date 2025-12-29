from typing import Optional, Dict, Any
from dataclasses import dataclass
from parsers import ParserFactory, BaseSOPParser
from converters import SOPToBPMNConverter
from generators import BPMNGenerator
from models import ProcessModel


@dataclass
class ConversionResult:
    success: bool
    bpmn_xml: Optional[str] = None
    process_model: Optional[ProcessModel] = None
    error: Optional[str] = None
    stats: Optional[Dict[str, Any]] = None


class ConversionService:
    def __init__(self):
        self._converter = SOPToBPMNConverter()
        self._generator = BPMNGenerator()
    
    def convert_file(self, file_path: str, process_name: str = "SOP Process") -> ConversionResult:
        try:
            parser = ParserFactory.get_parser_for_file(file_path)
            return self._execute_conversion(parser, file_path, process_name)
        except Exception as e:
            return ConversionResult(success=False, error=str(e))
    
    def convert_text(self, text: str, process_name: str = "SOP Process") -> ConversionResult:
        try:
            parser = ParserFactory.create_parser('text')
            return self._execute_conversion(parser, text, process_name)
        except Exception as e:
            return ConversionResult(success=False, error=str(e))
    
    def convert_bytes(self, content: bytes, filename: str, process_name: str = "SOP Process") -> ConversionResult:
        try:
            parser = ParserFactory.get_parser_for_file(filename)
            return self._execute_conversion(parser, content, process_name)
        except Exception as e:
            return ConversionResult(success=False, error=str(e))
    
    def _execute_conversion(self, parser: BaseSOPParser, source: Any, process_name: str) -> ConversionResult:
        sop_elements = parser.parse(source)
        
        if not sop_elements:
            return ConversionResult(success=False, error="No SOP elements found in the document")
        
        process_model = self._converter.convert(sop_elements, process_name)
        bpmn_xml = self._generator.generate(process_model)
        
        stats = {
            'sop_elements': len(sop_elements),
            'bpmn_elements': len(process_model.elements),
            'bpmn_flows': len(process_model.flows),
            'tasks': len(process_model.get_tasks()),
            'gateways': len(process_model.get_gateways())
        }
        
        return ConversionResult(success=True, bpmn_xml=bpmn_xml, process_model=process_model, stats=stats)
