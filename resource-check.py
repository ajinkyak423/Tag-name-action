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

def check_resource_limits_in_doc(data, filepath, threshold):
    try:
        resources = find_resources(data)
        if resources:
            request_memory = resources.get('requests', {}).get('memory')
            limit_memory = resources.get('limits', {}).get('memory')
            
            if request_memory and limit_memory:
                request_memory_bytes = extract_numeric_memory(request_memory)
                limit_memory_bytes = extract_numeric_memory(limit_memory)

                diff_percentage = abs((limit_memory_bytes - request_memory_bytes) / request_memory_bytes) * 100
                if diff_percentage > threshold:
                    namespace = data.get('metadata', {}).get('namespace')
                    name = data.get('metadata', {}).get('name')
                    print(f"::ERROR:: Object Name: {name}, Namespace: {namespace}, Difference Percentage: {diff_percentage}%, Threshold: {threshold}")
                    print(f"::ERROR:: Request Memory: {request_memory}, Limit Memory: {limit_memory}")
                    print("::warning:: Formula used for calculating difference percentage: |Limit Memory - Request Memory| / Request Memory * 100")
                    sys.exit(1)
            else:
                print(f"Request or limit memory not specified in file {filepath}")
    except Exception as e:
        print(f"::Error:: processing file {filepath}: {e}")

def load_yaml_file(filepath, threshold):
    with open(filepath, 'r') as file:
        try:
            print("Checking resource limits for file:", filepath)
            for data in yaml.load_all(file):
                check_resource_limits_in_doc(data, filepath, threshold)
        except Exception as e:
            print(f"::Error:: loading file {filepath}: {e}")
            sys.exit(1)

if __name__ == "__main__":
    print("Checking the resource limits in YAML files...")
    parser = argparse.ArgumentParser(description="Check resource limits in YAML files.")
    parser.add_argument('input', metavar='INPUT', help="YAML file to check")
    parser.add_argument('threshold', metavar='THRESHOLD', type=float, default=10, help="Threshold percentage for the difference between request and limit memory (default: 10)")
    args = parser.parse_args()
    print("Input file:", args.input)
    print("Threshold percentage:", args.threshold)
    if os.path.isfile(args.input):
        load_yaml_file(args.input, args.threshold)
    else:
        print(f"::ERROR:: Invalid input: {args.input}. YAML file is required.")
        sys.exit(1)
    print(f"Resource limits are within {args.threshold} percent difference for all YAML files.")
