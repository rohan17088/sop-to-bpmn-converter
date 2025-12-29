# SOP to BPMN Converter

A Python application that transforms Standard Operating Procedure (SOP) documents into BPMN 2.0 XML diagrams.

## Architecture Overview

```
┌─────────────┐    ┌──────────────┐    ┌───────────────┐    ┌──────────────┐    ┌─────────────┐
│  SOP Input  │ -> │    Parser    │ -> │  SOP Elements │ -> │   Converter  │ -> │ BPMN Model  │
│ (.docx/.txt)│    │   (Strategy) │    │  (Data Class) │    │   (Mapper)   │    │ (Composite) │
└─────────────┘    └──────────────┘    └───────────────┘    └──────────────┘    └──────┬──────┘
                                                                                       │
                                                                                       v
                                                                               ┌──────────────┐
                                                                               │  Generator   │
                                                                               │  (Builder)   │
                                                                               └──────┬───────┘
                                                                                      │
                                                                                      v
                                                                               ┌──────────────┐
                                                                               │  BPMN 2.0   │
                                                                               │    XML      │
                                                                               └──────────────┘
```

## Design Patterns Used

### 1. Strategy Pattern (Parser Layer)
- `BaseSOPParser` - Abstract interface for parsing
- `TextSOPParser` - Concrete strategy for .txt files
- `DocxSOPParser` - Concrete strategy for .docx files

### 2. Factory Pattern (Parser Factory)
- `ParserFactory` - Creates appropriate parser based on file type
- Supports runtime registration of new parsers

### 3. Template Method Pattern (Base Parser)
- `parse()` method defines the skeleton algorithm
- Subclasses override `extract_text()` for format-specific extraction

### 4. Composite Pattern (BPMN Elements)
- `BPMNElement` base class
- `Task`, `StartEvent`, `EndEvent`, `ExclusiveGateway`, `SequenceFlow`
- Allows uniform treatment of element hierarchy

### 5. Builder Pattern (BPMN Generator)
- Constructs complex BPMN XML structure step by step
- Methods: `_create_definitions()`, `_create_process()`, `_add_element()`

### 6. Facade Pattern (Conversion Service)
- `ConversionService` provides simple interface to complex subsystem
- Orchestrates: Parser -> Converter -> Generator

### 7. Mapper Pattern (Converter)
- `SOPToBPMNConverter` transforms between domain models
- Maps SOP elements to BPMN elements

## Project Structure

```
backend/
├── models/                    # Domain Models
│   ├── sop_elements.py       # SOP data classes (SOPStep, SOPDecision)
│   ├── bpmn_elements.py      # BPMN data classes (Task, Gateway, Flow)
│   └── process_model.py      # Internal process representation
├── parsers/                   # Parser Layer (Strategy Pattern)
│   ├── base_parser.py        # Abstract parser interface
│   ├── text_parser.py        # Text file parser
│   ├── docx_parser.py        # Word document parser
│   └── parser_factory.py     # Factory for parser creation
├── converters/                # Conversion Layer (Mapper)
│   └── sop_to_bpmn.py        # SOP to BPMN conversion logic
├── generators/                # Generator Layer (Builder)
│   └── bpmn_generator.py     # BPMN 2.0 XML generation
├── services/                  # Service Layer (Facade)
│   └── conversion_service.py # Main orchestration service
└── server.py                  # FastAPI REST API
```

## Key Assumptions

1. **SOP Format**: Steps are numbered (e.g., "1. Step text" or "1) Step text")
2. **Decisions**: Detected by keywords (if, check, verify, determine)
3. **Branches**: "If yes" and "If no" patterns for conditional branches
4. **Structure**: Reasonably well-formatted text with clear step progression

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/convert/text` | POST | Convert SOP text to BPMN |
| `/api/convert/file` | POST | Convert uploaded file to BPMN |
| `/api/convert/file/download` | POST | Convert and download BPMN file |

## Improvements with More Time

1. **Enhanced Parsing**: Support for more SOP formats (tables, nested lists)
2. **Lane Detection**: Identify roles/departments for BPMN swim lanes
3. **Validation**: BPMN schema validation before output
4. **Visual Preview**: Integrate bpmn.io for diagram preview
5. **Multi-branch Support**: Handle complex decision trees beyond yes/no
6. **Sub-process Detection**: Identify nested processes
7. **Error Recovery**: Better handling of malformed SOP documents

## Running the Application

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn server:app --reload

# Frontend
cd frontend
yarn install
yarn start
```

## Example

**Input SOP:**
```
1. Receive customer support email.
2. Check if the issue is billing-related.
3. If yes, assign to Billing Queue.
4. If no, assign to General Support Queue.
5. Send acknowledgment email to customer.
6. Close the triage step.
```

**Output:** BPMN 2.0 XML with:
- Start Event
- Task: "Receive customer support email"
- Exclusive Gateway: "the issue is billing-related?"
- Task: "assign to Billing Queue" (Yes branch)
- Task: "assign to General Support Queue" (No branch)
- Task: "Send acknowledgment email to customer"
- Task: "Close the triage step"
- End Event
