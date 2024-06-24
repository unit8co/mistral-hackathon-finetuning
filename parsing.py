from bs4 import BeautifulSoup
from typing import Dict
from ressources import load_text, write_text
import glob
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def extract_case(html_page: str) -> str:

    soup = BeautifulSoup(html_page, "html.parser")
    content = soup.find("div", class_="content")

    return str(content)


def pre_process_cases(input_cases_folder: str, output_cases_folder: str) -> None:
    cases_paths = glob.glob(f"{input_cases_folder}/*")

    for fpath in cases_paths:
        parsed_case = extract_case(load_text(fpath))

        filename = fpath.split("/")[-1]
        write_text(f"{output_cases_folder}/{filename}", parsed_case)


def unify_law_case_dataset(
    cases_folder: str, metadata_df: pd.DataFrame
) -> Dict[str, str]:

    cases_paths = glob.glob(f"{cases_folder}/*")
    cases = []
    for fpath in cases_paths:
        case = load_text(fpath)
        id = fpath.split("/")[-1].replace(".html", "")
        cases.append({"id": id, "html_content": case})

    cases_df = pd.DataFrame(cases)

    unified_df = pd.merge(metadata_df, cases_df, on="id", how="inner")

    return unified_df


def add_extracted_situation(law_cases: Dict[str, str]) -> Dict[str, str]:

    augmented_law_cases = []
    for e in law_cases:
        situation = extract_situation(
            html_text=e["html_content"], language=e["language"]
        )

        e["situation"] = situation

        augmented_law_cases.append(e)

    return augmented_law_cases


def extract_situation(html_text: str, language: str) -> str | None:
    """Extract the situation section from the html"""

    extracted_situations = None

    FACTS_BOUNDING_DIVS = {
        "fr": ["<b>Faits :</b>", "<b>Considérant en droit :</b>"],
        "de": ["<b>Sachverhalt:</b>", "<b>Erwägungen:</b>"],
        "it": ["<b>Fatti:<b>", "<b>Diritto:<b>"],
    }

    facts_bounding_div = FACTS_BOUNDING_DIVS[language]

    if facts_bounding_div[0] in html_text:
        facts_html = html_text.split(facts_bounding_div[0])[1].split(
            facts_bounding_div[1]
        )[0]
        soup = BeautifulSoup(facts_html, "html.parser")
        extracted_situations = soup.text

    else:
        logger.warning("Could not extracts facts from text")

    return extracted_situations
