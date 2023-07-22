#!python
# coding: utf-8

import re
regex = r"(\({0,1})(\{(.*?)\}|([A-Z]{1,2}[0-2]{0,1}))([.,?!\)]{0,1})"

def downloadDictionary():
    from os.path import exists

    if not exists("dictionary.txt"):
        import gdown
        gdown.download("https://drive.google.com/uc?id=1uciIczSNxzjhWZEzJ_gB2pzLGrtXSQHc", "dictionary.txt", quiet=False)

cmudict = {}

def ARPA(text):
    out = ''
    for word_ in text.split(" "):
        word=word_; end_chars = ''; start_chars = ''
        while any(elem in word for elem in r"!?,.;\(\)") and len(word) > 1:
            if word[-1] == '!': end_chars = '!' + end_chars; word = word[:-1]
            if word[-1] == '?': end_chars = '?' + end_chars; word = word[:-1]
            if word[-1] == ',': end_chars = ',' + end_chars; word = word[:-1]
            if word[-1] == '.': end_chars = '.' + end_chars; word = word[:-1]
            if word[-1] == ';': end_chars = ';' + end_chars; word = word[:-1]
            if word[-1] == ')': end_chars = ')' + end_chars; word = word[:-1]
            if word[0] == '(': start_chars = '(' + start_chars; word = word[1:]
            else: break
        try: word_arpa = cmudict[word.upper()]
        except: word_arpa = '[' + word + ']' #brak słowa w słowniku
        if len(word_arpa)!=0: word = "{" + str(word_arpa) + "}"
        out = (out + " " + start_chars + word + end_chars).strip()
    return out

def ARPAtoPolishPhonemes(ARPAphoneme):
    if ARPAphoneme[0] == '[' and ARPAphoneme[-1] == ']':
        return ARPAphoneme[1:-1] #zwróć słowa, których nie ma w słowniku bez zmian

    stress = ''
    if ARPAphoneme[-1] == '0' or ARPAphoneme[-1] == '1' or ARPAphoneme[-1] == '2':
        stress = ARPAphoneme[-1]
        ARPAphoneme = ARPAphoneme[:-1]
    return {
        #vowels
        'AA': 'o' if stress == '0' else 'a',
        'AE': 'e',
        'AH': 'e' if stress == '0' else 'a' if stress == '1' else 'o',
        'AO': 'o',
        'AW': 'oł',
        'AX': 'a',
        'AXR': 'er',
        'AY': 'aj',
        'EH': 'e',
        'ER': 'er',
        'EY': 'ej',
        'IH': 'i',
        'IX': 'i',
        'IY': 'i',
        'OW': 'oł',
        'OY': 'oj',
        'UH': 'u' if stress == '0' else 'ou',
        'UW': 'u',
        'UX': 'u',
        #consonants
        'B': 'b',
        'CH': 'cz',
        'D': 'd',
        'DH': 'd',
        'DX': 'w',
        'EL': 'yl',
        'EM': 'ym',
        'EN': 'yn',
        'F': 'f',
        'G': 'g',
        'H': 'h',
        'HH': 'h',
        'JH': 'dż',
        'K': 'k',
        'L': 'l',
        'M': 'm',
        'N': 'n',
        'NG': 'ng',
        'NX': 'n',
        'P': 'p',
        'Q': 'kju',
        'R': 'r',
        'S': 's',
        'SH': 'sz',
        'T': 't',
        'TH': 'f',
        'V': 'w',
        'W': 'ł',
        'WH': 'ł',
        'Y': 'j',
        'Z': 'z',
        'ZH': 'ż',
    }[ARPAphoneme]

def proceedARPA(text):
    matches = re.finditer(regex, text, re.MULTILINE)
    
    result = ""
    
    for matchNum, match in enumerate(matches, start=1):
        group1 = match.group(1) #znaki zaczynające (nawiasy)
        group3 = match.group(3) #fonemy w klamrach
        group4 = match.group(4) #pojedyncze fonemy (bez klamr)
        group5 = match.group(5) #znaki kończące
        
        if group1 != '':
            result += group1.strip()
        if group3 is not None:
            group3 = group3.strip()
            group3Phonemes = group3.split(" ")
            for phoneme in group3Phonemes:
                result += ARPAtoPolishPhonemes(phoneme)
        if group4 is not None:
            group4 = group4.strip()
            result += ARPAtoPolishPhonemes(group4)
        if group5 != '':
            result += group5.strip()
        
        result += " "
    return result[:-1]

def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Ścieżka do pliku z tekstem do przetworzenia", required = True)
    parser.add_argument("-o", "--output", help="Ścieżka do zapisu wyniku")
    args = parser.parse_args()
    inputFile = args.input
    if args.output:
        outputFile = args.output
    else:
        outputFile = inputFile + "-converted.txt" # nie chciało mi się pisać bardziej wyrafinowanego rozwiązania

    downloadDictionary()

    for line in reversed((open('dictionary.txt', "r", encoding='utf-8').read()).splitlines()):
        if line.startswith(";;;"): continue #komentarz
        word, phonemes = line.split(" ",1);
        cmudict[word] = phonemes.strip()

    isMekatron = False; isFlowtron = False; checked = False

    dataset_flowtron = r"(.+)\|(.+)\|(\d+)"
    dataset_mekatron = r"(.+)\|(.+)"

    result = ""

    output_file = open(outputFile, 'w')

    for line in (open(inputFile, "r", encoding='utf-8').read().splitlines()):
        if not checked:
            if re.match(dataset_flowtron, line):
                isFlowtron = True
                print("Detected Flowtron (or something similar) dataset")
            elif re.match(dataset_mekatron, line):
                print("Detected Mekatron/Tacotron2 dataset")
                isMekatron = True
            else:
                print("No datasets detected, probably normal text file")
            checked = True
        if isFlowtron:
            try:
                wav, text, speaker = line.split("|", 2)
                result = wav + "|" + proceedARPA(ARPA(text)) + "|" + speaker
            except:
                result = ''
                print("Something is wrong with line {}. Omitting...".format(line))
        elif isMekatron:
            try:
                wav, text = line.split("|", 1)
                result = wav + "|" + proceedARPA(ARPA(text))
            except:
                result = ''
                print("Something is wrong with line {}. Omitting...".format(line))
        else:
            result = proceedARPA(ARPA(line))

        if result != '':
            print(result)
            #print(ARPA(line))
            output_file.write(result + "\n")
    
    output_file.close()

if __name__ == "__main__":
    main()
