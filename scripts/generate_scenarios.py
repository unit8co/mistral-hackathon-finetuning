from scenario_generator import add_generated_scenarios
from ressources import SCRAPING_DATA_DIR, load_json

if __name__ == "__main__":

    law_cases = load_json(SCRAPING_DATA_DIR.joinpath("unified_law_cases_v2.json"))

    add_generated_scenarios(law_cases)
