import os
import time
from typing import Dict, List, Any, Optional
from google.cloud import documentai
import json


class GoogleDocumentAI:
    def __init__(self, project_id: str, location: str = "us"):
        self.project_id = project_id
        self.location = location
        self.client = documentai.DocumentProcessorServiceClient()
    
    def analyze_document(self, document_path: str, processor_id: str) -> Dict[str, Any]:
        """
        Analyze document using Google Cloud Document AI
        
        Args:
            document_path: Path to the document file
            processor_id: Processor ID for the specific model
        
        Returns:
            Dictionary containing analysis results and performance metrics
        """
        start_time = time.time()
        
        # Read the document
        with open(document_path, "rb") as document:
            document_content = document.read()
        
        # Determine MIME type
        mime_type = self._get_mime_type(document_path)
        
        # Create the request
        name = self.client.processor_path(self.project_id, self.location, processor_id)
        request = documentai.ProcessRequest(
            name=name,
            raw_document=documentai.RawDocument(content=document_content, mime_type=mime_type)
        )
        
        # Process the document
        result = self.client.process_document(request=request)
        document_result = result.document
        
        processing_time = time.time() - start_time
        
        # Extract text content
        text_content = document_result.text
        
        # Extract tables
        tables = []
        for page in document_result.pages:
            if hasattr(page, 'tables'):
                for table in page.tables:
                    table_data = {
                        "row_count": len(set(cell.layout.text_anchor.text_segments[0].start_index // 100 for cell in table.body_rows[0].cells)) if table.body_rows else 0,
                        "column_count": len(table.header_rows[0].cells) if table.header_rows else len(table.body_rows[0].cells) if table.body_rows else 0,
                        "cells": []
                    }
                    
                    # Extract header cells
                    if table.header_rows:
                        for row_idx, row in enumerate(table.header_rows):
                            for col_idx, cell in enumerate(row.cells):
                                cell_text = self._extract_text_from_layout(cell.layout, text_content)
                                table_data["cells"].append({
                                    "content": cell_text,
                                    "row_index": row_idx,
                                    "column_index": col_idx,
                                    "is_header": True,
                                    "confidence": cell.layout.confidence if hasattr(cell.layout, 'confidence') else 0.0
                                })
                    
                    # Extract body cells
                    for row_idx, row in enumerate(table.body_rows):
                        for col_idx, cell in enumerate(row.cells):
                            cell_text = self._extract_text_from_layout(cell.layout, text_content)
                            table_data["cells"].append({
                                "content": cell_text,
                                "row_index": row_idx + len(table.header_rows),
                                "column_index": col_idx,
                                "is_header": False,
                                "confidence": cell.layout.confidence if hasattr(cell.layout, 'confidence') else 0.0
                            })
                    
                    tables.append(table_data)
        
        # Extract form fields (key-value pairs)
        form_fields = []
        for page in document_result.pages:
            if hasattr(page, 'form_fields'):
                for field in page.form_fields:
                    field_name = self._extract_text_from_layout(field.field_name, text_content) if field.field_name else ""
                    field_value = self._extract_text_from_layout(field.field_value, text_content) if field.field_value else ""
                    
                    form_fields.append({
                        "key": field_name,
                        "value": field_value,
                        "confidence": field.field_value.confidence if field.field_value and hasattr(field.field_value, 'confidence') else 0.0
                    })
        
        # Extract entities
        entities = []
        if document_result.entities:
            for entity in document_result.entities:
                entities.append({
                    "type": entity.type_,
                    "mention_text": entity.mention_text,
                    "confidence": entity.confidence,
                    "normalized_value": entity.normalized_value.text if entity.normalized_value else ""
                })
        
        return {
            "service": "Google Cloud Document AI",
            "processor_id": processor_id,
            "processing_time": processing_time,
            "text_content": text_content,
            "tables": tables,
            "form_fields": form_fields,
            "entities": entities,
            "page_count": len(document_result.pages),
            "confidence_scores": self._extract_confidence_scores(document_result)
        }
    
    def _get_mime_type(self, file_path: str) -> str:
        """Determine MIME type based on file extension"""
        extension = os.path.splitext(file_path)[1].lower()
        mime_types = {
            '.pdf': 'application/pdf',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.tiff': 'image/tiff',
            '.tif': 'image/tiff',
            '.bmp': 'image/bmp',
            '.webp': 'image/webp'
        }
        return mime_types.get(extension, 'application/pdf')
    
    def _extract_text_from_layout(self, layout, full_text: str) -> str:
        """Extract text from layout segments"""
        if not layout or not layout.text_anchor:
            return ""
        
        text = ""
        for segment in layout.text_anchor.text_segments:
            start_index = segment.start_index
            end_index = segment.end_index
            text += full_text[start_index:end_index]
        
        return text.strip()
    
    def _extract_confidence_scores(self, document_result) -> Dict[str, float]:
        """Extract confidence scores from the analysis result"""
        confidences = []
        
        # Collect confidence scores from various elements
        for page in document_result.pages:
            # Form fields confidence
            if hasattr(page, 'form_fields'):
                for field in page.form_fields:
                    if field.field_value and hasattr(field.field_value, 'confidence'):
                        confidences.append(field.field_value.confidence)
            
            # Table cells confidence
            if hasattr(page, 'tables'):
                for table in page.tables:
                    for row in table.body_rows:
                        for cell in row.cells:
                            if hasattr(cell.layout, 'confidence'):
                                confidences.append(cell.layout.confidence)
        
        # Entities confidence
        if document_result.entities:
            confidences.extend([entity.confidence for entity in document_result.entities])
        
        if confidences:
            return {
                "average": sum(confidences) / len(confidences),
                "min": min(confidences),
                "max": max(confidences)
            }
        
        return {"average": 0.0, "min": 0.0, "max": 0.0}
    
    def analyze_image_text(self, image_path: str, processor_id: str) -> Dict[str, Any]:
        """
        Extract text from images using Google Document AI OCR processor
        """
        return self.analyze_document(image_path, processor_id)
    
    def analyze_table_structure(self, document_path: str, processor_id: str) -> Dict[str, Any]:
        """
        Analyze table structure in documents
        """
        return self.analyze_document(document_path, processor_id)


def create_google_client() -> Optional[GoogleDocumentAI]:
    """
    Create Google Document AI client from environment variables
    """
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us")
    
    if not project_id:
        print("Please set GOOGLE_CLOUD_PROJECT_ID environment variable")
        return None
    
    # Set up authentication
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not credentials_path:
        print("Please set GOOGLE_APPLICATION_CREDENTIALS environment variable")
        return None
    
    return GoogleDocumentAI(project_id, location)


if __name__ == "__main__":
    # Example usage
    client = create_google_client()
    if client:
        # Test with a sample document
        sample_doc = "sample_document.pdf"
        processor_id = os.getenv("GOOGLE_DOCUMENT_AI_PROCESSOR_ID")
        
        if not processor_id:
            print("Please set GOOGLE_DOCUMENT_AI_PROCESSOR_ID environment variable")
        elif os.path.exists(sample_doc):
            result = client.analyze_document(sample_doc, processor_id)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"Sample document {sample_doc} not found")