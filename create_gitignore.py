import os

# Create .gitignore so we don't commit unnecessary files
gitignore = """
__pycache__/
pw_profile/
cookies.json
*.har
script_content.txt
rsc_decoded.txt
fetched_schedule.html
schedule.html
"""
with open(r"C:\Users\nagat\Downloads\SCHEDULEwidget\.gitignore", "w") as f:
    f.write(gitignore)
