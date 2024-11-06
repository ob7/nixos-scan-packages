#!/usr/bin/env python3

import argparse
import subprocess
import os
import hashlib
import sys
from datetime import datetime
import re

# ANSI color codes for highlighting
RED = '\033[91m'
RESET = '\033[0m'

def get_unique_cache_file():
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

def highlight_matches(line, search_term, exact_match=False):
    if exact_match:
        pattern = re.compile(f'({re.escape(search_term)})')
    else:
        pattern = re.compile(f'({re.escape(search_term)})', re.IGNORECASE)
    return pattern.sub(f'{RED}\\1{RESET}', line)

def search_packages(cache_file, search_term, exact_match=False):
    try:
        with open(cache_file, 'r') as f:
            for line in f:
                matches = False
                if exact_match:
                    matches = search_term in line
                else:
                    matches = search_term.lower() in line.lower()
                
                if matches:
                    highlighted_line = highlight_matches(line.strip(), search_term, exact_match)
                    print(highlighted_line)
    except IOError as e:
        print(f"Error reading cache file: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Search NixOS packages with caching')
    parser.add_argument('search_term', help='Term to search for in package names and descriptions')
    parser.add_argument('-f', '--force', action='store_true', 
                        help='Force refresh of package cache')
    parser.add_argument('-e', '--exact', action='store_true',
                        help='Exact match (case sensitive)')
    parser.add_argument('--no-color', action='store_true',
                        help='Disable colored output')
    args = parser.parse_args()

    # Disable colors if requested or if output is not to a terminal
    if args.no_color or not sys.stdout.isatty():
        global RED, RESET
        RED = ''
        RESET = ''

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

    print(f"Searching for: {args.search_term} ({'exact match' if args.exact else 'case insensitive'})")
    print("-" * 40)
    search_packages(cache_file, args.search_term, args.exact)

if __name__ == "__main__":
    main()
