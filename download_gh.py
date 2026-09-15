import urllib.request
import zipfile
import os

url = "https://github.com/cli/cli/releases/download/v2.54.0/gh_2.54.0_windows_amd64.zip"
zip_path = "gh.zip"

print("Downloading GitHub CLI...")
urllib.request.urlretrieve(url, zip_path)

print("Extracting...")
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall("gh_cli")

print("Done.")
