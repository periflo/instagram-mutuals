# Instagram Mutuals

A command-line application that helps you determine who you follow that doesn't follow you back on Instagram.

---

### Prerequisites
* **Python 3** installed and accessible from your command line.
* A ZIP file containing your Instagram data (explained below).

---

### How to get your Instagram data in a ZIP file:
* Navigate to the Data Download page [here](https://accountscenter.instagram.com/info_and_permissions/dyi/).
* Click the big blue button that says "Create export."
* Select "Export to device."
* Select "Customise information."
* Uncheck everything **except** "Connections > Followers and following," then click "Save."
* Set "Date range" to "All time," then click "Save."
* Set "Format" to "JSON," then click "Save."
* Click the big blue button that says "Start export."
* Enter your Instagram password and click "Continue."
* Wait for an email from Meta to arrive at your associated email address. This may take some time.
* Navigate to the data download page again [here](https://accountscenter.instagram.com/info_and_permissions/dyi/?entry_point=notification).
* Download your requested data via the link provided in the email.

---

### How to use
* Download the source code or the release.
* Unzip the archive.
* Open your command-line interface (CLI) and navigate to the unzipped folder.
* Run the program. The syntax is as follows:

Linux / macOS
```
$ python3 moots.py /path/to/instagram/zip/file [-o /path/to/report/file]
```

Windows
```
> python3 moots.py path\to\instagram\zip\file [-o path\to\report\file]
```

---

### Arguments
The script accepts one mandatory positional argument and one optional flag:

* **Positional Argument:**
    * `zip_file_path`: The full path to the Instagram data ZIP file.

* **Optional Flag:**
    * `-o, --output FILENAME_PATH`: Writes the final report to the **specified file path** (`FILENAME_PATH`) instead of printing directly to the console (stdout).

---

### Considerations
* This program has been tested against a small Instagram account (less than 100 following and followers). If your ZIP file contains more than one file for following or followers (e.g., `followers_1.json`, `followers_2.json`), please open a pull request.
* **Important:** If someone has disabled or deleted their account, it will still appear in the results, as network validation is currently blocked by Meta's anti-scraping policies.
