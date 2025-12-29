from fastapi import FastAPI, APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import Response
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import sys

ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))
load_dotenv(ROOT_DIR / '.env')

from services import ConversionService

app = FastAPI(title="SOP to BPMN Converter", version="1.0.0")
api_router = APIRouter(prefix="/api")
conversion_service = ConversionService()


class TextConversionRequest(BaseModel):
    text: str = Field(..., description="SOP text content")
    process_name: str = Field(default="SOP Process")


class ConversionResponse(BaseModel):
    success: bool
    bpmn_xml: Optional[str] = None
    error: Optional[str] = None
    stats: Optional[Dict[str, Any]] = None


@api_router.get("/")
async def root():
    return {"message": "SOP to BPMN Converter API", "version": "1.0.0"}


@api_router.post("/convert/text", response_model=ConversionResponse)
async def convert_text(request: TextConversionRequest):
    result = conversion_service.convert_text(text=request.text, process_name=request.process_name)
    return ConversionResponse(success=result.success, bpmn_xml=result.bpmn_xml, error=result.error, stats=result.stats)


@api_router.post("/convert/file", response_model=ConversionResponse)
async def convert_file(
    file: UploadFile = File(...),
    process_name: str = Form(default="SOP Process")
):
    allowed_extensions = ['.docx', '.txt', '.doc']
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_ext}")
    
    content = await file.read()
    result = conversion_service.convert_bytes(content=content, filename=file.filename, process_name=process_name)
    return ConversionResponse(success=result.success, bpmn_xml=result.bpmn_xml, error=result.error, stats=result.stats)


@api_router.post("/convert/file/download")
async def convert_file_download(
    file: UploadFile = File(...),
    process_name: str = Form(default="SOP Process")
):
    allowed_extensions = ['.docx', '.txt', '.doc']
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_ext}")
    
    content = await file.read()
    result = conversion_service.convert_bytes(content=content, filename=file.filename, process_name=process_name)
    
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)
    
    output_name = Path(file.filename).stem + '.bpmn'
    return Response(content=result.bpmn_xml, media_type='application/xml', headers={'Content-Disposition': f'attachment; filename="{output_name}"'})


app.include_router(api_router)
app.add_middleware(CORSMiddleware, allow_credentials=True, allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','), allow_methods=["*"], allow_headers=["*"])

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
