#!/usr/bin/env python3

import argparse
import subprocess
import os
import hashlib
import sys
from datetime import datetime

def get_unique_cache_file():
    # Create a unique filename based on username and script path
    # This ensures different users and different script locations get different cache files
    username = os.getenv('USER', 'unknown')
    script_path = os.path.abspath(__file__)
    unique_string = f"{username}-{script_path}"
    filename_hash = hashlib.md5(unique_string.encode()).hexdigest()[:8]
    return f"/tmp/nix-packages-cache-{filename_hash}"

def update_cache(cache_file):
    print("Updating package cache...")
    try:
        result = subprocess.run(
            ['nix-env', '-qaP', '*', '--description'],
            capture_output=True,
            text=True,
            check=True
        )
        with open(cache_file, 'w') as f:
            f.write(result.stdout)
        print("Cache updated successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running nix-env: {e}", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"Error writing to cache file: {e}", file=sys.stderr)
        sys.exit(1)

def search_packages(cache_file, search_term):
    try:
        with open(cache_file, 'r') as f:
            for line in f:
                if search_term.lower() in line.lower():
                    print(line.strip())
    except IOError as e:
        print(f"Error reading cache file: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Search NixOS packages with caching')
    parser.add_argument('search_term', help='Term to search for in package names and descriptions')
    parser.add_argument('-f', '--force', action='store_true', 
                        help='Force refresh of package cache')
    args = parser.parse_args()

    cache_file = get_unique_cache_file()

    # Update cache if forced or if cache doesn't exist
    if args.force or not os.path.exists(cache_file):
        update_cache(cache_file)
    else:
        # Check if cache is older than 24 hours
        cache_age = datetime.now().timestamp() - os.path.getmtime(cache_file)
        if cache_age > 86400:  # 24 hours in seconds
            print("Cache is older than 24 hours. Updating...")
            update_cache(cache_file)

    print(f"Searching for: {args.search_term}")
    print("-" * 40)
    search_packages(cache_file, args.search_term)

if __name__ == "__main__":
    main()