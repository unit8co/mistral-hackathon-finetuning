from scraping.scrapper import scrape_cases
from scraping.ressources import DATA_DIR

if __name__ == "__main__":
    scrape_cases(
        scd_filepath=DATA_DIR.joinpath("scd.csv"),
        save_folder=DATA_DIR.joinpath("cases"),
    )
