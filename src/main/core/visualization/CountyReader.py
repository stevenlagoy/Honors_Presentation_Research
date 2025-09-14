from typing import List
import os

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

def main() -> None:
    files: List[str] = list_files_recursive(RESOURCES_DIR)
    with open("src\\main\\core\\visualization\\counties.json","w",encoding="utf-8") as out:
        out.write("{\n\t\"files\" : [\n")
        for i, file in enumerate(files):
            if "county" not in file:
                continue
            out.write(f"\t\t\"{file.replace("\\","/").replace("src/main","../..")}\"{"," if i < len(files) - 2 else ""}\n")
        out.write("\t]\n}")
    print("Main Done")

if __name__ == "__main__":
    main()