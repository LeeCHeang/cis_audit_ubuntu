import os
from typing import Dict
def handle(target: str, params: dict) -> Dict[str,any]:
    key_to_find = params.get('key')
    # pass_if_missing_val = params.get('pass_if_missing')
    if not os.path.exists(target):
        # If the file doesn't exist AND we have a 'pass_if_missing' value,
        # return that value. This will cause the check to PASS.
        # if pass_if_missing_val is not None:
        #     return pass_if_missing_val
        # Otherwise, report the error as before.
        return {
            "stdout": '',
            "stderr": f"ERROR: File not found: {target}",
            "error_code": 1
        }
    if not key_to_find:
        # return "ERROR: Missing 'key' in parameters"
        return {
            "stdout": '',
            "stderr": "ERROR: Missing 'key' in parameters",
            "error_code": 1
        }
    
    try:
        with open(target, 'r') as f:
            for line in f:
                # Skip comments and empty lines
                clean_line = line.strip()
                if not clean_line or clean_line.startswith('#'):
                    continue
                
                # Split the line and check for the key.
                # This handles 'key = value', 'key value', 'key: value' etc.
                parts = clean_line.split(None, 1) # Split only on the first whitespace
                if len(parts) == 2 and parts[0].lower() == key_to_find.lower():
                    # Return the raw value, stripping potential quotes
                    print(f"Found key '{key_to_find}': {parts[1]}")
                    return {
                        "stdout": parts[1].strip("'\""),
                        "stderr": '',
                        "exit_code": 0
                    }
                    # return parts[1].strip("'\"")
        
        # return f"ERROR: Key '{key_to_find}' not found in file."
        return {
            "stdout": '',
            "stderr": f"There no '{key_to_find}' found in file.",
            "exit_code": 1 
        }
        
    except Exception as e:
        return { 
            'stdout': "",
            'stderr': f"ERROR: Failed to read file '{target}'. Reason: {e}",
            "exit_code": 2
        }

# if __name__ == "__main__":
#     result = handle('/etc/some_config
#     .conf', {'key': 'some_setting'})
#     print(result)  # Outputs the value or an error message
# Note: This function assumes the config file is in a standard format
# where each line is either a comment, empty, or a key-value pair.
# It does not handle complex formats like JSON or YAML.
# This is a simple key-value parser for standard config files.
# debug = handle("/etc/passwd", {"key": "root"})
# print(debug)  # This will print the value of 'root' or an error message if the key is not found.
# This is a simple key-value parser for standard config files.