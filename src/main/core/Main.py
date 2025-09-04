from typing import List, Dict, Set
import requests
from bs4 import BeautifulSoup
from bs4.element import PageElement
import os

from Paths import *
from Nation import Nation
from State import State
from County import County

def get_soup(url: str) -> BeautifulSoup:
    ''' Get BeautifulSoup for a url. '''
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

def absolute_url(url: str) -> str:
    ''' Get the absolute url given any url. If relative, makes absolute with ROOT_URL. Otherwise,
        returns unmodified url. '''
    if url.startswith('/'):
        return ROOT_URL + url
    else:
        return url

def identify_states(start_url: str) -> Set[str]:
    ''' Identify states and returns a list of links to those states' pages. '''
    links = filter_links(get_links(get_soup(start_url)), ["state/"])
    return links

def create_states(start_url: str, limit: int = -1) -> List[State]:
    ''' Identify and create all States (links having "state/") linked to by the start_url page.
        Only creates limit number of states (-1 to identify all). '''
    states: List[State] = []
    links = identify_states(start_url)
    for link in links:
        if limit >= 0 and len(states)+1 > limit:
            break
        state_name = link.split("/")[-2].replace("-"," ")
        soup = get_soup(link.replace("Overview","Race-and-Ethnicity"))
        population = get_population(soup)
        demographics = get_demographics(soup)
        states.append(State(state_name, population, demographics))
    states.sort(key=lambda item: item.name)
    return states

def identify_counties(start_url: str) -> Set[str]:
    ''' Identify counties and return a list of links to those counties' pages. '''
    links = filter_links(get_links(get_soup(start_url)), ["county/"])
    return links

def create_counties(state_url: str, state: State, limit: int = -1) -> List[County]:
    ''' Identify and create all Counties (links having "county/") linked to by the start_url page.
        Only identifies limit number of counties (-1 to identify all). '''
    counties: List[County] = []
    links = filter_links(get_links(get_soup(state_url)), ["county/"])
    for link in links:
        if limit >= 0 and len(counties)+1 > limit:
            break
        county_name = link.split("/")[-2].replace("-"," ")
        soup = get_soup(link.replace("Overview","Race-and-Ethnicity"))
        print(county_name + ", " + state.name)
        pre = None
        try:
            pre = preprocessed_demographics[f"{county_name}, {state.name}"]
        except KeyError as e:
            pass
        counties.append(County(county_name, get_population(soup), pre if pre else get_demographics(soup), state))
    counties.sort(key=lambda item: item.name)
    return counties

def find_link_tree(start_url: str) -> Set[str]:
    ''' Get set of filtered links connected to the start url or its descendent pages. '''
    link_queue = [start_url]
    i: int = 0
    link: str = ""
    sublinks: Set[str] = set()
    while i < len(link_queue):
        print(f"index: {i} of {len(link_queue)}")
        link = link_queue[i]
        print("link: " + link)
        sublinks = filter_links(get_links(get_soup(link)))
        for sublink in sublinks:
            link_queue.append(sublink)
        i += 1
    return set(link_queue)


def get_links(soup: BeautifulSoup) -> List[str]:
    ''' Get all links (<a href=""> tags) on the page. '''
    links: List[str] = [absolute_url(link.get('href')) for link in soup.find_all('a') if link.get('href')] # type: ignore
    return links

_matches = ["state/"]
def filter_links(links: List[str], matches: List[str] = _matches) -> Set[str]:
    ''' Filter links into set of links containing text in the matches list. '''
    filtered: List[str] = []
    for link in links:
        if link not in filtered:
            for match in matches:
                if match in link:
                    filtered.append(link)
                    break
    return set(filtered)

def formatted_number_to_int(number: str) -> int | None:
    ''' Turn a formatted number (I.E. 1.5M 10,394 54k) into an integer. '''
    try:
        return int(number.replace(",",""))
    except ValueError as e:
        pass
    try:
        value = int(number[:-2].replace(",",""))
        letter_part = number[-1]
        if letter_part == 'M':
            value *= 1000000
        elif letter_part == "k":
            value *= 1000
        return value
    except ValueError as e:
        print(str(e))
        return None


def percent_to_float(percent: str) -> float | None:
    ''' Turn a percent (I.E. 54.32% 0.0432%) into a float. '''
    try:
        return float(percent.replace("%","")) / 100
    except ValueError as e:
        print(str(e))
        return None

def get_population(soup: BeautifulSoup) -> int:
    ''' Get the population from the State info sidebar on the page. '''
    selector = "#contents-nav > div > table > tbody > tr:nth-child(1) > td"
    element = soup.select(selector)[0]
    try:
        population = int(element.get_text().replace(",",""))
        return population
    except ValueError as e:
        print(str(e))
        return 0

preprocessed_demographics = { # Invalid or unparsable pages will have data manually placed here
    # "Clay County, Alabama" : {'White': 0.80264036, 'Hispanic': 0.03070533, 'Black': 0.14781577, 'Asian': 0.0, 'Mixed': 0.00815842, 'Other': 0.01068012},
    # "Coosa County, Alabama" : {'White': 0.65022091, 'Hispanic': 0.01288660, 'Black': 0.32363770, 'Asian': 0.0, 'Mixed': 0.01251841, 'Other': 0.00073638},
    # "Fayette County, Alabama" : {'White': 0.0, 'Hispanic': 0.0, 'Black': 0.0, 'Asian': 0.0, 'Mixed': 0.0, 'Other': 0.0},
    # "Henry County, Alabama" : {},
    # "Lamar County, Alabama" : {},
    # "Lowndes County, Alabama" : {},
    # "Wilcox County, Alabama" : {}
}
def get_demographics(soup: BeautifulSoup) -> Dict[str, float]:
    ''' Get demographics from the race/ethnicity graphic on the page. '''

    selector = "#figure\\/race-and-ethnicity > div.figure-contents > svg > g"
    graphic = soup.select(selector)[0]
    inner_graphics = graphic.select("g")
    race_ethnicity_labels: List[str] = []
    for inner in inner_graphics:
        if "font-style=\"normal\"" in inner.prettify():
            race_ethnicity_labels.append(inner.get_text())
    race_ethnicity_values: List[float] = []
    for inner in inner_graphics:
        if "<g>\n <title>" in inner.prettify():
            value = inner.find_all("title")[0].get_text()
            if '%' in value:
                float_value = percent_to_float(value)
                if float_value:
                    race_ethnicity_values.append(float_value)
    demographics: Dict[str, float] = {}
    try:
        for index, race_ethnicity in enumerate(race_ethnicity_labels):
            demographics[race_ethnicity] = race_ethnicity_values[index]
    except IndexError as e:
        print(str(e))
        print(graphic.prettify())
        return {}
    return demographics
    
def read_data_into_files(start_url):
    ''' Read state data into files in resources\\data for quicker access later. '''

    # Read and write nation data
    nation_folder = "src\\main\\resources\\data\\nation"
    try:
        os.mkdir(nation_folder)
    except FileExistsError:
        pass
    except OSError as e:
        print(str(e))
    soup = get_soup("https://statisticalatlas.com/United-States/Race-and-Ethnicity")
    with open(nation_folder + "\\race_ethnicity.html", 'w') as out:
        out.write(soup.prettify())

    # Identify States and write files
    states_links = identify_states("https://statisticalatlas.com/United-States/Overview")
    for link in states_links:
        state_page_name = link.split("/")[-2]
        state_file_name = state_page_name.replace("-","_").lower()
        print(state_file_name + " -----------------------------------------")

        state_folder = "src\\main\\resources\\data\\" + state_file_name
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

        if not os.path.exists(state_folder + "\\race_ethnicity.html"):
            soup = get_soup(link.replace("Overview","Race-and-Ethnicity"))
            with open(state_folder + "\\race_ethnicity.html", 'w', encoding='utf-8') as out:
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

            if not os.path.exists(county_folder + "\\race_ethnicity.html"):
                soup = get_soup(link.replace("Overview","Race-and-Ethnicity"))
                with open(county_folder + "\\race_ethnicity.html",'w', encoding='utf-8') as out:
                    out.write(soup.prettify())


def main() -> None:

    read_data_into_files("")
    exit()

    STATES_READ_LIMIT = 1
    COUNTIES_READ_LIMIT = -1

    soup: BeautifulSoup = BeautifulSoup()

    # Get nation demographics
    soup = get_soup("https://statisticalatlas.com/United-States/Race-and-Ethnicity")
    nation = Nation("United States", get_population(soup), get_demographics(soup))
    print(str(nation))

    # Identify states and get demographics
    states = identify_states(NATION_URL, STATES_READ_LIMIT)
    for state in states:
        print(str(state))

    # Identify counties and get demographics
    counties: Dict[State, List[County]] = dict.fromkeys(states, [])
    for state in states:
        # print(f"Finding counties: {state.name}")
        counties[state] = identify_counties(state.get_link(), state, COUNTIES_READ_LIMIT)
        for county in counties[state]:
            print(str(county))
    for state in states:
        print(f"# Counties in {state.name}: {len(counties[state])}")
    print("Total counties: " + str(len([county for state in counties for county in counties[state]])))

    for state in states:
        counties_pop_sum = 0
        counties_demographics = {}
        for county in counties[state]:
            counties_pop_sum += county.population
        print("Population of " + state.name)
        print("Counties pops: " + str(counties_pop_sum))
        print("State pop:     " + str(state.population))














    exit()

    soup = get_soup("https://statisticalatlas.com/county/Alabama/Autauga-County/Race-and-Ethnicity")
    selector = "#figure\\/race-and-ethnicity > div.figure-contents > svg > g"
    graphic = soup.select(selector)[0]
    inner_graphics = graphic.select("g")
    with open("logs\\log.out",'w') as file:
        for inner_graphic in inner_graphics:
            file.write(inner_graphic.prettify() + "\n")

    race_ethnicity_labels: List[str] = []
    for inner in inner_graphics:
        if "font-style=\"normal\"" in inner.prettify():
            race_ethnicity_labels.append(inner.get_text())
    print(race_ethnicity_labels)

    race_ethnicity_values: List[float] = []
    for inner in inner_graphics:
        if "<g>\n <title>" in inner.prettify():
            value = inner.find_all("title")[0].get_text()
            if '%' in value:
                float_value = percent_to_float(value)
                if float_value:
                    race_ethnicity_values.append(float_value)
    print(race_ethnicity_values)




    exit()
    counties: Dict[State, List[County]] = dict.fromkeys(states, [])
    for state in states:
        print(f"Finding counties: {state.name}")
        counties[state] = identify_counties(state.get_link(), state)
    for state in counties:
        for county in counties[state]:
            print(county.get_name_with_state())
    print("Total counties: " + str(len([county for state in counties for county in counties[state]])))
    
    links: List[str] = []
    for state in counties:
        links.append(state.get_link())
        for county in counties[state]:
            links.append(county.get_link())
    for link in links:
        print(link)


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