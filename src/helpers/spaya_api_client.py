import json
import sys
import time
import urllib.parse
from typing import Dict, List, Any
import requests
from datetime import datetime


class SpayaAPIClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.session = requests.Session()
        self.session.headers.update(
            {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        )

    def submit_batch(self, smiles_list: List[str]) -> int:
        """Submit a batch of SMILES for retrosynthesis."""
        url = f"{self.base_url}/retrosynthesis/batch"

        payload = {
            "smiles": smiles_list,
            "timeout": 2,  # minutes
        }

        # full_payload = {
        #     ###########
        #     # Run parameters
        #     ###########
        #    "smiles": smiles_list,
        #    "timeout": 10,  # minutes
        #     "earlyStoppingScore": 1,
        #     "maxDepth": 10,
        #     "nbMaxResults": 300,
        #     ###########
        #     # Advanced search parameters
        #     ###########
        #     "maxDeliveryDays": 0,
        #     "maxPricePerG": 0,
        #     "removeChirality": False,
        #     "filterRegioIssues": False,
        #     "catalog": [],
        #     "providers": [],
        #     "forbiddenStructures": [],
        #     "imposedStructures": [],
        #     "intermediateSmiles": [],
        #     "nameReactionsAtLeast": [],
        #     "nameReactionsExclude": [],
        #     "nameReactionsOnly": [],
        #     "nameReactionsCategoriesAtLeast": [],
        #     "nameReactionsCategoriesExclude": [],
        #     "nameReactionsCategoriesOnly": [],
        #     "nameReactionsSubCategoriesAtLeast": [],
        #     "nameReactionsSubCategoriesExclude": [],
        #     "nameReactionsSubCategoriesOnly": [],
        #     "forbiddenReacSmiles": [],
        #     "enableSingleStepRetry": True,
        #     "noCache": False,
        # }

        print(
            f"You are about to submit the following payload to the Spaya API at {self.base_url}:"
        )
        # Create a copy of payload without smiles for logging
        log_payload = payload.copy()
        log_payload["smiles"] = f"List of {len(smiles_list)} SMILES"
        print(json.dumps(log_payload, indent=2, ensure_ascii=False))
        print("Continue? (y/n)")
        if input() != "y":
            print("Operation cancelled by user.")
            sys.exit(1)

        print(f"Submitting batch with {len(smiles_list)} SMILES...")
        response = self.session.post(url, json=payload)

        if response.status_code != 200:
            print(f"Error submitting batch: {response.status_code}")
            print(f"Response: {response.text}")
            response.raise_for_status()

        result = response.json()
        job_id = result.get("jobId")

        if not job_id:
            raise ValueError(f"No jobId found in response: {result}")

        return job_id

    def get_batch_status(self, job_id: int) -> Dict[str, Any]:
        """Get the status of a batch job."""
        url = f"{self.base_url}/retrosynthesis/{job_id}/status"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_batch_scores(self, job_id: int) -> List[Dict[str, Any]]:
        """Get scores for all targets in a batch."""
        url = f"{self.base_url}/retrosynthesis/{job_id}/scores"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_target_routes(self, job_id: int, smiles: str, page: int) -> Dict[str, Any]:
        """Get routes for a specific target molecule."""
        # URL encode the SMILES string
        encoded_smiles = urllib.parse.quote(smiles, safe="")
        url = f"{self.base_url}/retrosynthesis/{job_id}/target/{encoded_smiles}/page/{page}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def wait_for_completion(
        self, job_id: int, check_interval: int = 30, start_time: float = 0
    ) -> Dict[str, Any]:
        """Wait for batch job to complete."""
        print(f"\n⏳ Waiting for batch job {job_id} to complete...")

        while True:
            try:
                status_data = self.get_batch_status(job_id)

                status = status_data["status"]
                progress = status_data.get("progress", 0)
                created_at_iso = status_data.get("createdAt")
                if created_at_iso:
                    # Handle 'Z' suffix in ISO format by replacing with '+00:00'
                    if created_at_iso.endswith("Z"):
                        created_at_iso = created_at_iso[:-1] + "+00:00"
                    created_at: float = datetime.fromisoformat(
                        created_at_iso
                    ).timestamp()
                else:
                    created_at = start_time

                elapsed_seconds = time.time() - created_at

                if elapsed_seconds > 3600:
                    elapsed_hours = elapsed_seconds / 3600
                    elapsed_formatted = f"{elapsed_hours:.2f} hours"
                elif elapsed_seconds > 60:
                    elapsed_minutes = elapsed_seconds / 60
                    elapsed_formatted = f"{elapsed_minutes:.2f} minutes"
                else:
                    elapsed_formatted = f"{elapsed_seconds:.2f} seconds"

                print(
                    f"Status: {status}, Progress: {progress:.1f}%, Elapsed: {elapsed_formatted} (started at {datetime.fromisoformat(created_at_iso).strftime('%Y-%m-%d %H:%M:%S')})",
                    end="\r",
                )

                if status == "DONE":
                    print(f"\nBatch job {job_id} completed successfully!")
                    return status_data
                elif status in ["ERROR", "KILLED", "QUOTA_EXCEEDED"]:
                    print(f"\nBatch job {job_id} failed with status: {status}")
                    return status_data

                time.sleep(check_interval)

            except KeyboardInterrupt:
                print(f"\nInterrupted. Job {job_id} may still be running.")
                return self.get_batch_status(job_id)
            except Exception as e:
                print(f"\nError checking status: {e}")
                time.sleep(check_interval)
