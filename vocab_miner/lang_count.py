import re
import shutil
from collections import Counter
import random


transcripts = {
    'spa': [
        'anuelaa_amanece.txt',
        'badbunny_titimepregunto.txt',
        'chrisjeday_ahoradice.txt',
        'karolg_provenza.txt',
        'lunay_aventura.txt',
        'rauwalejandro_babyhello.txt',
        'tainy_adicto.txt',
        'youngmiko_algocasual.txt',
    ],
    'rus': [
        'miaboyka_lyrics.txt',
        'miaboyka_lyrics2.txt',
    ],
}


def get_lang_choice():
    while True:
        language_full = input(
            '\nWhat language is the file in?\n>> ').strip().lower()
        if len(language_full) < 3:
            print('\nPlease provide the first 3 letters of the language or more.')
            continue
        lang = language_full[0:3]
        return lang


skip_choice = None


print('Welcome to the Vocab Miner!')

# get user action choice

while True:
    choice = input("""
What would you like to do?
                   
> Mine = Isolate study worthy vocab from a text file
> Add  = Add words to your Known Words List(s)
> Stop = Add words to your Stop Words List(s)
> Exit = Close the program

>> """).lower().strip()

# allow for language-agnostic vocab mining, including option to quit to main menu

    if choice == 'mine':

        # loop to get a valid filename from the user following missing file, contains option to quit to main menu

        while True:
            filename = input(
                '\nEnter the filename. You can also enter "random" for a random transcript or "quit" to return to menu:\n>> ').lower().strip()
            if filename == 'quit':
                break
            elif filename == 'random':
                skip_choice = True
                lang = get_lang_choice()
                try:
                    filename = random.choice(transcripts[lang])
                except:
                    print('\nNo transcripts found in that language.')

        # try/except tree to allow for multiple file locations, including a direct path to the file, adding convenience

            try:
                with open(f'transcripts/spanish/{filename}', 'r', encoding='utf-8') as file:
                    text = file.read().lower()
                break
            except:
                try:
                    with open(f'transcripts/russian/{filename}', 'r', encoding='utf-8') as file:
                        text = file.read().lower()
                    break
                except:
                    try:
                        with open(f'transcripts/{filename}', 'r', encoding='utf-8') as file:
                            text = file.read().lower()
                        break
                    except:
                        try:
                            with open(filename, 'r', encoding='utf-8') as file:
                                text = file.read().lower()
                            break
                        except:
                            print('No file was found at that address.')

        if filename == 'quit':
            continue

    # loop to get a valid language choice from the user, including standardization of inputs, and option to quit to main menu

        while True:
            continue_choice = -1
            stop_words = []
            if not skip_choice:
                lang = get_lang_choice()

        # try to open the stop words list for the language choice, if it fails, prompt user to continue or return to main menu

            try:
                with open(f'filters/stop_words/stop_words_{lang}.txt', 'r', encoding='utf-8') as f:
                    stop_words = [line.strip().lower()
                                  for line in f if line.strip()]
                break
            except:
                print(
                    '\nWARNING: No Stop Words list was found in that language choice. Continue?')
                continue_choice = input(
                    '"Y" = Continue, "N" = Main Menu, "R" = Re-try\n>> ').lower().strip()
                if continue_choice == 'n':
                    break
                elif continue_choice == 'y':
                    break
        if continue_choice == 'n':
            continue

    # loop to get a valid response from the user regarding whether or not to use a Known Words filter, including option to quit to main menu

        while True:
            filter_list = input(
                '\nWould you like to use a "Known Words" filter? (y/n)\n>> ').lower().strip()
            if filter_list == 'y':

                # try to open the Known Words list for the language choice, if it fails, prompt user to continue without a Known Words list, try again, or return to main menu

                try:
                    with open(f'filters/known_words/known_words_{lang}.txt', 'r', encoding='utf-8') as f:
                        known_words = [line.strip().lower()
                                       for line in f if line.strip()]
                        break
                except:
                    print(
                        'WARNING: No Known Words list was found for that language choice.\nContinuing without a Known Words list.')
                    known_words = []
                    break
            elif filter_list == 'n':
                known_words = []
                break
            elif filter_list == 'quit':
                break
            else:
                print('Invalid input. Please respond with "y" or "n".')
        if filter_list == 'quit':
            continue

    # process the text to isolate words, count them, and print a filtered list of words with their counts
        words = re.findall(r"\b\w+(?:'\w+)*\b", text, flags=re.UNICODE)
        lines = text.split('\n')
        counts = Counter(words)
        n = 0
        print('\nVocabulary list (filtered):\n---------------------------')
        for word, count in counts.most_common():
            if word not in stop_words and word not in known_words:
                for line in lines:
                    if word in line:
                        word_line = line
                n += 1
                print(f'{n}: {word} - {count} | {word_line}')
        print(f'-----------------------------\nYou found {n} words to study out of {len(counts)} total words!')

# allow for adding of words to a known words list, including input standardization and option to quit to main menu
    elif choice == 'add':
        while True:
            language_full = input('\nWhich Known Words list would you like to add to?\n>> ').lower().strip()
            if len(language_full) < 3:
                print('\nPlease provide the first 3 letters of the language or more.')
                continue
            break

    # try to open the Known Words list for the language choice, if it fails, create a new Known Words list for that language
        lang = language_full[0:3]
        try:
            with open(f'filters/known_words/known_words_{lang}.txt', 'r', encoding='utf-8') as f:
                known_words = [line.strip().lower()
                               for line in f if line.strip()]
        except:
            known_words = []

    # prompt user for words to add to the Known Words list, standardize input, and write the updated list to file
        add_words_str = input('What words would you like to add to the list? Separate the words only with spaces.\n>> ').lower().strip()
        add_words = [add_words_str.split()]
        for word in add_words:
            if word in known_words:
                continue
            known_words.extend(word)
            known_words.sort()

    # try to copy the existing Known Words list to a backup file, if it fails, print a message that the Known Words list is being created, then write the updated Known Words list to file
        try:
            shutil.copy(f'filters/known_words/known_words_{lang}.txt',
                        f'filters/known_words/backups/known_words_{lang}_backup.txt')
            print(f'\nCreating backup of known_words_{lang}.txt')
        except:
            print(f'Creating known_words_{lang}.txt')
        with open(f'filters/known_words/known_words_{lang}.txt', 'w', encoding='utf-8') as f:
            for word in known_words:
                f.write(f'{word}\n')
        print(f'"{add_words_str}" {'has' if len(add_words) == 1 else 'have'} successfully been added to known_words_{lang}.txt')
        print(f'The list is now {len(known_words)} words long.')

# all for adding words to stop words list from within the program
    elif choice == 'stop':
        while True:
            language_full = input("""
What stop words list would you like to add to?
Please enter the full language name or "done" to return to the menu.
>> """).lower().strip()
            if len(language_full) < 3:
                print('\nPlease provide the first 3 letters of the language or more.')
                continue
            break
    # try to open the Known Words list for the language choice, if it fails, create a new Known Words list for that language
        lang = language_full[0:3]
        try:
            with open(f'filters/stop_words/stop_words_{lang}.txt', 'r', encoding='utf-8') as f:
                stop_words = [line.strip().lower() for line in f if line.strip()]
        except:
            known_words = []
    # prompt user for words to add to the Stop Words list, standardize input, and write the updated list to file
        add_words_str = input('\n\nWhat words would you like to add to the list? Separate the words only with spaces.\n>> ').lower().strip()
        add_words = [add_words_str.split()]
        for word in add_words:
            if word in stop_words:
                continue
            stop_words.extend(word)
            stop_words.sort()
    # try to copy the existing Stop Words list to a backup file, if it fails, print a message that the Stop Words list is being created, then write the updated Stop Words list to file
        try:
            shutil.copy(f'filters/stop_words/stop_words_{lang}.txt',
                        f'filters/stop_words/backups/stop_words_{lang}_backup.txt')
            print(f'\nCreating backup of stop_words_{lang}.txt')
        except:
            print(f'Creating stop_words_{lang}.txt')
        with open(f'filters/stop_words/stop_words_{lang}.txt', 'w', encoding='utf-8') as f:
            for word in stop_words:
                f.write(f'{word}\n')
        print(f'"{add_words_str}" {'has' if len(add_words) == 1 else 'have'} successfully been added to stop_words_{lang}.txt')

# allow for exiting the program
    elif choice == 'exit':
        exit()

# handle invalid user input

    else:
        print('Invalid input.')
