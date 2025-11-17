import pandas as pd
import json
from datetime import date

EXCEL_FILE_PATH = 'data.xlsx'
OUTPUT_FILE_PATH = 'legacyCertificateData.ts'

COLUMN_MAPPING = {
    'Student Name': 'studentName',
    "Father's Name": 'fatherName',
    'Branch': 'branch',
    'Internship Topic': 'internshipTopic',
    'Certificate Number': 'certificateNumber'
}

def excel_to_json():
    try:
        df = pd.read_excel(EXCEL_FILE_PATH, dtype=str).fillna('')
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

        required = list(COLUMN_MAPPING.keys())
        missing = [c for c in required if c not in df.columns]
        if missing:
            print(f"Missing columns: {', '.join(missing)}")
            return

        df = df[required].rename(columns=COLUMN_MAPPING)
        df['issueDate'] = 'June 2025'

        data = df.to_dict(orient='records')
        output = f"""
// Auto-generated file
export interface LegacyCertificate {{
  studentName: string;
  fatherName: string;
  branch: string;
  internshipTopic: string;
  certificateNumber: string;
  issueDate: string;
}}

export const legacyCertificateData: LegacyCertificate[] = {json.dumps(data, indent=2)};
"""

        with open(OUTPUT_FILE_PATH, 'w', encoding='utf-8') as f:
            f.write(output)

        print(f"Converted {len(data)} records → {OUTPUT_FILE_PATH}")

    except FileNotFoundError:
        print(f"File not found: {EXCEL_FILE_PATH}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    excel_to_json()
