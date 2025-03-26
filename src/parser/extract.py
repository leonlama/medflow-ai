import os, json
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv()

client = DocumentAnalysisClient(
    os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT"),
    AzureKeyCredential(os.getenv("AZURE_FORM_RECOGNIZER_KEY"))
)

def extract_tables(input_path: str, output_path: str):
    with open(input_path, "rb") as f:
        poller = client.begin_analyze_document("prebuilt-document", document=f)
    tables = [table.to_dict() for table in poller.result().tables]
    with open(output_path, "w") as out:
        json.dump(tables, out, indent=2)

if __name__ == "__main__":
    extract_tables("sample_data/sample_lab_report.pdf", "parsed_data/report.json")
