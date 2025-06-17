import subprocess

def handle(target: str, params: dict) -> str:
    if not target:
        return "ERROR: Mount point target cannot be empty."

    try:
        # The 'findmnt -kn <path>' command returns info only if it's a mount point.
        # This is the same command used in your configure_filesystem_partitions.sh script.
        result = subprocess.run(
            ['findmnt', '-kn', target],
            capture_output=True,
            text=True
        )
        
        # If the command's output is not empty, a mount point was found.
        # if result.stdout.strip():
        #     return "is_separate_partition"
        # else:
        #     return "is_not_separate_partition"
        
        # Return all the output and Will you contain Algorithm
        # return result.stdout.strip()
        return {
            'strdout': result.stdout.strip(),
            'strderr': result.stderr.strip(),
            'exit_code': result.returncode 
        }
            
    except FileNotFoundError:
        return "ERROR: 'findmnt' command not found."
    except Exception as e:
        return f"ERROR: An unexpected exception occurred: {e}"

# debug = handle("/proc", "") 
# print(debug)  # This will print the debug output if the decorator is working correctly.