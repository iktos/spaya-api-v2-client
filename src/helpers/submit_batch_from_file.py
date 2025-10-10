import argparse
import sys
import requests
from src.helpers.spaya_api_client import SpayaAPIClient
from src.helpers.utils import load_smiles_from_file


def submit_batch_from_file(args: argparse.Namespace):
    try:
        # Load SMILES from file
        smiles_list = load_smiles_from_file(args.file)

        if not smiles_list:
            print("No SMILES found in the file")
            sys.exit(1)

        # Initialize API client
        client = SpayaAPIClient(
            args.base_url,
            args.token,
        )

        # Submit batch
        job_id = client.submit_batch(smiles_list)
        print(f"✓ Batch {job_id} submitted successfully!")

        return job_id

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
