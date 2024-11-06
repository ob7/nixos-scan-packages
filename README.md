# nixos-scan-packages
Quickly check what packages are available to your NixOS machine

# NixOS Package Search Tool

This project provides a Python-based CLI tool for searching NixOS packages. It uses caching to improve search performance, especially for repeated searches. The script supports various search modes and can highlight matching terms in the results for better readability.

## Features

- **Caching**: Automatically caches package information for faster subsequent searches.
- **Search Modes**:
  - Case-sensitive search
  - Whole word match
  - Match at the end of package names
  - Exact component match
- **Customizable Output**: Option to enable or disable colored output for matched terms.
- **Automatic Cache Refresh**: Cache updates automatically if it's older than 24 hours.

## Requirements                                                                                                                
- **NixOS**: The tool uses `nix-env` to fetch package details, and is intended to be ran on NixOS
- **Python 3**: Ensure Python 3 is installed.


## Usage

Run the script with a search term to look for NixOS packages. The tool provides several optional flags for different search behaviors.

### Basic Command

```bash
python search-nixos-packages.py <search_term>
```

### Options

- **`-f`, `--force`**: Force refresh the package cache, even if it’s less than 24 hours old.
- **`-x`**: Case-sensitive match.
- **`-xx`**: Match whole words only, ensuring the search term is a separate word.
- **`-xxx`**: Match at the end of package names, restricting results to packages where the term appears at the end.
- **`-xxxx` or `-e`**: Match exact package name components only, highlighting packages that match the term exactly, either at the start or after a period.
- **`--no-color`**: Disable colored output for matched terms.

### Examples

1. **Simple Search** (case-insensitive):
   ```bash
   python search-nixos-packages.py firefox
   ```

2. **Case-Sensitive Search**:
   ```bash
   python search-nixos-packages.py -x firefox
   ```

3. **Exact Package Component Search**:
   ```bash
   python search-nixos-packages.py -xxxx firefox
   ```

4. **Force Update Cache**:
   ```bash
   python search-nixos-packages.py firefox -f
   ```

5. **Shorthand for Exact Component Search**:
   ```bash
   python search-nixos-packages.py -e firefox
   ```

### Output Example

Running the command below highlights `firefox` as an exact package component, showing only matches where `firefox` appears precisely as part of the package name or after a period.

```bash
python search-nixos-packages.py -e firefox
```

```
Searching for: firefox (exact package name components only)
----------------------------------------
nixos.firefox              A web browser built from Firefox source tree
```

## How It Works

1. **Caching**: The script saves package information to a unique cache file in `/tmp`. The cache is refreshed automatically if it's older than 24 hours, or can be forced to refresh using the `-f` flag.
2. **Matching and Highlighting**: The tool provides multiple matching modes to customize the search behavior. It highlights matching terms in red by default, which can be disabled with the `--no-color` option.

## Code Structure

- **`highlight_matches`**: Highlights the matched search term in the output line.
- **`search_packages`**: Reads the cached package file and applies the search term with the chosen match type.
- **`update_cache`**: Updates the package cache by calling `nix-env`.
- **`main`**: Manages argument parsing, cache checking, and initiates the search.
