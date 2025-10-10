from pathlib import Path
from typing import Dict, List, Any, Tuple
from tabulate import tabulate
from src.helpers.spaya_api_client import SpayaAPIClient


def load_smiles_from_file(file_path: str) -> List[str]:
    """Load SMILES from a text file (one per line)."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    smiles_list = []
    with path.open("r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if line and not line.startswith("#"):  # Skip empty lines and comments
                smiles_list.append(line)

    if not smiles_list:
        raise ValueError(f"No valid SMILES found in {file_path}")

    print(f"Loaded {len(smiles_list)} SMILES from {file_path}")
    return smiles_list


def display_scores_table(scores_data: List[Dict[str, Any]]) -> None:
    """Display scores in a formatted table."""

    table_data = []
    for entry in scores_data:
        smiles = entry.get("smiles", "N/A")
        score = entry.get("score", "N/A")
        nb_steps = entry.get("nbSteps", "N/A")
        status = entry.get("status", "N/A")
        nb_routes = len(entry.get("routes", []))

        # Format score and steps
        if isinstance(score, (int, float)) and score is not None:
            score_str = f"{score:.3f}"
        else:
            score_str = str(score) if score is not None else "N/A"

        if isinstance(nb_steps, (int, float)) and nb_steps is not None:
            steps_str = str(int(nb_steps))
        else:
            steps_str = str(nb_steps) if nb_steps is not None else "N/A"

        table_data.append(
            [
                smiles[:50] + "..." if len(smiles) > 50 else smiles,
                score_str,
                steps_str,
                status,
                nb_routes,
            ]
        )

    headers = ["SMILES", "Score", "Steps", "Status", "Routes"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))


def __get_routes(
    client: SpayaAPIClient, job_id: int, smiles: str, page: int
) -> Tuple[List[Dict[str, Any]], int]:
    """Get routes for a specific SMILES."""
    routes_data = client.get_target_routes(job_id, smiles, page)
    total_pages: int = routes_data.get("pageCount", 0) or 0
    routes: List[Dict[str, Any]] = routes_data.get("routes", []) or []
    return routes, total_pages


def populate_routes(
    client: SpayaAPIClient, job_id: int, scores_data: List[Dict[str, Any]]
) -> None:
    """Populate the routes for each SMILES."""
    print("⏳ Populating routes...")

    progress = 0.0
    progress_increment = 100 / len(scores_data)
    for entry in scores_data:
        smiles = entry.get("smiles")
        progress += progress_increment

        print(
            f"Progress: {progress:.1f}%, SMILES: {smiles}",
            end="\r",
        )

        if not smiles or entry.get("status") != "DONE":
            continue

        try:
            all_routes = []
            routes, total_pages = __get_routes(client, job_id, smiles, 1)
            if routes:
                all_routes.extend(routes)

            page = 2
            while page <= total_pages:
                print(
                    f"Getting routes for {smiles} page {page} of {total_pages}",
                    end="\r",
                )
                routes, total_pages = __get_routes(client, job_id, smiles, page)
                if routes:
                    all_routes.extend(routes)
                page += 1

            if not all_routes:
                entry["routes"] = []
                continue

            print(f"Found {len(all_routes)} routes for {smiles}", end="\r")
            entry["routes"] = all_routes

        except Exception as e:
            print(f"Error retrieving routes: {e}")
    print(f"✓ Routes populated for {len(scores_data)} SMILES\n")
