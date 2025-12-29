from .base_parser import BaseSOPParser


class TextSOPParser(BaseSOPParser):
    def extract_text(self, source: str) -> str:
        if source.endswith('.txt'):
            try:
                with open(source, 'r', encoding='utf-8') as f:
                    return f.read()
            except FileNotFoundError:
                return source
        return source
