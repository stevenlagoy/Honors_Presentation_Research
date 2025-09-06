from typing import List, Dict, Set, Tuple, Any
import requests
from bs4 import BeautifulSoup
from bs4.element import PageElement, Tag
import os
import json

from Paths import *
from Nation import Nation
from State import State
from County import County
from page_reader import get_soup, identify_states, identify_counties
from MapEntityFactory import create_all_counties_from_files, create_all_counties_in_state_from_files, create_state_from_files, create_county_from_files, create_nation_from_files


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

            for page in pages:
                if not os.path.exists(county_folder + "\\" + page + ".html"):
                    c_soup = get_soup(link.replace("Overview", page))
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

def main() -> None:

    # webpages_to_files()

    # convert_html_json_files()
    

    if not os.path.exists(f"{RESOURCES_DIR}\\nation.json"):
        print("NATION ===========================")
        nation = create_nation_from_files()
        with open(f"{RESOURCES_DIR}\\nation.json",'w',encoding='utf-8') as out:
            nation_json = nation.to_json()
            out.write(json.dumps(nation_json, indent=4, separators=(", "," : ")))

    for state_name in os.listdir(f"{DATA_DIR}"):
        if not "." in state_name and not os.path.exists(f"{RESOURCES_DIR}\\{state_name}\\{state_name}.json"):
            print(state_name + " ------------------------------")
            state = create_state_from_files(state_name)
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
                
            # counties: List[County] = create_all_counties_in_state_from_files(state_name)
            # print("made counties")
            # state: State = counties[0].state
            # with open(f"{DATA_DIR}\\{state_name}\\data.json", 'w', encoding='utf-8') as file:
            #     counties_jsons = [county.to_json() for county in counties]
            #     state_json = state.to_json()
            #     state_json['counties'] = counties_jsons
            #     file.write(json.dumps(state_json, indent=4, separators=(", "," : ")))

    # combine_jsons()
        

    # Identify counties and get demographics
    # counties: Dict[State, List[County]] = dict.fromkeys(states, [])
    # for state in states:
    #     # print(f"Finding counties: {state.name}")
    #     counties[state] = identify_counties(state.get_link(), state, COUNTIES_READ_LIMIT)
    #     for county in counties[state]:
    #         print(str(county))
    # for state in states:
    #     print(f"# Counties in {state.name}: {len(counties[state])}")
    # print("Total counties: " + str(len([county for state in counties for county in counties[state]])))

    # for state in states:
    #     counties_pop_sum = 0
    #     counties_demographics = {}
    #     for county in counties[state]:
    #         counties_pop_sum += county.population
    #     print("Population of " + state.name)
    #     print("Counties pops: " + str(counties_pop_sum))
    #     print("State pop:     " + str(state.population))














    # exit()

    # soup = get_soup("https://statisticalatlas.com/county/Alabama/Autauga-County/Race-and-Ethnicity")
    # selector = "#figure\\/race-and-ethnicity > div.figure-contents > svg > g"
    # graphic = soup.select(selector)[0]
    # inner_graphics = graphic.select("g")
    # with open("logs\\log.out",'w') as file:
    #     for inner_graphic in inner_graphics:
    #         file.write(inner_graphic.prettify() + "\n")

    # race_ethnicity_labels: List[str] = []
    # for inner in inner_graphics:
    #     if "font-style=\"normal\"" in inner.prettify():
    #         race_ethnicity_labels.append(inner.get_text())
    # print(race_ethnicity_labels)

    # race_ethnicity_values: List[float] = []
    # for inner in inner_graphics:
    #     if "<g>\n <title>" in inner.prettify():
    #         value = inner.find_all("title")[0].get_text()
    #         if '%' in value:
    #             float_value = percent_to_float(value)
    #             if float_value:
    #                 race_ethnicity_values.append(float_value)
    # print(race_ethnicity_values)




    # exit()
    # counties: Dict[State, List[County]] = dict.fromkeys(states, [])
    # for state in states:
    #     print(f"Finding counties: {state.name}")
    #     counties[state] = identify_counties(state.get_link(), state)
    # for state in counties:
    #     for county in counties[state]:
    #         print(county.get_name_with_state())
    # print("Total counties: " + str(len([county for state in counties for county in counties[state]])))
    
    # links: List[str] = []
    # for state in counties:
    #     links.append(state.get_link())
    #     for county in counties[state]:
    #         links.append(county.get_link())
    # for link in links:
    #     print(link)


    # input()
    # link_tree = find_link_tree(ROOT_URL + "/United-States/Overview")
    # for link in link_tree:
    #     print(link)
    # input()
    # soup = get_soup(ROOT_URL + "/United-States/Overview")
    # #print(soup.prettify())
    # # Get all the urls linked to by this page
    # links = get_links(soup)
    # for link in links:
    #     if 'county/' in link: # type: ignore
    #         print(absolute_url(link))
    #         print(link.split("/")[-2].replace("-"," ")) # type: ignore

    # for state in STATES:
    #     print(state.name)

if __name__ == "__main__":
    main()