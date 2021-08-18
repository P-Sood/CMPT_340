from librosa.core import audio
import pandas as pd

# audio_files_data = pd.read_pickle("extracted_features1.pkl")
# audio_files_data[["mfccs","chroma","mel","contrast","tonnetz","zero_crossing","centroids","energy"]] = pd.DataFrame(audio_files_data['to_drop'].tolist(), index=audio_files_data.index)
# audio_files_data.drop('to_drop',inplace=True, axis=1)



# print(audio_files_data.info())

folder_path = "/audio_and_txt_files"

x = folder_path[1:] + folder_path[0]
print(x)
