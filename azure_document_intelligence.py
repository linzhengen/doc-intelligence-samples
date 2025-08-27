import os
import time
from typing import Dict, List, Any, Optional
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import json


class AzureDocumentIntelligence:
    def __init__(self, endpoint: str, api_key: str):
        self.client = DocumentAnalysisClient(
            endpoint=endpoint, 
            credential=AzureKeyCredential(api_key)
        )
    
    def analyze_document(self, document_path: str, model_id: str = "prebuilt-layout") -> Dict[str, Any]:
        """
        Analyze document using Azure Document Intelligence
        
        Args:
            document_path: Path to the document file
            model_id: Model to use for analysis (prebuilt-layout, prebuilt-invoice, etc.)
        
        Returns:
            Dictionary containing analysis results and performance metrics
        """
        start_time = time.time()
        
        with open(document_path, "rb") as document:
            poller = self.client.begin_analyze_document(
                model_id=model_id, 
                document=document
            )
            result = poller.result()
        
        processing_time = time.time() - start_time
        
        # Extract text content
        text_content = result.content if result.content else ""
        
        # Extract tables
        tables = []
        if result.tables:
            for table in result.tables:
                table_data = {
                    "row_count": table.row_count,
                    "column_count": table.column_count,
                    "cells": []
                }
                for cell in table.cells:
                    table_data["cells"].append({
                        "content": cell.content,
                        "row_index": cell.row_index,
                        "column_index": cell.column_index,
                        "row_span": cell.row_span,
                        "column_span": cell.column_span
                    })
                tables.append(table_data)
        
        # Extract key-value pairs
        key_value_pairs = []
        if result.key_value_pairs:
            for kv_pair in result.key_value_pairs:
                key_value_pairs.append({
                    "key": kv_pair.key.content if kv_pair.key else "",
                    "value": kv_pair.value.content if kv_pair.value else "",
                    "confidence": kv_pair.confidence
                })
        
        # Extract paragraphs
        paragraphs = []
        if result.paragraphs:
            for paragraph in result.paragraphs:
                paragraphs.append({
                    "content": paragraph.content,
                    "role": paragraph.role
                })
        
        return {
            "service": "Azure Document Intelligence",
            "model_id": model_id,
            "processing_time": processing_time,
            "text_content": text_content,
            "tables": tables,
            "key_value_pairs": key_value_pairs,
            "paragraphs": paragraphs,
            "page_count": len(result.pages) if result.pages else 0,
            "confidence_scores": self._extract_confidence_scores(result)
        }
    
    def _extract_confidence_scores(self, result) -> Dict[str, float]:
        """Extract confidence scores from the analysis result"""
        confidences = []
        
        # Collect confidence scores from various elements
        if result.key_value_pairs:
            confidences.extend([kv.confidence for kv in result.key_value_pairs if kv.confidence])
        
        if result.tables:
            for table in result.tables:
                confidences.extend([cell.confidence for cell in table.cells if cell.confidence])
        
        if confidences:
            return {
                "average": sum(confidences) / len(confidences),
                "min": min(confidences),
                "max": max(confidences)
            }
        
        return {"average": 0.0, "min": 0.0, "max": 0.0}
    
    def analyze_image_text(self, image_path: str) -> Dict[str, Any]:
        """
        Extract text from images using Azure Document Intelligence
        """
        return self.analyze_document(image_path, "prebuilt-read")
    
    def analyze_table_structure(self, document_path: str) -> Dict[str, Any]:
        """
        Analyze table structure in documents
        """
        return self.analyze_document(document_path, "prebuilt-layout")


def create_azure_client() -> Optional[AzureDocumentIntelligence]:
    """
    Create Azure Document Intelligence client from environment variables
    """
    endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
    api_key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")
    
    if not endpoint or not api_key:
        print("Please set AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT and AZURE_DOCUMENT_INTELLIGENCE_KEY environment variables")
        return None
    
    return AzureDocumentIntelligence(endpoint, api_key)


if __name__ == "__main__":
    # Example usage
    client = create_azure_client()
    if client:
        # Test with a sample document
        sample_doc = "sample_document.pdf"
        if os.path.exists(sample_doc):
            result = client.analyze_document(sample_doc)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"Sample document {sample_doc} not found")