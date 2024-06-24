from rag import CompletionModel
import os
import logging
from typing import Dict, Any
from ressources import write_json, SCRAPING_DATA_DIR

# 4000 chars
MAX_CONTEXT_LENGTH = 4000

logger = logging.getLogger(__name__)

turbo_model = CompletionModel(
    provider="openai",
    api_key=os.environ["AZURE_GPT35_API_KEY"],
    api_version=os.environ["AZURE_GPT35_API_VERSION"],
    endpoint=os.environ["AZURE_GPT35_API_ENDPOINT"],
    model_deployment=os.environ["AZURE_GPT35_MODEL_DEPLOYMENT"],
)

model = CompletionModel(
    provider="openai",
    api_key=os.environ["AZURE_GPT4O_API_KEY"],
    api_version=os.environ["AZURE_GPT4O_API_VERSION"],
    endpoint=os.environ["AZURE_GPT4O_API_ENDPOINT"],
    model_deployment=os.environ["AZURE_GPT4O_MODEL_DEPLOYMENT"],
)


def generate_scenario_from_law_case(law_case: str) -> str:

    INSTRUCTION = (
        "You are given a description of a situation that was brought at a court."
        "Your task is to inspire yourself from this situation to write in english a short (max 200 characters)"
        "explanation a normal person would describe to their lawyer. \n"
        "Example output: My neighbour is mawing the lawn every Sunday at 7am. I asked him to stop but "
        "he still does it, how can I make this situation stop ?"
        "Example output: A big construction company is planning to build a 8 story building in front of "
        "my house blocking my view of the lake, how can I prevent this ?"
    )

    answer = turbo_model.call(
        messages=[
            {"role": "system", "content": INSTRUCTION},
            {"role": "user", "content": law_case},
        ],
        temperature=0,
    )

    return answer


def add_generated_scenarios(law_cases: Dict[str, Any]) -> Dict[str, Any]:
    augmented_law_cases = []
    for i, entry in enumerate(law_cases):
        if entry["situation"]:
            scenario = None
            try:
                scenario = generate_scenario_from_law_case(
                    entry["situation"][:MAX_CONTEXT_LENGTH]
                )

            except Exception as e:
                logger.error(e)

            entry["generated_scenario"] = scenario

            augmented_law_cases.append(entry)
            write_json(
                augmented_law_cases,
                SCRAPING_DATA_DIR.joinpath(f"generated_scenarios/v_{i}.json"),
            )
    return augmented_law_cases
