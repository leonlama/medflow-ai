from faker import Faker
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

fake = Faker()

def make_csv(path="sample_data/patient_records.csv", rows=10):
    df = pd.DataFrame([{
        "patient_id": fake.uuid4(),
        "name": fake.name(),
        "dob": fake.date_of_birth(minimum_age=18, maximum_age=90),
        "test_date": fake.date_this_year(),
        "test_type": fake.random_element(elements=("CBC","Lipid Panel","CMP")),
        "result": round(fake.pyfloat(left_digits=2, right_digits=2, positive=True),2),
        "units": fake.random_element(elements=("mg/dL","g/L","mmol/L")),
        "reference_range": fake.random_element(elements=("10-20","50-100","3.5-5.5"))
    } for _ in range(rows)])
    df.to_csv(path, index=False)
    return df

def make_pdf(csv_path="sample_data/patient_records.csv", pdf_path="sample_data/sample_lab_report.pdf"):
    df = pd.read_csv(csv_path)
    data = [df.columns.tolist()] + df.values.tolist()
    doc = SimpleDocTemplate(pdf_path)
    table = Table(data)
    style = TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey)
    ])
    table.setStyle(style)
    doc.build([table])

if __name__ == "__main__":
    make_csv()
    make_pdf()
    print("Generated sample CSV & PDF in sample_data/")
