import os
import platform
import argparse
import zipfile
import hashlib
import sys
import json
import tempfile
import shutil
from enum import IntEnum
from json import JSONDecodeError
from pathlib import Path
from zipfile import BadZipfile

class Language(IntEnum):
    """
        For the language selector menu.
        May be expanded by the community.
    """
    ENGLISH = 1
    ESPANOL = 2

def main():
    # Arguments used by the program.
    parser = argparse.ArgumentParser(description = "Analyzes Instagram data files to find non-mutual followings (moots) and vice-versa.")
    parser.add_argument("zip_file_path", type = Path, help = "Path to the .zip file containing the information from the desired Instagram account.")
    parser.add_argument("-o", "--output", type = Path, dest = "output_file_path", help = "Writes the final report to the specified text file instead of printing to the console.")
    args = parser.parse_args()
    zip_path = args.zip_file_path
    output_file_path = args.output_file_path

    # Checks if the provided ZIP file is in fact a valid ZIP file.
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.testzip()
    except BadZipfile:
        print("ERROR: Bad argument.", file = sys.stderr)
        sys.exit(1)

    # Calculates the MD5 hash of the ZIP file.
    hasher = hashlib.md5()
    try:
        with zip_path.open('rb') as f:
            while chunk := f.read(4096):
                hasher.update(chunk)
            zip_hash = hasher.hexdigest()
    except IOError as e:
        print(e, file = sys.stderr)
        sys.exit(1)

    # Creates the working directory.
    working_dir = Path(tempfile.gettempdir()) / f"periflo/moots/{zip_hash}"
    try:
        working_dir.mkdir(parents = True, exist_ok = True)
        print("Working path OK.")
    except (OSError, PermissionError) as e:
        print(e, file = sys.stderr)
        sys.exit(1)

    # Extracts the contents of the ZIP file in the working directory.
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(working_dir)
            print("ZIP file OK.")
    except (BadZipfile, IOError, OSError) as e:
        print(e, file = sys.stderr)
        sys.exit(1)

    # Checks if the data files exist.
    following_file =  working_dir / "connections/followers_and_following/following.json"
    followers_file =  working_dir / "connections/followers_and_following/followers_1.json"
    if not following_file.is_file() or not followers_file.is_file():
        print("ERROR: Data files not found.", file = sys.stderr)
        sys.exit(1)

    # Checks if the following data file is a valid JSON and parses it. Stores the users in a list.
    try:
        with following_file.open('r', encoding = "utf-8") as f:
            data = json.load(f)
            print("Following data OK.")

            main_list = data.get("relationships_following", [])

            if not main_list:
                print("ERROR: Damaged data file.", file = sys.stderr)
                sys.exit(1)

            following = [
                inner_element["href"]
                for main_element in main_list
                for inner_element in main_element.get("string_list_data", [])
                if "href" in inner_element
            ]
    except (IOError, JSONDecodeError) as e:
        print(e, file = sys.stderr)
        sys.exit(1)

    # Cleans the users so only the usernames remain.
    following = [
        url.rstrip("/").rsplit("/", 1)[-1].strip().lower()
        for url in following
    ]
    print("Parsing following data OK.")

    # Checks if the followers data file is a valid JSON and parses it. Stores the users in a list.
    try:
        with followers_file.open('r', encoding = "utf-8") as f:
            data = json.load(f)
            print("Followers data OK.")
            if not isinstance(data, list) and data:
                print("ERROR: Damaged data file.", file = sys.stderr)
                sys.exit(1)

            followers = [
                element["href"]
                for dictionary in data
                for element in dictionary.get("string_list_data", [])
                if "href" in element
            ]

    except (IOError, JSONDecodeError) as e:
        print(e, file = sys.stderr)
        sys.exit(1)

    # Cleans the users so only the usernames remain.
    followers = [
        url.rstrip("/").rsplit("/", 1)[-1].strip().lower()
        for url in followers
    ]
    print("Parsing followers data OK.")

    # Compares and sorts sets of users.
    following_set = set(following)
    followers_set = set(followers)

    they_dont_follow_you_back_set = following_set - followers_set
    they_dont_follow_you_back_list = sorted(list(they_dont_follow_you_back_set))

    you_dont_follow_them_back_set = followers_set - following_set
    you_dont_follow_them_back_list = sorted(list(you_dont_follow_them_back_set))

    print("Comparison of sets OK.")

    # Clears the console.
    clear_console()

    # Language selector.
    print("* * * * * SELECT A LANGUAGE * * * * *")
    print(f"{Language.ENGLISH.value} - English")
    print(f"{Language.ESPANOL.value} - Español")

    while True:
        try:
            selection = int(input("> "))
            selected_language = Language(selection)
            break
        except ValueError:
            print("Try again.")

    # Clears the console.
    clear_console()

    # By default, outputs to the console.
    output_destination = sys.stdout

    # Changes the mode to output to a file.
    if output_file_path:
        try:
            output_destination = output_file_path.open("w", encoding = "utf-8")
        except IOError as e:
            print(e, file = sys.stderr)
            sys.exit(1)

    # Prints or writes to a file the results.
    if selected_language.value == 1:
        title_a = "THE FOLLOWING ACCOUNTS DON'T FOLLOW YOU BACK:"
        title_b = "YOU DON'T FOLLOW BACK THE FOLLOWING ACCOUNTS:"
        none = "- None -"
    elif selected_language.value == 2:
        title_a = "LAS SIGUIENTES CUENTAS NO TE SIGUEN DE VUELTA:"
        title_b = "NO SIGUES DE VUELTA A LAS SIGUIENTES CUENTAS:"
        none = "- Ninguna -"

    output_destination.write(title_a + "\n")

    if they_dont_follow_you_back_list:
        for account in they_dont_follow_you_back_list:
            output_destination.write(account + "\n")
    else:
        output_destination.write(none + "\n")

    output_destination.write("\n")

    output_destination.write(title_b + "\n")

    if you_dont_follow_them_back_list:
        for account in you_dont_follow_them_back_list:
            output_destination.write(account + "\n")
    else:
        output_destination.write(none + "\n")

    if output_destination is not sys.stdout:
        output_destination.close()

    # The program cleans after itself.
    try:
        if working_dir.exists():
            shutil.rmtree(working_dir)
    except (OSError, PermissionError) as e:
        print(f"WARNING: Could not remove temporary directory {working_dir}. {e}", file = sys.stderr)

def clear_console():
    """
    Clears the console.
    """
    if platform.system() in ("Linux", "Darwin"):
        os.system("clear")
    elif platform.system() == "Windows":
        os.system("cls")
    else:
        print("\n" * 50)

if __name__ == "__main__":
    main()