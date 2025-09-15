from typing import List
import os
import json
import time

from Paths import *
from page_reader import get_soup, identify_states, identify_counties
from MapEntityFactory import create_state_from_files, create_county_from_files, create_nation_from_files

def webpages_to_files():
    ''' Read state data into files in resources\\data for quicker access later. '''

    pages = ["Race-and-Ethnicity", "Age-and-Sex", "Household-Types", "Marital-Status", "Ancestry", "Household-Income", "Employment-Status", "Industries", "Educational-Attainment"]

    # Read and write nation data
    for page in pages:
        soup = get_soup("https://statisticalatlas.com/United-States/" + page)
        with open(DATA_DIR + "\\" + page + ".html", 'w', encoding='utf-8') as out:
            out.write(soup.prettify())

    # Identify States and write files
    states_links = identify_states("https://statisticalatlas.com/United-States/Overview")
    for link in states_links:
        state_page_name = link.split("/")[-2]
        state_file_name = state_page_name.replace("-","_").lower()
        print(state_file_name + " -----------------------------------------")

        state_folder = DATA_DIR + "\\" + state_file_name
        try:
            os.mkdir(state_folder)
        except FileExistsError:
            pass
        except OSError as e:
            print(str(e))
        try:
            os.mkdir(state_folder + "\\counties\\")
        except FileExistsError:
            pass
        except OSError as e:
            print(str(e))

        for page in pages:
            if not os.path.exists(state_folder + "\\" + page + ".html"):
                soup = get_soup(link.replace("Overview", page))
                with open(state_folder + "\\" + page + ".html", 'w', encoding='utf-8') as out:
                    out.write(soup.prettify())

        # state_tasks = []
        # with ThreadPoolExecutor(max_workers=1) as executor:
        #     for page in pages:
        #         filepath = state_folder + "\\" + page + ".html"
        #         if not os.path.exists(filepath):
        #             url = link.replace("Overview", page)
        #             state_tasks.append(executor.submit(fetch_and_save, url, filepath))
        #     for future in as_completed(state_tasks):
        #         future.result()

        counties_links = identify_counties(link)
        for c_link in counties_links:
            county_page_name = c_link.split("/")[-2]
            county_file_name = county_page_name.replace("-","_").lower()
            print(county_file_name)

            county_folder = state_folder + "\\counties\\" + county_file_name
            try:
                os.mkdir(county_folder)
            except FileExistsError:
                pass
            except OSError as e:
                print(str(e))

            # county_tasks = []
            # for page in pages:
            #     filepath = county_folder + "\\" + page + ".html"
            #     if not os.path.exists(filepath):
            #         url = c_link.replace("Overview", page)
            #         county_tasks.append(executor.submit(fetch_and_save, url, filepath))
            # for future in as_completed(county_tasks):
            #     future.result()

            for page in pages:
                if not os.path.exists(county_folder + "\\" + page + ".html"):
                    c_soup = get_soup(c_link.replace("Overview", page))
                    with open(county_folder + "\\" + page + ".html", 'w', encoding='utf-8') as out:
                        out.write(c_soup.prettify())

def combine_jsons():

    output: List[str] = []
    states: List[str] = []

    with open(DATA_DIR + "\\data.json") as nation_file:
        for line in nation_file.readlines():
            output.append(line)
    for state_folder in os.listdir(DATA_DIR):
        if "." in state_folder:
            continue # only read folders
        with open(DATA_DIR + state_folder + "\\data.json") as state_file:
            for line in state_file.readlines():
                states.append(line)
        states[-1] += ",\n"
    output[-2] = output[-2].replace("\n","") + ",\n"
    output.insert(-1, "\t\"states\" : [\n")
    for line in states:
        output.insert(-1, "\t\t" + line)
    output.insert(-1, "\t]\n")
    output[-3] = output[-3].replace(",","") # remove trailing comma from states list
    with open(DATA_DIR + "combined_data.json", 'w') as file:
        for line in output:
            file.write(line)

def list_states() -> List[str]:
    return [state for state in os.listdir(DATA_DIR) if "." not in state]

def convert_html_json_files():
    if not os.path.exists(f"{RESOURCES_DIR}\\nation.json"):
        print("NATION ===========================")
        nation = create_nation_from_files()
        with open(f"{RESOURCES_DIR}\\nation.json",'w',encoding='utf-8') as out:
            nation_json = nation.to_json()
            out.write(json.dumps(nation_json, indent=4, separators=(", "," : ")))

    for state_name in os.listdir(f"{DATA_DIR}"):
        if '.' not in state_name:
            print(state_name + " ------------------------------")
            state = create_state_from_files(state_name)
            if not os.path.exists(f"{RESOURCES_DIR}\\{state_name}\\{state_name}.json"):
                try:
                    os.mkdir(f"{RESOURCES_DIR}\\{state_name}")
                except OSError:
                    pass
                with open(f"{RESOURCES_DIR}\\{state_name}\\{state_name}.json",'w',encoding='utf-8') as out:
                    state_json = state.to_json()
                    out.write(json.dumps(state_json, indent=4, separators=(", "," : ")))
            for county_name in os.listdir(f"{DATA_DIR}\\{state_name}\\counties"):
                if not "." in county_name and not os.path.exists(f"{RESOURCES_DIR}\\{state_name}\\counties\\{county_name}.json"):
                    print(county_name)
                    county = create_county_from_files(state_name, county_name, state)
                    try:
                        os.mkdir(f"{RESOURCES_DIR}\\{state_name}\\counties")
                    except OSError:
                        pass
                    with open(f"{RESOURCES_DIR}\\{state_name}\\counties\\{county_name}.json",'w',encoding='utf-8') as out:
                        county_json = county.to_json()
                        out.write(json.dumps(county_json, indent=4, separators=(", "," : ")))

def count_counties():
    for state_name in [_ for _ in os.listdir(f"{RESOURCES_DIR}") if '.' not in _]:
        counties_count = len([_ for _ in os.listdir(f"{RESOURCES_DIR}\\{state_name}\\counties")])
        print(f"{state_name} has {counties_count} counties")

unremovable_files: List[str] = []
def verify_data():
    global unremovable_files
    ''' Deletes all data files which contain a rate limit message. '''
    for file in list_files_recursive(DATA_DIR):
        print("Verifying: " + file)
        remove_file = False
        with open(file) as data:
            if "Too many requests" in data.readline():
                print("BAD FILE: " + file)
                remove_file = True
        if remove_file:
            for _ in range(10):
                try:
                    os.chmod(file, 0o777)
                    os.remove(file)
                    print("REMOVED: " + file)
                    break
                except PermissionError:
                    time.sleep(0.1)
            else:
                print("UNABLE TO REMOVE: " + file)
                unremovable_files.append(file)
    print("Files which could not be removed:")
    for file in unremovable_files:
        print(file)

def validate_json():
    ''' Check that all json data files contian the necessary objects. '''
    bad_files: List[str] = []
    required_lines = ["name", "population", "demographics", "race_and_ethnicity", "age_and_sex", "household_types", "marital_status", "employment_status", "industries", "educational_attainment"]
    for file in list_files_recursive(RESOURCES_DIR):
        has_required: List[bool] = [False for _ in required_lines]
        content: List[str] = []
        with open(file, 'r', encoding='utf-8') as data:
            content = data.readlines()
        for i, required_line in enumerate(required_lines):
            for line in content[i:]:
                if required_line in line:
                    has_required[i] = True
                    break
        if False in has_required:
            bad_files.append(file)
            print(f"{file} is BAD ------------------------------")
        else:
            print(f"{file} is good")
    print("Bad files:")
    for file in bad_files:
        print(file)

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

def add_states_to_jsons():
    for state_dir in os.listdir(RESOURCES_DIR):
        if '.' in state_dir:
            continue
        state_name = state_dir.replace("_"," ").title()
        for county_file in os.listdir(f"{RESOURCES_DIR}\\{state_dir}\\counties"):
            content: List[str] = []
            with open(f"{RESOURCES_DIR}\\{state_dir}\\counties\\{county_file}",'r') as data:
                content = data.readlines()
            if "\"state\"" in "\n".join(content):
                continue
            for i, line in enumerate(content):
                if "\"name\"" in line:
                    content.insert(i+1, f"\t\"state\" : \"{state_name}\", \n")
                    break
            with open(f"{RESOURCES_DIR}\\{state_dir}\\counties\\{county_file}","w") as data:
                for line in content:
                    data.write(line)

def main() -> None:

    # Gather all webpages
    webpages_to_files()

    # Verify downloaded webpage files, and delete any invalid
    verify_data()

    # Convert downloaded pages into json files
    convert_html_json_files()

    # Validate the json files
    validate_json()

    # Count the counties in each state
    count_counties()

    # Add state names to the json files
    add_states_to_jsons()

if __name__ == "__main__":
    main()