import zipfile
with zipfile.ZipFile('audio_and_txt_files.zip', 'r') as zip_ref:
    zip_ref.extractall('sound_files')