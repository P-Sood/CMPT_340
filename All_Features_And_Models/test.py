from librosa.core import audio
import pandas as pd

dataset = pd.read_pickle('Final_Data.pkl') 

df = dataset[ dataset["Diagnosis"] == "Asthma"]

print(df)