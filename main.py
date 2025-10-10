#!/usr/bin/env python3
"""
Retrosynthesis Batch Processing Script for Spaya API v2

This script executes retrosynthesis for a list of SMILES from a file,
waits for batch completion, shows scores, and retrieves the first route
for each SMILES.

Usage: python retrosynthesis_batch.py <smiles_file> --token <oauth_token> [--base-url <url>]

File format: One SMILES string per line

Dependencies:
    pip install requests tabulate urllib3
"""

import argparse
import os
import sys
from src.helpers.submit_batch_from_file import submit_batch_from_file
from src.helpers.check_batch_status import check_batch_status


def parse_args():
    parser = argparse.ArgumentParser(
        description="Execute retrosynthesis batch processing using Spaya API v2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python retrosynthesis_batch.py molecules.txt --token your_oauth_token
  python retrosynthesis_batch.py molecules.txt --token your_token --base-url https://spaya.ai/api/v2
        """,
    )

    parser.add_argument(
        "--file",
        help="Path to file containing SMILES (one per line)",
        default=None,
        required=False,
    )
    parser.add_argument("--job", help="Job ID", default=None, required=False)
    parser.add_argument("--token", help="OAuth2 Bearer token for API authentication")
    parser.add_argument(
        "--base-url",
        default="https://spaya.ai/api/v2",
        help="Base URL for Spaya API (default: staging environment)",
    )
    parser.add_argument(
        "--check-interval",
        type=int,
        default=30,
        help="Status check interval in seconds (default: 30)",
    )

    args = parser.parse_args()
    if not args.token:
        args.token = os.getenv("SPAYA_API_TOKEN")

    return args


def main():
    args = parse_args()

    if args.file:
        job_id = submit_batch_from_file(args)
        args.job = job_id
        check_batch_status(args)
    elif args.job:
        check_batch_status(args)
    else:
        print("No file or job ID provided")
        sys.exit(1)


if __name__ == "__main__":
    main()
