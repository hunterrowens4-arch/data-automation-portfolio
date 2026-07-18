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

def add_known_words():
    language = input('\nWhich Known Words list would you like to add to?\n>> ').lower().strip()

    # try to open the Known Words list for the language choice, if it fails, create a new Known Words list for that language
    try:
        known_words = load_known_words(language)
    except FileNotFoundError:
        known_words = []

    # prompt user for words to add to the Known Words list, standardize input, and write the updated list to file
    add_words_str = input('\nWhat words would you like to add to the list? Separate the words only with spaces.\n>> ').lower().strip()
    add_words = [add_words_str.split()]
    known_words = extend_list(known_words, add_words)

    # try to copy the existing Known Words list to a backup file, if it fails, print a message that the Known Words list is being created, then write the updated Known Words list to file
    copy_words_list("known_words", language)
    save_words_list("known_words", known_words, language)

def add_stop_words():
    language = input('\nWhich Stop Words list would you like to add to?\n>> ').lower().strip()

    # try to open the Stop Words list for the language choice, if it fails, create a new Stop Words list for that language
    try:
        stop_words = load_stop_words(language)
    except FileNotFoundError:
        stop_words = []

    # prompt user for words to add to the Stop Words list, standardize input, and write the updated list to file
    add_words_str = input('\nWhat words would you like to add to the list? Separate the words only with spaces.\n>> ').lower().strip()
    add_words = [add_words_str.split()]
    stop_words = extend_list(stop_words, add_words)

    # try to copy the existing Stop Words list to a backup file, if it fails, print a message that the Stop Words list is being created, then write the updated Stop Words list to file
    copy_words_list("stop_words", language)
    save_words_list("stop_words", language)

def analyze_transcript(text, stop_words, known_words):
    words = re.findall(r"\b\w+(?:'\w+)*\b", text, flags=re.UNICODE)
    lines = text.split("\n")
    counts = Counter(words)

    n = 0
    results = []

    for word, count in counts.most_common():
        if word not in stop_words and word not in known_words:

            example_line = ""
            for line in lines:
                if word in line:
                    example_line = line
                    break  # optional improvement

            n += 1
            results.append((n, word, count, example_line))

    return results, counts

def copy_words_list(words_list, language):
    try:
        shutil.copy(f'filters/{words_list}/{words_list}_{language}.txt',
                    f'filters/{words_list}/backups/{words_list}_{language}_backup.txt')
        print(f'\nCreating backup of {words_list}_{language}.txt')
    except:
        print(f'Creating {words_list}_{language}.txt')

def extend_list(word_list, words):
    for word in words:
        if word in word_list:
            continue
    word_list.extend(word)
    word_list.sort()
    return word_list

def get_transcript_request():
    # RANDOM FUNCTION DISABLED FOR REFRACTORING
    # QUIT FUNCTION DISABLED FOR REFRACTORING
    filename = input(
        '\nEnter the filename\n>> '
    ).lower().strip()
    
    language = input(
        '\nWhat language is the transcript in? Please enter the full language (for example: "Spanish")\n>> '
    ).lower().strip()

    return filename, language

def load_known_words(language):
    try:
        with open(f'filters/known_words/known_words_{language}.txt', 'r', encoding='utf-8') as f:
            known_words = [line.strip().lower()
                            for line in f if line.strip()]
        return known_words
    except FileNotFoundError:
        raise

def load_stop_words(language):
    try:
        with open(f'filters/stop_words/stop_words_{language}.txt', 'r', encoding='utf-8') as f:
            stop_words = [line.strip().lower()
                            for line in f if line.strip()]
        return stop_words
    except FileNotFoundError:
        raise

def load_transcript(filename, language):
    try:
        with open(f'transcripts/{language}/{filename}', 'r', encoding='utf-8') as file:
            text = file.read().lower()
        return text
    except FileNotFoundError:
        raise

def mine_transcript():
    while True:
        filename, language = get_transcript_request()
        try:
            text = load_transcript(filename, language)
            break
        except FileNotFoundError:
            print('\nError, file not found, try again.')

        # loop to get a valid language choice from the user, including standardization of inputs, and option to quit to main menu

    while True:
        continue_choice = -1
        stop_words = []

        # try to open the stop words list for the language choice, if it fails, prompt user to continue or return to main menu

        try:
            stop_words = load_stop_words(language)
            break
        except FileNotFoundError:
            print(
                '\nWARNING: No Stop Words list was found in that language choice. Continue?')
            continue_choice = input(
                '"Y" = Continue, "N" = Main Menu, "R" = Re-try\n>> ').lower().strip()
            if continue_choice == 'n':
                break
            elif continue_choice == 'y':
                break

    # loop to get a valid response from the user regarding whether or not to use a Known Words filter, including option to quit to main menu

    while True:
        filter_list = input(
            '\nWould you like to use a "Known Words" filter? (y/n)\n>> ').lower().strip()
        if filter_list == 'y':

            # try to open the Known Words list for the language choice, if it fails, prompt user to continue without a Known Words list, try again, or return to main menu
            try:
                known_words = load_known_words(language)
                break
            except FileNotFoundError:
                print('\nError, File not found, try again.')
            
        elif filter_list == 'n':
            known_words = []
            break
        elif filter_list == 'quit':
            break
        else:
            print('Invalid input. Please respond with "y", "n", or "quit".')
        if filter_list == 'quit':
            continue

    # process the text to isolate words, count them, and print a filtered list of words with their counts
    results, counts = analyze_transcript(text, stop_words, known_words)

    print('\nVocabulary list (filtered):\n')

    for n, word, count, example_line in results:
        print(f'{n}: {word} - {count} | {example_line}')

    print(f'\nYou have identified {len(results)} study words out of {len(counts)} total words! ({len(results) / len(counts):.1%})')

def save_words_list(list_name, words_list, language):
    with open(f'filters/{list_name}/{list_name}_{language}.txt', 'w', encoding='utf-8') as f:
        for word in words_list:
            f.write(f'{word}\n')
    print(f'The list is now {len(words_list)} words long.')

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
        mine_transcript()
       
# allow for adding of words to a known words list, including input standardization and option to quit to main menu
    elif choice == 'add':
        add_known_words()

# all for adding words to stop words list from within the program
    elif choice == 'stop':
        add_stop_words()

# allow for exiting the program
    elif choice == 'exit':
        exit()

# handle invalid user input
    else:
        print('Invalid input.')
