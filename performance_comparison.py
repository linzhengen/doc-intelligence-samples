import os
import json
import time
from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime
from azure_document_intelligence import create_azure_client
from google_document_ai import create_google_client


class DocumentIntelligenceComparison:
    def __init__(self):
        self.azure_client = create_azure_client()
        self.google_client = create_google_client()
        self.results = []
    
    def compare_services(self, 
                        document_path: str, 
                        azure_model_id: str = "prebuilt-layout",
                        google_processor_id: str = None) -> Dict[str, Any]:
        """
        Compare Azure Document Intelligence and Google Document AI on the same document
        
        Args:
            document_path: Path to the document to analyze
            azure_model_id: Azure model ID to use
            google_processor_id: Google processor ID to use
        
        Returns:
            Dictionary containing comparison results
        """
        if not os.path.exists(document_path):
            raise FileNotFoundError(f"Document not found: {document_path}")
        
        results = {
            "document_path": document_path,
            "timestamp": datetime.now().isoformat(),
            "azure_result": None,
            "google_result": None,
            "comparison_metrics": {}
        }
        
        # Test Azure Document Intelligence
        if self.azure_client:
            try:
                print(f"Processing with Azure Document Intelligence...")
                azure_result = self.azure_client.analyze_document(document_path, azure_model_id)
                results["azure_result"] = azure_result
                print(f"Azure processing time: {azure_result['processing_time']:.2f}s")
            except Exception as e:
                print(f"Azure error: {str(e)}")
                results["azure_result"] = {"error": str(e)}
        else:
            print("Azure client not available")
        
        # Test Google Document AI
        if self.google_client and google_processor_id:
            try:
                print(f"Processing with Google Document AI...")
                google_result = self.google_client.analyze_document(document_path, google_processor_id)
                results["google_result"] = google_result
                print(f"Google processing time: {google_result['processing_time']:.2f}s")
            except Exception as e:
                print(f"Google error: {str(e)}")
                results["google_result"] = {"error": str(e)}
        else:
            print("Google client not available or processor ID not provided")
        
        # Calculate comparison metrics
        results["comparison_metrics"] = self._calculate_comparison_metrics(
            results["azure_result"], 
            results["google_result"]
        )
        
        self.results.append(results)
        return results
    
    def _calculate_comparison_metrics(self, azure_result: Dict, google_result: Dict) -> Dict[str, Any]:
        """Calculate comparison metrics between Azure and Google results"""
        metrics = {}
        
        if azure_result and not azure_result.get("error") and google_result and not google_result.get("error"):
            # Processing time comparison
            azure_time = azure_result.get("processing_time", 0)
            google_time = google_result.get("processing_time", 0)
            
            metrics["processing_time"] = {
                "azure": azure_time,
                "google": google_time,
                "faster_service": "Azure" if azure_time < google_time else "Google",
                "time_difference": abs(azure_time - google_time)
            }
            
            # Text length comparison
            azure_text_len = len(azure_result.get("text_content", ""))
            google_text_len = len(google_result.get("text_content", ""))
            
            metrics["text_extraction"] = {
                "azure_text_length": azure_text_len,
                "google_text_length": google_text_len,
                "length_difference": abs(azure_text_len - google_text_len)
            }
            
            # Table detection comparison
            azure_tables = len(azure_result.get("tables", []))
            google_tables = len(google_result.get("tables", []))
            
            metrics["table_detection"] = {
                "azure_tables_count": azure_tables,
                "google_tables_count": google_tables,
                "tables_difference": abs(azure_tables - google_tables)
            }
            
            # Confidence scores comparison
            azure_confidence = azure_result.get("confidence_scores", {})
            google_confidence = google_result.get("confidence_scores", {})
            
            metrics["confidence_scores"] = {
                "azure_avg_confidence": azure_confidence.get("average", 0),
                "google_avg_confidence": google_confidence.get("average", 0),
                "azure_min_confidence": azure_confidence.get("min", 0),
                "google_min_confidence": google_confidence.get("min", 0),
                "azure_max_confidence": azure_confidence.get("max", 0),
                "google_max_confidence": google_confidence.get("max", 0)
            }
            
            # Key-value pairs / form fields comparison
            azure_kv_count = len(azure_result.get("key_value_pairs", []))
            google_ff_count = len(google_result.get("form_fields", []))
            
            metrics["form_extraction"] = {
                "azure_key_value_pairs": azure_kv_count,
                "google_form_fields": google_ff_count,
                "extraction_difference": abs(azure_kv_count - google_ff_count)
            }
        
        return metrics
    
    def batch_comparison(self, 
                        documents_dir: str, 
                        azure_model_id: str = "prebuilt-layout",
                        google_processor_id: str = None) -> List[Dict[str, Any]]:
        """
        Compare services on multiple documents in a directory
        """
        if not os.path.exists(documents_dir):
            raise FileNotFoundError(f"Directory not found: {documents_dir}")
        
        results = []
        supported_extensions = ['.pdf', '.png', '.jpg', '.jpeg', '.gif', '.tiff', '.tif', '.bmp']
        
        for filename in os.listdir(documents_dir):
            if any(filename.lower().endswith(ext) for ext in supported_extensions):
                document_path = os.path.join(documents_dir, filename)
                print(f"\nProcessing: {filename}")
                
                try:
                    result = self.compare_services(document_path, azure_model_id, google_processor_id)
                    results.append(result)
                except Exception as e:
                    print(f"Error processing {filename}: {str(e)}")
        
        return results
    
    def generate_report(self, output_file: str = "comparison_report.json"):
        """Generate a comprehensive comparison report"""
        if not self.results:
            print("No results to report. Run comparisons first.")
            return
        
        report = {
            "summary": self._generate_summary(),
            "detailed_results": self.results,
            "generated_at": datetime.now().isoformat()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"Report saved to {output_file}")
        return report
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics from all results"""
        if not self.results:
            return {}
        
        successful_comparisons = [r for r in self.results 
                                if r.get("azure_result") and not r["azure_result"].get("error") 
                                and r.get("google_result") and not r["google_result"].get("error")]
        
        if not successful_comparisons:
            return {"message": "No successful comparisons found"}
        
        azure_times = [r["azure_result"]["processing_time"] for r in successful_comparisons]
        google_times = [r["google_result"]["processing_time"] for r in successful_comparisons]
        
        summary = {
            "total_documents": len(self.results),
            "successful_comparisons": len(successful_comparisons),
            "performance_summary": {
                "azure_avg_time": sum(azure_times) / len(azure_times) if azure_times else 0,
                "google_avg_time": sum(google_times) / len(google_times) if google_times else 0,
                "azure_fastest_count": sum(1 for r in successful_comparisons 
                                         if r["comparison_metrics"]["processing_time"]["faster_service"] == "Azure"),
                "google_fastest_count": sum(1 for r in successful_comparisons 
                                          if r["comparison_metrics"]["processing_time"]["faster_service"] == "Google")
            }
        }
        
        return summary
    
    def export_to_csv(self, output_file: str = "comparison_results.csv"):
        """Export comparison results to CSV for analysis"""
        if not self.results:
            print("No results to export")
            return
        
        rows = []
        for result in self.results:
            row = {
                "document_path": result["document_path"],
                "timestamp": result["timestamp"]
            }
            
            # Azure metrics
            if result.get("azure_result") and not result["azure_result"].get("error"):
                azure = result["azure_result"]
                row.update({
                    "azure_processing_time": azure["processing_time"],
                    "azure_text_length": len(azure.get("text_content", "")),
                    "azure_tables_count": len(azure.get("tables", [])),
                    "azure_avg_confidence": azure.get("confidence_scores", {}).get("average", 0),
                    "azure_page_count": azure.get("page_count", 0)
                })
            
            # Google metrics
            if result.get("google_result") and not result["google_result"].get("error"):
                google = result["google_result"]
                row.update({
                    "google_processing_time": google["processing_time"],
                    "google_text_length": len(google.get("text_content", "")),
                    "google_tables_count": len(google.get("tables", [])),
                    "google_avg_confidence": google.get("confidence_scores", {}).get("average", 0),
                    "google_page_count": google.get("page_count", 0)
                })
            
            # Comparison metrics
            if result.get("comparison_metrics"):
                metrics = result["comparison_metrics"]
                if "processing_time" in metrics:
                    row["faster_service"] = metrics["processing_time"]["faster_service"]
                    row["time_difference"] = metrics["processing_time"]["time_difference"]
            
            rows.append(row)
        
        df = pd.DataFrame(rows)
        df.to_csv(output_file, index=False)
        print(f"Results exported to {output_file}")


def main():
    """Example usage of the comparison tool"""
    # Initialize comparison tool
    comparator = DocumentIntelligenceComparison()
    
    # Example single document comparison
    document_path = "sample_document.pdf"
    google_processor_id = os.getenv("GOOGLE_DOCUMENT_AI_PROCESSOR_ID")
    
    if os.path.exists(document_path) and google_processor_id:
        print("Comparing services on single document...")
        result = comparator.compare_services(
            document_path=document_path,
            azure_model_id="prebuilt-layout",
            google_processor_id=google_processor_id
        )
        
        # Generate and save report
        comparator.generate_report("single_document_report.json")
        comparator.export_to_csv("single_document_results.csv")
    
    # Example batch comparison
    documents_dir = "sample_documents"
    if os.path.exists(documents_dir) and google_processor_id:
        print("\nRunning batch comparison...")
        batch_results = comparator.batch_comparison(
            documents_dir=documents_dir,
            azure_model_id="prebuilt-layout",
            google_processor_id=google_processor_id
        )
        
        # Generate comprehensive report
        comparator.generate_report("batch_comparison_report.json")
        comparator.export_to_csv("batch_comparison_results.csv")


if __name__ == "__main__":
    main()