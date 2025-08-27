import os
from typing import Dict, Any


def setup_environment_variables() -> Dict[str, str]:
    """
    Setup guide for environment variables needed for the comparison
    
    Returns:
        Dictionary with required environment variables and their descriptions
    """
    required_vars = {
        "AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT": "Your Azure Document Intelligence endpoint URL (e.g., https://your-resource.cognitiveservices.azure.com/)",
        "AZURE_DOCUMENT_INTELLIGENCE_KEY": "Your Azure Document Intelligence API key",
        "GOOGLE_CLOUD_PROJECT_ID": "Your Google Cloud Project ID",
        "GOOGLE_CLOUD_LOCATION": "Google Cloud location (default: 'us')",
        "GOOGLE_APPLICATION_CREDENTIALS": "Path to your Google Cloud service account JSON file",
        "GOOGLE_DOCUMENT_AI_PROCESSOR_ID": "Your Google Document AI processor ID"
    }
    
    print("=== Environment Setup Guide ===\n")
    print("Please set the following environment variables:\n")
    
    for var, description in required_vars.items():
        current_value = os.getenv(var)
        status = "✓ Set" if current_value else "✗ Not set"
        print(f"{var}: {description}")
        print(f"Status: {status}")
        if current_value and not var.endswith("_KEY"):  # Don't show keys for security
            print(f"Current value: {current_value}")
        print()
    
    return required_vars


def create_sample_env_file():
    """Create a sample .env file for easy setup"""
    env_content = """# Azure Document Intelligence Configuration
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_DOCUMENT_INTELLIGENCE_KEY=your_azure_api_key_here

# Google Cloud Document AI Configuration
GOOGLE_CLOUD_PROJECT_ID=your-google-cloud-project-id
GOOGLE_CLOUD_LOCATION=us
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json
GOOGLE_DOCUMENT_AI_PROCESSOR_ID=your_processor_id_here

# Optional: Set these if you want to use specific models
AZURE_MODEL_ID=prebuilt-layout
"""
    
    with open(".env.example", "w") as f:
        f.write(env_content)
    
    print("Created .env.example file. Copy it to .env and fill in your credentials.")


def check_dependencies():
    """Check if required Python packages are installed"""
    required_packages = [
        "azure-ai-formrecognizer",
        "google-cloud-documentai", 
        "pandas",
        "python-dotenv"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✓ {package} is installed")
        except ImportError:
            print(f"✗ {package} is NOT installed")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nInstall missing packages with:")
        print(f"pip install {' '.join(missing_packages)}")
    else:
        print("\n✓ All required packages are installed!")


def create_sample_documents_info():
    """Create information about sample documents for testing"""
    sample_docs_info = """
=== Sample Documents for Testing ===

To test the document intelligence services, you'll need sample documents with:

1. Tables:
   - PDF with structured tables
   - Excel files converted to PDF
   - Forms with table-like structures

2. Text Images:
   - Scanned documents
   - Screenshots with text
   - Handwritten notes (for OCR testing)

3. Mixed Content:
   - Invoice documents
   - Reports with tables and text
   - Forms with key-value pairs

Recommended test cases:
- Simple table with 3x3 grid
- Complex table with merged cells
- Document with both tables and paragraphs
- Low-quality scanned image
- High-resolution image with small text
- Multi-page PDF document

Place your test documents in a 'sample_documents' directory.
"""
    
    with open("SAMPLE_DOCUMENTS_GUIDE.md", "w") as f:
        f.write(sample_docs_info)
    
    print("Created SAMPLE_DOCUMENTS_GUIDE.md with testing recommendations")


if __name__ == "__main__":
    print("Setting up document intelligence comparison environment...\n")
    
    # Check environment variables
    setup_environment_variables()
    
    # Create sample env file
    create_sample_env_file()
    
    # Check dependencies
    print("\n=== Dependency Check ===")
    check_dependencies()
    
    # Create sample documents guide
    print("\n=== Sample Documents ===")
    create_sample_documents_info()
    
    print("\n=== Next Steps ===")
    print("1. Install required packages: pip install -r requirements.txt")
    print("2. Copy .env.example to .env and fill in your credentials")
    print("3. Set up your Google Cloud service account and download the JSON key")
    print("4. Create Azure Document Intelligence resource and get endpoint/key")
    print("5. Create Google Document AI processor and get processor ID")
    print("6. Place test documents in 'sample_documents' directory")
    print("7. Run: python performance_comparison.py")