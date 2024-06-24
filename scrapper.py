import requests
import pandas as pd
import logging
import glob

logger = logging.getLogger(__name__)


def scrape_cases(
    scd_filepath: str = "data/scd.csv", save_folder: str = "data/usecases"
):

    df = pd.read_csv(scd_filepath)

    saved_pages = glob.glob(f"{save_folder}/*")
    saved_pages = [s.split("/")[-1].replace(".html", "") for s in saved_pages]
    df_remaining = df[~df["id"].isin(saved_pages)]

    scrape_html(df=df_remaining, save_folder=save_folder)


def scrape_html(df: pd.DataFrame, save_folder: str) -> None:
    """
    Assumes df has row id and url
    """
    for _, row in df.iterrows():
        id = row["id"]
        url = row["url"]
        resp = requests.get(url=url)
        if resp.status_code != 200:
            logger.warning(
                f"Error failed to retrieve page, error code: {resp.status_code}"
            )
            with open(f"{save_folder}/failed_{id}.txt", "w") as f:
                f.write("FAILED")
        else:
            html_page = resp.text
            logger.info(f"Scraped page index {id}")
            with open(f"{save_folder}/{id}.html", "w") as f:
                f.write(html_page)
