import os, sys, logging
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import azure.functions as func
from src.cleaner.cleaner import clean_data

app = func.FunctionApp()

@app.function_name(name="CleanData")
@app.route(route="CleanData", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def clean_data_func(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("CleanData HTTP trigger received")
    try:
        body = req.get_json()
        df = clean_data(body.get("input_path"))
        return func.HttpResponse(df.to_json(orient="records"), mimetype="application/json")
    except Exception as e:
        logging.error(f"Cleaning failed: {e}")
        return func.HttpResponse(str(e), status_code=500)
