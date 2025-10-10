import argparse
import json
import sys
import time
import requests
from src.helpers.spaya_api_client import SpayaAPIClient
from src.helpers.utils import display_scores_table, populate_routes


def check_batch_status(args: argparse.Namespace):
    try:
        job_id = args.job

        # Initialize API client
        client = SpayaAPIClient(
            args.base_url,
            args.token,
        )

        # start timer
        start_time = time.time()

        print(f"✓ Checking batch status for Job ID: {job_id}")

        # Wait for completion
        final_status = client.wait_for_completion(
            job_id, args.check_interval, start_time
        )

        if final_status["status"] != "DONE":
            print(f"Batch job did not complete successfully: {final_status['status']}")
            sys.exit(1)

        # Get and display scores
        print("⏳ Getting scores...")
        scores_data = client.get_batch_scores(job_id)
        end_time = time.time()
        print(f"✓ Processing complete in {end_time - start_time:.2f} seconds")

        populate_routes(client, job_id, scores_data)
        display_scores_table(scores_data)

        # Save all routes to a file
        output_file = f"output/routes_job_{job_id}.json"
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(scores_data, f, indent=2, ensure_ascii=False)
            print(f"\n✓ Routes saved to: {output_file}")
        except Exception as e:
            print(f"\nWarning: Could not save routes to file: {e}")

        # stop timer
        print(f"✓ Job ID for future reference: {job_id}")

    except FileNotFoundError as e:
        print(f"File error: {e}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"API error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)
