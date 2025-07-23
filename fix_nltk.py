import os
import shutil
import nltk
import zipfile

# Define where NLTK data lives inside your virtual environment
venv_nltk_dir = os.path.join('venv', 'nltk_data')

# Step 1: Remove existing nltk_data folder
if os.path.exists(venv_nltk_dir):
    print(f"Removing existing {venv_nltk_dir}...")
    shutil.rmtree(venv_nltk_dir)
else:
    print(f"No existing {venv_nltk_dir} found, skipping deletion.")

# Step 2: Re-download NLTK resources to venv
resources = ['punkt', 'wordnet', 'omw-1.4']
print(f"Downloading NLTK resources to {venv_nltk_dir}...")

for res in resources:
    nltk.download(res, download_dir=venv_nltk_dir)

# Step 3: Unzip any .zip files into folders
print("Checking for .zip files to extract...")

for root, dirs, files in os.walk(venv_nltk_dir):
    for file in files:
        if file.endswith('.zip'):
            zip_path = os.path.join(root, file)
            target_dir = os.path.join(root, file.replace('.zip', ''))

            print(f"Extracting {zip_path} to {target_dir}...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                os.makedirs(target_dir, exist_ok=True)
                zip_ref.extractall(target_dir)

            print(f"Deleting original zip file {zip_path}...")
            os.remove(zip_path)

print("All NLTK data downloaded and unzipped successfully!")
