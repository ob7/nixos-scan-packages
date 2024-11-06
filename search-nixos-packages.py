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

def highlight_matches(line, search_term, match_type='normal'):
    if match_type == 'case_sensitive':  # -x
        pattern = re.compile(f'({re.escape(search_term)})')
    elif match_type == 'word_boundary':  # -xx
        pattern = re.compile(f'\\b({re.escape(search_term)})\\b')
    elif match_type == 'end_boundary':   # -xxx
        pattern = re.compile(f'({re.escape(search_term)})(?=$|\\s)')
    elif match_type == 'exact_component': # -xxxx
        # Match start of line or dot, capture the search term, and ensure it ends at whitespace or end of line
        pattern = re.compile(f'(^|\\.)({re.escape(search_term)})(?=$|\\s)')
    else:  # normal case-insensitive
        pattern = re.compile(f'({re.escape(search_term)})', re.IGNORECASE)

    # Apply the substitution, handling boundaries properly for exact_component
    if match_type == 'exact_component':
        return pattern.sub(lambda m: f'{m.group(1)}{RED}{m.group(2)}{RESET}', line)
    else:
        return pattern.sub(f'{RED}\\1{RESET}', line)


def search_packages(cache_file, search_term, match_type='normal'):
    try:
        with open(cache_file, 'r') as f:
            for line in f:
                matches = False
                # Split the line into package name and description
                parts = line.strip().split(None, 1)
                if not parts:
                    continue
                    
                package_name = parts[0]
                
                if match_type == 'case_sensitive':  # -x
                    matches = search_term in line
                elif match_type == 'word_boundary':  # -xx
                    matches = bool(re.search(f'\\b{re.escape(search_term)}\\b', line))
                elif match_type == 'end_boundary':   # -xxx
                    matches = bool(re.search(f'{re.escape(search_term)}(?:$|\\s)', package_name))
                elif match_type == 'exact_component': # -xxxx
                    matches = bool(re.search(f'(?:^|\\.)' + re.escape(search_term) + '(?:$|\\s)', package_name))
                else:  # normal case-insensitive
                    matches = search_term.lower() in line.lower()
                
                if matches:
                    highlighted_line = highlight_matches(line.strip(), search_term, match_type)
                    print(highlighted_line)
    except IOError as e:
        print(f"Error reading cache file: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Search NixOS packages with caching')
    parser.add_argument('search_term', help='Term to search for in package names and descriptions')
    parser.add_argument('-f', '--force', action='store_true', 
                        help='Force refresh of package cache')
    parser.add_argument('-x', action='store_true',
                        help='Case sensitive match')
    parser.add_argument('-xx', action='store_true',
                        help='Match whole words only')
    parser.add_argument('-xxx', action='store_true',
                        help='Match at end of package names')
    parser.add_argument('-xxxx', action='store_true',
                        help='Match exact package name components only')
    parser.add_argument('-e', action='store_true',
                        help='Most strict matching (same as -xxxx)')
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

    # Determine match type (most specific flag wins)
    match_type = 'normal'
    if args.e or args.xxxx:
        match_type = 'exact_component'
    elif args.xxx:
        match_type = 'end_boundary'
    elif args.xx:
        match_type = 'word_boundary'
    elif args.x:
        match_type = 'case_sensitive'

    match_description = {
        'normal': 'case insensitive',
        'case_sensitive': 'case sensitive',
        'word_boundary': 'whole words only',
        'end_boundary': 'matches at end of names',
        'exact_component': 'exact package name components only'
    }

    print(f"Searching for: {args.search_term} ({match_description[match_type]})")
    print("-" * 40)
    search_packages(cache_file, args.search_term, match_type)

if __name__ == "__main__":
    main()
