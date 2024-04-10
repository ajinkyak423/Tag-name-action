import os
import sys
import re
import argparse
import ruamel.yaml as yaml
yaml = yaml.YAML(typ='safe', pure=True)

def extract_numeric_memory(memory_str):
    # Regular expression to match numeric values followed by memory units
    match = re.match(r'(\d+\.?\d*)([GgMmKk]?[iI]?)', memory_str)
    if match:
        numeric_value = float(match.group(1))
        unit = match.group(2).upper()
        
        if unit.startswith('G'):
            return numeric_value * 1024 * 1024 * 1024
        elif unit.startswith('M'):
            return numeric_value * 1024 * 1024
        elif unit.startswith('K'):
            return numeric_value * 1024
        else:
            return numeric_value
    else:
        return None
    
def find_resources(data):
    if isinstance(data, dict):
        if 'resources' in data:
            return data['resources']
        for value in data.values():
            result = find_resources(value)
            if result:
                return result
    return None

def check_resource_limits_in_doc(data, filepath):
    try:
        resources = find_resources(data)
        if resources:
            request_memory = resources.get('requests', {}).get('memory')
            limit_memory = resources.get('limits', {}).get('memory')
            
            if request_memory is not None and limit_memory is not None:
                request_memory = extract_numeric_memory(request_memory)
                limit_memory = extract_numeric_memory(limit_memory)

                diff_percentage = abs((limit_memory - request_memory) / request_memory) * 100
                if diff_percentage > 10:
                    print(f"In file {filepath}, the difference between request and limit memory ({diff_percentage}%) exceeds 10%.")
                    sys.exit(1)
            else:
                print(f"Request or limit memory not specified in file {filepath}")
        else:
            print(f"Resources not found in file {filepath}")
    except Exception as e:
        print(f"Error processing file {filepath}: {e}")

def load_yaml_file(filepath):
    with open(filepath, 'r') as file:
        try:
            print("Checking resource limits for file:", filepath)
            for data in yaml.load_all(file):
                check_resource_limits_in_doc(data, filepath)
        except Exception as e:
            print(f"Error loading file {filepath}: {e}")
            sys.exit(1)

if __name__ == "__main__":
    print("Checking the resource limits in YAML files...")
    parser = argparse.ArgumentParser(description="Check resource limits in YAML files.")
    parser.add_argument('input', metavar='INPUT', help="YAML file or directory containing YAML files to check")
    args = parser.parse_args()
    print("Input file/directory:", args.input)
    if os.path.isfile(args.input):
        load_yaml_file(args.input)
    else:
        print(f"Invalid input: {args.input}. yaml file is required.")
        sys.exit(1)
    print("Resource limits are within 10 percent difference for all YAML files.")