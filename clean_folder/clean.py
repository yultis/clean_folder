import sys
import re
import shutil
from pathlib import Path

JPEG = []
JPG = []
PNG = []
SVG = []
AVI = []
MP4 = []
MOV = []
MKV = []
DOC = []
DOCX = []
TXT = []
PDF = []
XLSX = []
PPTX = []
MP3 = []
OGG = []
WAV = []
AMR = []
my_other = []
archives = []

# Register of known extensions:
REGISTER_EXTENSION = {
    'JPEG': JPEG,
    'JPG': JPG,
    'PNG': PNG,
    'SVG': SVG,
    'AVI': AVI,
    'MP4': MP4,
    'MOV': MOV,
    'MKV': MKV,
    'DOC': DOC,
    'DOCX': DOCX,
    'TXT': TXT,
    'PDF': PDF,
    'XLSX': XLSX,
    'PPTX': PPTX,
    'MP3': MP3,
    'OGG': OGG,
    'WAV': WAV,
    'AMR': AMR,
    'ZIP': archives,
    'GZ': archives,
    'TAR': archives,
}

# Adding a variable where all folders will be stored:
FOLDERS = []
# Adding a variable where all known extensions will be stored:
EXTENSIONS = set()
# Adding a variable where all extensions that could not be identified will be stored:
UNKNOWN = set()


# A function that returns an extension from a file:
def get_extension(name: str) -> str:
    return Path(name).suffix[1:].upper()  # suffix[1:] -> .jpg -> JPG

# A function that receives a path as an input, and checks on this path whether it is a folder or a file:
def scan(folder: Path):
    for item in folder.iterdir():
        # Working with a folder
        if item.is_dir():  # check whether the object is a folder
            if item.name not in ('archives', 'video', 'audio', 'documents', 'images', 'my_other'):
                FOLDERS.append(item)
                scan(item)
            continue

        # Working with a file
        extension = get_extension(item.name)  # Taking the file extension
        full_name = folder / item.name  # taking the full path to the file
        if not extension:
            my_other.append(full_name)
        else:
            try:
                ext_reg = REGISTER_EXTENSION[extension]
                ext_reg.append(full_name)
                EXTENSIONS.add(extension)
            except KeyError:
                UNKNOWN.add(extension)  # .py, .psd, .cr2
                my_other.append(full_name)



CYRILLIC_SYMBOLS = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ'
TRANSLATION = ("a", "b", "v", "g", "d", "e", "jo", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "iu", "ia", "ie", "i", "ji", "g")

TRANS = dict()

for cyrillic, latin in zip(CYRILLIC_SYMBOLS, TRANSLATION):
    TRANS[ord(cyrillic)] = latin
    TRANS[ord(cyrillic.upper())] = latin.upper()


def normalize(name: str) -> str:
    translate_name = re.sub(r"\W\.\\", '_', name.translate(TRANS))
    return translate_name



# A function that processes folders and moves files by replacing ("normalizing") the name:
def handle_media(file_name: Path, target_folder: Path):
    target_folder.mkdir(exist_ok=True, parents=True)
    file_name.replace(target_folder / normalize(file_name.name))

# A function that unpacks archives, and then deletes the archives themselves:
def handle_archive(file_name: Path, target_folder: Path):
    target_folder.mkdir(exist_ok=True, parents=True)
    folder_for_file = target_folder / normalize(file_name.name.replace(file_name.suffix, ''))
    folder_for_file.mkdir(exist_ok=True, parents=True)
    
    try:
        shutil.unpack_archive(str(file_name.absolute()), str(folder_for_file.absolute()))
    except shutil.ReadError:
        folder_for_file.rmdir()
        return
    file_name.unlink()

    # Recursively process the unpacked content
    for item in folder_for_file.iterdir():
        if item.is_file() and item.suffix == '.zip':
            handle_archive(item, folder_for_file)


def main(folder: Path):
    scan(folder) # call the scan function from the file_parser,
    # iterate over each of the lists of all JPEG, JPG, PNG, SVG, AVI, etc. extensions 
    # and define the path where we put the files with the appropriate extensions 
    # by calling the handle_media function:
    for file in JPEG:
        handle_media(file, folder / 'images' / 'JPEG')
    for file in JPG:
        handle_media(file, folder / 'images' / 'JPG')
    for file in PNG:
        handle_media(file, folder / 'images' / 'PNG')
    for file in SVG:
        handle_media(file, folder / 'images' / 'SVG')
    for file in AVI:
        handle_media(file, folder / 'video' / 'AVI')
    for file in MP4:
        handle_media(file, folder / 'video' / 'MP4')
    for file in MOV:
        handle_media(file, folder / 'video' / 'MOV')
    for file in MKV:
        handle_media(file, folder / 'video' / 'MKV')
    for file in DOC:
        handle_media(file, folder / 'documents' / 'DOC')
    for file in DOCX:
        handle_media(file, folder / 'documents' / 'DOCX')
    for file in TXT:
        handle_media(file, folder / 'documents' / 'TXT')
    for file in PDF:
        handle_media(file, folder / 'documents' / 'PDF')
    for file in XLSX:
        handle_media(file, folder / 'documents' / 'XLSX')
    for file in PPTX:
        handle_media(file, folder / 'documents' / 'PPTX')
    for file in MP3:
        handle_media(file, folder / 'audio' / 'MP3')
    for file in OGG:
        handle_media(file, folder / 'audio' / 'OGG')
    for file in WAV:
        handle_media(file, folder / 'audio' / 'WAV')
    for file in AMR:
        handle_media(file, folder / 'audio' / 'AMR')

    for file in my_other:
        handle_media(file, folder / 'my_other')

    for file in archives:
        handle_archive(file, folder / 'archives')

    for folder in FOLDERS[::-1]:
        # Delete empty folders after sorting
        try:
            folder.rmdir()
        except OSError:
            print(f'Error during remove folder {folder}')



def start():
    if sys.argv[1]:
        folder_process = Path(sys.argv[1])
        main(folder_process)
