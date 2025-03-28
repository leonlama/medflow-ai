# backend/shared/form_cleaner.py

def clean_form_data(data: dict) -> dict:
    """
    Dummy cleaning function for now. Replace with real logic.
    """
    return {k: v for k, v in data.items() if v not in (None, "", [], {})}

