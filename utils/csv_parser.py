import csv
import os
import ast
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
                reader = csv.reader(csvfile)
                header = [h.strip() for h in next(reader)] 

                for row_num, row in enumerate(reader, 2): # Start from row 2 for better error messages
                    row_dict = dict(zip(header, row))
                    
                    profile_str = row_dict.get('Profile', 'All')
                    profiles = [p.strip() for p in profile_str.split(',')]
                    
                    params_str = row_dict.get('Parameters', '')
                    params: Union[Dict, List] = {}

                    if params_str:
                        try:
                            evaluated_params = ast.literal_eval(params_str)
                            if isinstance(evaluated_params, (dict, list)):
                                params = evaluated_params
                            else:
                                params = {"error": f"Parameters on row {row_num} is not a valid dictionary or list."}
                        except (ValueError, SyntaxError) as e:
                            # params = {"error": f"Malformed parameters string on row {row_num}: {e}", "original_value": params_str}
                            params = {"error": f"Malformed parameters string on row {row_num}: {e}", "original_value": params_str}

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