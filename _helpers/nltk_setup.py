# _helpers/nltk_setup.py
import nltk
import os

def ensure_nltk_resources():
    venv_base = os.path.dirname(os.path.dirname(nltk.__file__))
    nltk_data_dir = os.path.join(venv_base, 'nltk_data')

    if not os.path.exists(nltk_data_dir):
        os.makedirs(nltk_data_dir)
        print(f"Created nltk_data directory at {nltk_data_dir}")

    if nltk_data_dir not in nltk.data.path:
        nltk.data.path.insert(0, nltk_data_dir)

    resources = [
        'punkt',
        'wordnet',
        'omw-1.4',
        'averaged_perceptron_tagger',
        'averaged_perceptron_tagger_eng'
    ]

    for resource in resources:
        try:
            if resource == 'punkt':
                nltk.data.find(f'tokenizers/{resource}')
            elif 'tagger' in resource:
                nltk.data.find(f'taggers/{resource}')
            else:
                nltk.data.find(f'corpora/{resource}')
            print(f"NLTK resource '{resource}' already installed in venv.")
        except LookupError:
            print(f"Downloading NLTK resource '{resource}' to {nltk_data_dir}...")
            nltk.download(resource, download_dir=nltk_data_dir)

    print("All required NLTK resources are ready.")
