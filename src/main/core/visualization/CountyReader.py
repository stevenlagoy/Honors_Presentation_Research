from typing import List
import os
import json

RESOURCES_DIR = "src\\main\\resources"

def list_files_recursive(root_dir: str, files = None) -> List[str]:
    if files is None:
        files = []
    for path in os.listdir(root_dir):
        if '.' in path: # File
            files.append(root_dir + "\\" + path)
        else:
            for file in list_files_recursive(root_dir + "\\" + path):
                files.append(file)
    return files

def write_file_paths():
    files: List[str] = list_files_recursive(RESOURCES_DIR)
    with open("src\\main\\core\\visualization\\counties.json","w",encoding="utf-8") as out:
        out.write("{\n\t\"files\" : [\n")
        for i, file in enumerate(files):
            if "county" not in file:
                continue
            out.write(f"\t\t\"{file.replace("\\","/").replace("src/main","../..")}\"{"," if i < len(files) - 2 else ""}\n")
        out.write("\t]\n}")

def combine_data() -> List[str]:
    combined: List[str] = []
    files: List[str] = list_files_recursive(RESOURCES_DIR)

    for file in files:
        if file.split("\\")[-1].replace(".json", "").isnumeric():
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                fips = data.get("FIPS")
                if fips:
                    combined.append(f'"{fips}" : ' + json.dumps(data, indent=4) + ",\n")

    if combined:
        combined[-1] = combined[-1].rstrip(",\n")  # remove trailing comma from last item

    return combined

def main() -> None:
    with open("src\\main\\core\\visualization\\counties.json",'w',encoding='utf-8') as out:
        out.write("{\n")
        for line in combine_data():
            out.write(line)
        out.write("}")
    print("Main Done")

if __name__ == "__main__":
    main()