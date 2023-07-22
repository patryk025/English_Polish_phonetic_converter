# English Polish phonetic converter
This program converts an English sentence into a textual representation of the pronunciation in Polish. For example sentence "King Julien is the greatest king in the world." will be converted into "king dżulien iz de grejtest king in de łerld.".

The program uses the The CMU Pronouncing Dictionary (English->ARPAbet dictionary) to convert English words into phonemes, and then translates them into Polish.

Included support for Mekatron/Tacotron2 and Flowtron datasets.

Requirements:
- Python 3
- gdown (to download dictionary file)

usage: converter.py -i INPUT [-o OUTPUT]

-i INPUT, --input INPUT => Ścieżka do pliku z tekstem do przetworzenia

-o OUTPUT, --output OUTPUT => Ścieżka do zapisu wyniku