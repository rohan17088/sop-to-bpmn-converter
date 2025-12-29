from .base_parser import BaseSOPParser
from .text_parser import TextSOPParser
from .docx_parser import DocxSOPParser


class ParserFactory:
    _parsers = {
        'txt': TextSOPParser,
        'text': TextSOPParser,
        'docx': DocxSOPParser,
        'doc': DocxSOPParser,
    }
    
    @classmethod
    def create_parser(cls, file_type: str) -> BaseSOPParser:
        file_type = file_type.lower().strip('.')
        parser_class = cls._parsers.get(file_type)
        
        if parser_class is None:
            supported = ', '.join(cls._parsers.keys())
            raise ValueError(f"Unsupported file type: {file_type}. Supported: {supported}")
        
        return parser_class()
    
    @classmethod
    def get_parser_for_file(cls, filename: str) -> BaseSOPParser:
        if '.' not in filename:
            return TextSOPParser()
        extension = filename.rsplit('.', 1)[-1]
        return cls.create_parser(extension)
    
    @classmethod
    def register_parser(cls, file_type: str, parser_class: type) -> None:
        cls._parsers[file_type.lower()] = parser_class
