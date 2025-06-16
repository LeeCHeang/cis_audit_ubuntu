import csv
import os
import json
from audit_task import AuditTask
from typing import List, Union, Dict

class CISBenchmarkParser:
    def __init__(self, csv_file_path: str):
        self.csv_file_path = csv_file_path

    def parse_csv(self) -> List[AuditTask]:
        if not os.path.exists(self.csv_file_path):
            raise FileNotFoundError(f"CSV file not found: {self.csv_file_path}")
        
        tasks = []
        try:
            with open(self.csv_file_path, 'r', encoding='utf-8') as csvfile:
                # Use csv.reader and skip header to avoid case sensitivity issues
                reader = csv.reader(csvfile)
                header = [h.strip() for h in next(reader)] # Read header row

                for row in reader:
                    row_dict = dict(zip(header, row))
                    profile_str = row_dict.get('Profile', 'All')
                    profiles = [p.strip() for p in profile_str.split(',')]
                    params_str = row_dict.get('Parameters', '{}')
                    params: Union[Dict, List] = {}
                    try:
                        params = json.loads(params_str.replace("'", '"')) if params_str else {}
                    except json.JSONDecodeError:
                        params = {"error": "Malformed JSON in Parameters column"}

                    # The AuditTask object is created using only the fields that
                    # actually exist in the class definition.
                    task = AuditTask(
                        id=row_dict.get('ID', ''),
                        level=row_dict.get('Level','N/A'),
                        profile=profiles,
                        domain=row_dict.get('Domain','General'),
                        title=row_dict.get('Title', 'No Title'),
                        check_type=row_dict.get('Check_Type', ''),
                        target=row_dict.get('Target', ''),
                        parameters=params,
                        algorithm=row_dict.get('Algorithm', ''),
                        expected_value=row_dict.get('Expected_Value', '')
                    )
                    tasks.append(task)
        except KeyError as e:
            raise ValueError(f"Missing required column in CSV: {e}")
        except Exception as e:
            raise Exception(f"Error parsing CSV file: {e}")

        return tasks