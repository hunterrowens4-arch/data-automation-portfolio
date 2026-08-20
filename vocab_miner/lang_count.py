from collections import Counter
from pathlib import Path
import json
import random
import re
import shutil

def add_known_words():
    language = get_language()

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

def add_ignored_words():
    try:
        ignore_words = load_ignore_words()
    except FileNotFoundError:
        ignore_words = []

    add_words_str = input('\nWhat words would you like to add to the list? Separate the words only with spaces.\n>> ').lower().strip()
    add_words = [add_words_str.split()]
    ignore_words = extend_list(ignore_words, add_words)

    copy_ignored_list()
    save_ignored_list(ignore_words)

def analyze_transcript(text, stop_words, known_words, ignore_words):
    words = re.findall(r"\b\w+(?:'\w+)*\b", text, flags=re.UNICODE)
    lines = text.split("\n")
    counts = Counter(words)

    n = 0
    results = []

    for word, count in counts.most_common():
        if word.isdigit():
            continue
        elif word not in stop_words and word not in known_words and word not in ignore_words:

            example_line = ""
            for line in lines:
                if word in line:
                    example_line = line
                    break  # optional improvement

            n += 1
            results.append((n, word, count, example_line))

    return results, counts

def choose_media(media_paths, language):
    while True:
        print_subheader('SELECT MEDIA TYPE')
        print('')
        for number, file in enumerate(media_paths, start=1):
            print(f'    {number}:  {file.name.capitalize()}')
        user_media_choice = input(f'\n>> ').strip()
        try:
            choice = int(user_media_choice)
            if not 1<= choice <= len(media_paths):
                print(f'\nPlease select a listed type of media.')
                continue
        except ValueError:
            print(f'\nPlease print a valid number.')
            continue
        chosen_media = media_paths[choice - 1]
        print_subheader('CONFIRM')
        confirm_media = input(f'\n    Studying {chosen_media.name} in {language.capitalize()}.\n    Continue? (Y/N)\n\n>> ').lower().strip()
        if confirm_media == 'y':
            return chosen_media
        elif confirm_media == 'n':
            continue
        else:
            print_error('Invalid input. Please enter the number associated with your choice, followed by "Y" or "N" to confirm.')
            pause()

def choose_transcript(transcript_paths):
    while True:
        print_subheader('SELECT TRANSCRIPT')
        print(f'\n')
        for number, transcript in enumerate(transcript_paths, start=1):
            metadata = load_metadata(transcript)
            print(f'    {number}:  {metadata["artist"]} - {metadata["title"]}')
        user_transcript_choice = input(f'\nPlease enter the number of the transcript you would like to select.\nOr enter "R" for a random transcript.\n\n>> ').lower().strip()
        if user_transcript_choice == 'r':
            while True:
                chosen_transcript = random.choice(transcript_paths)
                metadata = load_metadata(chosen_transcript)

                if confirm_transcript == 'y':
                    return chosen_transcript
                elif confirm_transcript == 'n':
                    continue
                else:
                    print_error('Invalid input. Please enter the number associated with your choice, followed by "Y" or "N" to confirm.')
                    pause()
                    continue
        else:
            try:
                choice = int(user_transcript_choice)
                if not 1<= choice <= len(transcript_paths):
                    print_error('Please select a listed transcript.')
                    continue
                chosen_transcript = transcript_paths[choice - 1]
            except ValueError:
                print_error('Please enter a valid number.')
                continue

        metadata = load_metadata(chosen_transcript)
        confirm_transcript = input(f"""
    Studying: {metadata["title"]}
    Artist: {metadata["artist"]}

    Estimated difficulty: {metadata["difficulty"]}/10 ({metadata["difficulty_tier"]})
    Length: {metadata["total_word_count"]} words
    Vocabulary: {metadata["unique_word_count"]} words
        
    Continue? (Y/N)

>> """).lower().strip()
        if confirm_transcript == 'y':
            return chosen_transcript
        else:
            continue

def copy_ignored_list():
    try:
        shutil.copy(f'filters/ignore_words/ignore_words_global.txt',
                    f'filters/ignore_words/ignore_words_global_backup.txt')
        print(f'\nCreating a backup of your ignored words list.')
    except:
        print(f'Creating ignore_words_global.txt')

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

def generate_id(artist_name, transcript_title):
    artist_id = "".join(word.lower() for word in re.findall(
        r"\b\w+(?:'\w+)*\b",
        artist_name,
        flags=re.UNICODE
    ))
    title_id = "".join(word.lower() for word in re.findall(
        r"\b\w+(?:'\w+)*\b",
        transcript_title,
        flags=re.UNICODE
    ))
    transcript_id = f"{artist_id}_{title_id}"
    return transcript_id

def get_language():
    while True:
        print_subheader('SELECT LANGUAGE')
        language_choice = input(f"""
    1:  Spanish
    2:  Russian

>> """).strip()
        if language_choice in supported_languages:
            language_validated = supported_languages[language_choice]
            return language_validated
        else:
            print(f'Invalid response. Please enter the number associated with your choice.\n')
            continue
    
def get_media_type(language):
    while True:
        media_paths = list_media_type(language)
        if len(media_paths) == 0:
            print(f'\nError, folder not found, or no transcripts found in folder. Please try again.')
            continue
        else:
            chosen_media = choose_media(media_paths, language)
            return chosen_media    

def get_transcript_request():   
    while True:
        language = get_language()
        media_paths = list_media_type(language)
        chosen_media = get_media_type(language)
        transcript_paths = list_transcripts(language, chosen_media)
        if len(transcript_paths) == 0:
            print(f'\nError, folder not found, or no transcripts found in folder. Please try again.')
            continue
        else:
            chosen_transcript = choose_transcript(transcript_paths)
            return chosen_transcript, language

def import_transcript():
    language_import = get_language()

    media_options = {
        "1": "music",
        "2": "reading",
        "3": "video"
    }

    while True:
        print_subheader('IMPORT TRANSCRIPT')
        media_import = input(f"""
What type of media are you importing?

    1: Music
    2: Reading
    3: Video

>> """).strip()

        if media_import in media_options:
            media_import_validated = media_options[media_import]
            break

        print(f'\nError, please enter 1, 2, or 3.')

    title_import = input(f'\nWhat is the title of the transcript?\n\n>> ').lower().strip()
    artist_import = input(f'\nWhat is the name of the artist or creator?\n\n>> ').lower().strip()
    id_import = generate_id(artist_import, title_import)
    print(f'\nCopy and paste the transcript text below.')
    print(f'Type "---END---" on a line by itself when finished.\n')

    lines = []

    while True:
        line = input()
        if line == "---END---":
            break
        lines.append(line)

    text_import = "\n".join(lines)
    
    stop_words = []
    known_words = []
    ignore_words = []

    resutls, counts = analyze_transcript(text_import, stop_words, known_words, ignore_words)
    total_word_count_import = sum(counts.values())
    unique_word_count_import = len(counts)

    folder = (
        Path("transcripts")
        / language_import
        / media_import_validated
        / id_import
    )
    folder.mkdir(parents=True, exist_ok=False)

    transcript_file = folder / "transcript.txt"

    transcript_file.write_text(
        text_import,
        encoding="utf-8"
    )

    metadata = {
    "id": id_import,
    "artist": artist_import.title(),
    "title": title_import.title(),
    "language": language_import,
    "media_type": media_import_validated,
    "difficulty": None,
    "difficulty_tier": None,
    "total_word_count": total_word_count_import,
    "unique_word_count": unique_word_count_import
    }
    
    metadata_file = folder / "meta.json"

    print_subheader('CONFIRM')
    import_confirmation = input(f"""
    Import {metadata['title']}?
    
    By          : {metadata['artist']}
    Unique words: {metadata['unique_word_count']}
    Total words : {metadata['total_word_count']}

    Continue? (Y/N)

>> """).lower().strip()

    if import_confirmation == 'n':
        print('Cancelling import ...')
    elif import_confirmation =='y':
        with metadata_file.open("w", encoding="utf-8") as file:
            json.dump(
                metadata,
                file,
                indent=4,
                ensure_ascii=False
            )
        print(f'Imported {metadata['title']} by {metadata['artist']}.')

def list_media_type(language):
    folder = Path("transcripts") / language
    media_paths = list(folder.iterdir())
    media_paths.sort(key=lambda path: path.name)
    return media_paths

def list_transcripts(language, chosen_media):
    transcript_paths = list(chosen_media.iterdir())
    transcript_paths = [
        path for path in transcript_paths
        if path.is_dir()
    ]
    transcript_paths.sort(key=lambda path: path.name)
    return transcript_paths

def load_ignore_words():
    try:
        with open(f'filters/ignore_words/ignore_words_global.txt', 'r', encoding='utf-8') as f:
            ignore_words = [line.strip().lower()
                            for line in f if line.strip()]
        return ignore_words
    except FileNotFoundError:
        raise

def load_known_words(language):
    try:
        with open(f'filters/known_words/known_words_{language}.txt', 'r', encoding='utf-8') as f:
            known_words = [line.strip().lower()
                            for line in f if line.strip()]
        return known_words
    except FileNotFoundError:
        raise

def load_metadata(transcript):
    with open(transcript / 'meta.json', 'r', encoding="utf-8") as file:
        metadata = json.load(file)
    return metadata

def load_stop_words(language):
    try:
        with open(f'filters/stop_words/stop_words_{language}.txt', 'r', encoding='utf-8') as f:
            stop_words = [line.strip().lower()
                            for line in f if line.strip()]
        return stop_words
    except FileNotFoundError:
        raise

def load_transcript(filepath):
    try:
        with open(filepath / "transcript.txt", 'r', encoding='utf-8') as file:
            text = file.read().lower()
        return text
    except FileNotFoundError:
        raise

def mine_transcript():
    while True:
        chosen_transcript, language = get_transcript_request()
        try:
            text = load_transcript(chosen_transcript)
            break
        except FileNotFoundError:
            print('\nError, file not found, try again.')

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
            '\nWould you like to use a "Known Words" filter? (y/n)\n\n>> ').lower().strip()
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

    ignore_words = load_ignore_words()

    # process the text to isolate words, count them, and print a filtered list of words with their counts
    results, counts = analyze_transcript(text, stop_words, known_words, ignore_words)

    print('\nVocabulary list (filtered):\n')

    for n, word, count, example_line in results:
        print(f'{n}: {word} - {count} | {example_line}')

    print(f'\nYou have identified {len(results)} study words out of {len(counts)} total unique words! ({1 - (len(results) / len(counts)):.1%} known)')

def pause():
    input('\nPress ENTER to continue...')

def print_error(message):
    print(f'\n[ERROR] {message}')

def print_header(title, width=60):
    print('\n' + '=' * width)
    print(title.center(width))
    print('=' * width)

def print_subheader(title, width=60):
    print('\n' + '-' * width)
    print(title.center(width))
    print('-' * width)

def save_ignored_list(ignore_words):
    with open(f'filters/ignore_words/ignore_words_global.txt', 'w', encoding='utf-8') as f:
        for word in ignore_words:
            f.write(f'{word}\n')
    print(f'The list is now {len(ignore_words)} words long.')

def save_words_list(list_name, words_list, language):
    with open(f'filters/{list_name}/{list_name}_{language}.txt', 'w', encoding='utf-8') as f:
        for word in words_list:
            f.write(f'{word}\n')
    print(f'The list is now {len(words_list)} words long.')

menu_commands = {
    '1': ('Mine vocabulary', mine_transcript),
    '2': ('Add known words', add_known_words),
    '3': ('Add ignored words', add_ignored_words),
    '4': ('Import transcript', import_transcript),
    '5': ('Exit', exit)
}

supported_languages = {
    '1': 'spanish',
    '2': 'russian' 
}

# get user action choice
choice = None

while True:
    print_header('VOCAB MINER')
    print(f'\nWhat would you like to do?\n')
    for number, (label, function) in menu_commands.items():
        print(f'    {number}:  {label}')
    choice = input('\n>> ')

    if choice in menu_commands:
        menu_commands[choice][1]()

# for testing / debugging
# comment out when not in use
    elif choice == 'metadata_wordcount':
        stop_words = []
        known_words = []
        ignore_words = []
        chosen_transcript, language = get_transcript_request()
        try:
            text = load_transcript(chosen_transcript)
        except FileNotFoundError:
            print('\nError, file not found, try again.')
        results, counts = analyze_transcript(text, stop_words, known_words, ignore_words)
        print(f'\nTotal Words: {sum(counts.values())}')
        print(f'Unique Words: {len(counts)}')

# handle invalid user input
    else:
        print_error('Invalid input. Please enter the number associated with your choice.')
        pause()
