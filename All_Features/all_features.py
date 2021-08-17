# -*- coding: utf-8 -*-
"""All features.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1TWm-VEDyO8FZV-AOURUaj6iZ9dzH0zGd

# All features

This notebook will contain all the features that we will train our dataset on. These will be stored in a Pandas DataFrame called "df".
"""

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import pandas as pd 
import os
import matplotlib.pyplot as plt
import seaborn as sns
import librosa
import librosa.display
from os import listdir
from os.path import isfile, join
import scipy
import glob
from tqdm import tqdm
import wave
import random as rand
from librosa.effects import pitch_shift, time_stretch


path_to_audio_files = []

folder_path = "/audio_and_txt_files"
root = os.getcwd() + folder_path

for filename in glob.glob(os.path.join('audio_and_txt_files', '*.wav')):
    path_to_audio_files.append(filename)
audio_files_data = pd.DataFrame(path_to_audio_files, columns = ['audio_file'])

# Get all of the audio_files in one dataframe

audio_files_data

diagnosis_df = pd.read_csv('patient_diagnosis.csv', names=['Patient number', 'Diagnosis'])
diagnosis_df['Binary_diagnosis'] = diagnosis_df['Diagnosis'].apply(lambda x: 'Healthy' if x =='Healthy'  else 'Unhealthy')

df_demographic_info = pd.read_csv('demographic_info.txt', names = ['Patient number', 'Age', 'Sex' , 'Adult BMI (kg/m2)', 'Child Weight (kg)' , 'Child Height (cm)'], delimiter = ' ')
df =  df_demographic_info.join(diagnosis_df.set_index('Patient number'), on = 'Patient number', how = 'left')

df

filenames = [s.split('.')[0] for s in os.listdir(path = root) if '.txt' in s]

"""The above line goes through every .txt file in our directory. It gets the name of the file and splits it on the "." this way we get two parts [file_name,".wav"]. Thus by taking the [0] we are now taking the actual name of the file. 

I.E.

160_1b3_Lr_mc_AKGC417L.txt --> 160_1b3_Lr_mc_AKGC417L --> 



"""

def extract_annotation_data(file_name, root):
    
    tokens = file_name.split('_')
    
    recording_info = pd.DataFrame(data = [tokens + [file_name + ".wav"]], columns = ['Patient number', 'Recording index', 'Chest location','Acquisition mode','Recording equipment','audio_file'])
    
    recording_annotations = pd.read_csv(os.path.join(root, file_name + '.txt'), names = ['Start', 'End', 'Crackles', 'Wheezes'], delimiter= '\t')
    
    return (recording_info, recording_annotations)

"""This function splits the filename from the last part, since the filename contained useful information. Then we put it in a Pandas DataFrame for future use.

I.E.


160_1b3_Lr_mc_AKGC417L --> 




Patient ID;	Recording index;	Chest location;	Acquisition mode;	Recording equipment

160;	    1b3;	   Lr;	    mc;	     AKGC417L


"""

i_list = []
rec_annotations = []
rec_annotations_dict = {}

for s in filenames:
    
    (i,a) = extract_annotation_data(s, root)
    i_list.append(i)
    rec_annotations.append(a)
    rec_annotations_dict[s] = a
    
recording_info = pd.concat(i_list, axis = 0)
recording_info.head()

recording_info

recording_info["Patient number"] = pd.to_numeric(recording_info["Patient number"])

# df, recording_info

df = pd.merge(df,recording_info, on = "Patient number")

df
"""Now we have most of the statistical data about the patients all ready in the dataframe"""



"""The next function audio_features was the conjoining of code from Vaib, Jyotir, and Anuj"""

def audio_features(filename): 
    sound, sample_rate = librosa.load(filename)
    stft = np.abs(librosa.stft(sound))  
 
    mfccs = np.mean(librosa.feature.mfcc(y=sound, sr=sample_rate, n_mfcc=40),axis=1)
    chroma = np.mean(librosa.feature.chroma_stft(S=stft, sr=sample_rate),axis=1)
    mel = np.mean(librosa.feature.melspectrogram(sound, sr=sample_rate),axis=1)
    contrast = np.mean(librosa.feature.spectral_contrast(S=stft, sr=sample_rate),axis=1)
    tonnetz = np.mean(librosa.feature.tonnetz(y=librosa.effects.harmonic(sound), sr=sample_rate),axis=1)
    zero_crossing = sum(librosa.zero_crossings(sound, pad=False))
    centroids = librosa.feature.spectral_centroid(sound, sample_rate)[0].shape[0]
    energy = scipy.linalg.norm(sound) 
    return [mfccs,chroma,mel,contrast,tonnetz,zero_crossing,centroids,energy]

tqdm.pandas()

audio_files_data.to_pickle("extracted_features.pkl")


audio_files_data['to_drop'] = audio_files_data['audio_file'].progress_apply(lambda x: audio_features(x))

audio_files_data.to_pickle("extracted_features1.pkl")

audio_files_data = pd.read_pickle("extracted_features1.pkl")

audio_files_data[["mfccs","chroma","mel","contrast","tonnetz","zero_crossing","centroids","energy"]] = pd.DataFrame(audio_files_data['to_drop'].tolist(), index=audio_files_data.index)
audio_files_data.drop('to_drop',inplace=True, axis=1)

audio_files_data


df['audio_file'] = df['audio_file'].astype(str)
audio_files_data['audio_file'] = audio_files_data['audio_file'].astype(str)

df = pd.concat([df,audio_files_data],axis=1)


df


df.drop('audio_file',inplace=True, axis=1)

df

"""Now our dataframe df holds all the columns we are going to use in our data.

Afterwards we start doing data exploration to really know our data and understand what we have collected
"""

df.info()

df.isnull().sum()

"""Thus at this point we see we have many NaN values in our dataset. However we notice that BMI, weight, and height are all related through a mathamatical equation. So we have hope of finding ways to fill in these NaN values."""

df.to_pickle("Every_Feature.pkl")

"""

```
# This is formatted as code
```

# Removing data and filling in NaN's"""

df = pd.read_pickle('Every_Feature.pkl')

df

"""Using our weight and height columns lets calculate the missing BMI values"""

y_2 = df.assign(Calculated_BMI=lambda x:(x['Child Weight (kg)'] /  (x['Child Height (cm)']/100)**2))

y_2

y_2.info()

y_2.isnull().sum()

y_2['new BMI'] = y_2[['Adult BMI (kg/m2)', 'Calculated_BMI']].max(axis=1)

"""If you look at Rows 0,1,2 in the above dataframe you notice that BMI is NaN, but we have values for height and weight. Thus i take the max(NaN, calculated_BMI) to remove as many BMI NaN's as possible"""

y_2.isnull().sum()

y_2.info()

"""So now looking at our column new BMI, we see that 67 NaN out of 85 were correctly calculated

Thus we have 18 null values for BMI that wont be solved due to a lack of data
"""

to_drop = []
audio_files_data['audio_file']
count=0
for file_name in audio_files_data['audio_file']:
  with wave.open(file_name, "rb") as wave_file:
    frame_rate = wave_file.getframerate()
    if(frame_rate != 44100):
      to_drop.append(file_name)
for file_name in to_drop:
      audio_files_data = audio_files_data[audio_files_data.audio_file != file_name]


unique_vals = []


for i in audio_files_data['audio_file'].array:
  unique_vals.append(i[20:23])

unique_vals = list(unique_vals)


"""The code above was made by Anuj to remove all audio data that had a **sampling frequency** that was different then 44100


---


"""

rows_to_delete = [int(row) for row in unique_vals]

# print(rows_to_delete)


y_2 = y_2.drop(rows_to_delete, axis = 0)

y_2.info()

y_2.isnull().sum()

y_2['new BMI'] = y_2['new BMI'].fillna(0) # Filled every NaN value with 0, to use the max function in the next line

y_2.isnull().sum()

"""Did the fillna(0) after I removed the other rows, just in case I removed some rows already earlier from the sampling frequency"""

NaN_BMI = y_2['new BMI'] == 0

vals = []
for index, value in NaN_BMI.items():
    if value == True:
      vals.append(index)

pd.set_option("display.max_columns",None)

"""Now lets look at the data that is still NaN, and see if we can find a way to fill those in"""

# display(y_2.loc[vals])

remove = [908,             
909,            
910,              
911,             
912,         
913]

"""These rows had very little information and contained many NaN's"""

y_2 = y_2.drop(remove,axis=0)

y_2.info()

y_2.isna().sum()

y_2 = y_2.drop(columns=['Adult BMI (kg/m2)',"Child Weight (kg)","Child Height (cm)","Calculated_BMI"])

y_2.info()

"""Now we see that at the very end we have now come to 805 rows of data. IF you are wondering why we dropped so many rows in the previous few lines, it is because they were missing so many values that it was impossible to try and still use it without it being super noisy."""

changeBMI = [41,
 474,
 541,
 645,
 646,
 684,
 717,
 718,
 877,
 905,
 906,
 907]

"""On these rows I am going to find the average BMI of a child of a particular age of a particular sex"""

# display(y_2.loc[changeBMI])

"""(Age,Sex,Average_BMI)

(3,M,16)\
(1,M,17) I added in my own interpolation\
(14,F,19)\
(3,F,16)\
(16,F,20)\
(12,F,18)\
(60,M,20)


https://www.medicalnewstoday.com/articles/320917
https://www.cdc.gov/healthyweight/assessing/bmi/childrens_bmi/about_childrens_bmi.html


"""

Males = y_2['Sex'] == "M"
Females = y_2['Sex'] == "F"
Three_year_olds = y_2['Age'] == 3.0

Three_year_olds = y_2['Age'] == 3.0
M_3_YO = Males & Three_year_olds
F_3_YO = Females & Three_year_olds

Three_year_olds = y_2['Age'] == 3.0
M_3_YO = Males & Three_year_olds
F_3_YO = Females & Three_year_olds
All_Male_3 = y_2[M_3_YO] # selects the "True" rows recorded in the boolean index
All_Female_3 = y_2[F_3_YO] # selects the "True" rows recorded in the boolean index

All_Male_3

"""Seems like 16 is a good guess at the weights for Male 3, especially since there are multiple patients here that we can get information from and take an eduacated average/guess"""

All_Female_3

"""19 is good"""

fourteen_year_olds = y_2['Age'] == 14.0
F_14_YO = Females & fourteen_year_olds
All_Female_14 = y_2[F_14_YO] # selects the "True" rows recorded in the boolean index
All_Female_14

"""23 works here"""

sixteen_year_olds = y_2['Age'] == 16.0
F_16_YO = Females & sixteen_year_olds
All_Female_16 = y_2[F_16_YO] # selects the "True" rows recorded in the boolean index
All_Female_16

"""Should just remove these 2 data points as their is nothing to get


"""

twelve_year_olds = y_2['Age'] == 12.0
F_12_YO = Females & twelve_year_olds
All_Female_12 = y_2[F_12_YO] # selects the "True" rows recorded in the boolean index
All_Female_12

"""should just remove"""

sixty_year_olds = y_2['Age'] == 60.0
M_60_YO = Males & sixty_year_olds
All_Male_60 = y_2[M_60_YO] # selects the "True" rows recorded in the boolean index
All_Male_60

"""Just 1 other patient, so should remove this data as we can't calculate BMI properly

changeBMI = [41, \
 474,\
 541,\
 645,\
 646,\
 684,\
 717,\
 718,\
 877,\
 905,\
 906,\
 907]


**Above are the rows and below is the guessed BMI using my aformentioned resources**


newBMI = [ 16, \
 'idk' ,\
17, # His weight was 1.3 kg heavier but his size should still be same\
 23, \
 23,\
 19,\
remove,\
 remove,\
 remove,\
 remove,\
 remove,\
 remove]

After looking at each piece of data, it seems that making an educated guess would only harm the results as it would incorporate false realities. And wanting to take the average of other similar patients failed, since there were not enough similar individuals to make a good guess for every patient.

Thus each patient with a NaN BMI,weight, and height were just removed for accuracies sake, of being consistent with our true data.
"""

y_2 = y_2.drop(changeBMI,axis=0)

y_2.info()

y_2.isna().sum()

"""Now all of our data contains no NaN's and are all able to be used in our Machine Learning Models

We should reset the index to properly reflect how many rows we do have in our dataset
"""

y_2 = y_2.reset_index(drop=True)

y_2.to_pickle("Cleaned_Data.pkl")

y_2

"""# Need to concatenate all of our spectral feature arrays and put them all in one array"""

x_2 = pd.read_pickle("Cleaned_Data.pkl")

good_rows = []
for i in range(len(x_2)):
    good_rows.append(np.concatenate((x_2['mfccs'][i] , x_2['chroma'][i] , x_2['mel'][i] , x_2['contrast'][i] , x_2['tonnetz'][i])))

df =  pd.DataFrame({'info': good_rows})

df #

df = pd.DataFrame(df['info'].tolist(), index=df.index)
# audio_files_data.drop('to_drop',inplace=True, axis=1)

df

"""We see that we have made 193 columns, so what do each of these elements mean?"""

print(x_2['mfccs'][0].shape[0]) 
print(x_2['chroma'][0].shape[0]  )
print(x_2['mel'][0].shape[0] )
print(x_2['contrast'][0].shape[0])
print(x_2['tonnetz'][0].shape[0] )

x_2['mfccs'][0].shape[0] + x_2['chroma'][0].shape[0] + x_2['mel'][0].shape[0] + x_2['contrast'][0].shape[0] + x_2['tonnetz'][0].shape[0]

"""So now we see that the first 40 columns are mfccs, 12 for chroma, 128 for mel, 7 for contrast and 6 for tonnetz.

Now we know every single piece of data that we are feeding our model
"""

x_2 = x_2.drop(columns=['mfccs','chroma','mel','contrast','tonnetz'])

x_2

"""Now I want to move new BMI to be with the rest of the patient data to keep everything more organized"""

x_2 = x_2[["Patient number",	"Age",	"Sex",	"Diagnosis",	"Binary_diagnosis",	"Recording index", "Chest location",	"Acquisition mode",	"Recording equipment", "new BMI" ,	"zero_crossing",	"centroids",	"energy"]]
x_2

df = pd.concat([x_2, df], axis=1)

df

df.to_pickle("All_Features.pkl")

"""# Augment data slightly for new results"""

y_2 = pd.read_pickle("Cleaned_Data.pkl")

print(y_2.info())

y_2['Patient number'] = y_2["Patient number"].astype(str)

"""Given that we have already removed data rows, we need only certain wav files, so lets get back the wav files for all the data that we are going to be using"""

folder_path = folder_path[1:] + folder_path[0]

y_2 = y_2.assign(wav_file=lambda x: folder_path + x['Patient number'] + "_" + x['Recording index'] + "_" + x['Chest location'] + "_" + x['Acquisition mode'] + "_" + x['Recording equipment'] + ".wav")

y_2




"""Now given the audio files we create a function similar to the one earlier, except we use a random integer to apply some sort of shift to the audio. For future analysis"""

def audio_features_change_audio(filename): 
  
    sound, sample_rate = librosa.load(filename)
    stft = np.abs(librosa.stft(sound))  

    i = rand.randint(0,3)
    
    if i == 0:
      sound = time_stretch(sound, 2.0)
    elif i == 1:
      sound = pitch_shift(sound, sample_rate, 1)
    elif i == 2:
      sound = time_stretch(sound,  0.5)
    else:
      sound = pitch_shift(sound, sample_rate, -1)

 
    mfccs = np.mean(librosa.feature.mfcc(y=sound, sr=sample_rate, n_mfcc=40),axis=1)
    chroma = np.mean(librosa.feature.chroma_stft(S=stft, sr=sample_rate),axis=1)
    mel = np.mean(librosa.feature.melspectrogram(sound, sr=sample_rate),axis=1)
    contrast = np.mean(librosa.feature.spectral_contrast(S=stft, sr=sample_rate),axis=1)
    tonnetz = np.mean(librosa.feature.tonnetz(y=librosa.effects.harmonic(sound), sr=sample_rate),axis=1)
    zero_crossing = sum(librosa.zero_crossings(sound, pad=False))
    centroids = librosa.feature.spectral_centroid(sound, sample_rate)[0].shape[0]
    energy = scipy.linalg.norm(sound)

    concat = np.concatenate((mfccs,chroma,mel,contrast,tonnetz)) 

    return [zero_crossing,centroids,energy,concat,i]

dataframe_2_append = y_2[['wav_file']]

dataframe_2_append

tqdm.pandas()
z_2 = dataframe_2_append.progress_applymap(audio_features_change_audio)

"""Now we just do what we have done before and just go from lists to single elements and then from the concat list down to its single elements. So we are just flattening the "array"""

z_2

z_2.to_pickle("augmented_data_new.pkl")

z_2[["zero_crossing","centroids","energy","concat","rand int i"]] = pd.DataFrame(z_2['wav_file'].tolist(), index=z_2.index)

z_2.drop("wav_file",inplace=True,axis=1)
z_2

dataframe_2_append = y_2[[ 'Patient number',	'Age',	'Sex',	'Diagnosis',	'Binary_diagnosis',	'Recording index',	'Chest location',	'Acquisition mode',	'Recording equipment' , 'new BMI'	 ]]

a_2 = pd.concat([dataframe_2_append, z_2], axis=1)

a_2

concat = a_2[['concat']]
concat

concat = pd.DataFrame(concat['concat'].tolist(), index=a_2.index)

concat

b_2 = pd.concat([a_2, concat], axis=1)

b_2.drop(columns="concat",inplace=True,axis=1)

b_2

b_2.to_pickle("Augmented_Data_All_Features.pkl")

"""# Append Data

Now we can append this dataset onto df, to have twice the amount of data with different features for the value since they are augmented.

Now we will create a row of -1 for "rand int i" in our actual dataset to signify that those were unchanged values
"""

df = pd.read_pickle('All_Features.pkl')
b_2 = pd.read_pickle('Augmented_Data_All_Features.pkl')

df.insert(13, 'rand int i', -1)

df

b_2

df = df.append(b_2)
df = df.reset_index(drop=True)

df

"""Now we have all of our original and transformed data in one dataset"""

df.to_pickle("New_Data_Before_OHE.pkl")

"""# OHE

In this section we One Hot Encode all of our categorical variables. 

Need to OHE: 

*   Sex (Binary)

*   Chest Location

*   Acquisition Mode

*   Recording Equipment



"""

df = pd.read_pickle("New_Data_Before_OHE.pkl")

df = pd.get_dummies(data=df, columns=['Chest location','Acquisition mode','Recording equipment'])

df

df['Sex'] = (df['Sex'] == "M").astype(int)
df

"""Here, all of our data except for Diagnosis, Binary diagnosis, and Recording index have been One Hot Encoded."""

print("Number of Healthy Patients: ",(df['Binary_diagnosis'] == "Healthy").sum())
print("Number of Unhealthy Patients: ",(df['Binary_diagnosis'] == "Unhealthy").sum())

print("Number of Patients with Asthma are: ",(df['Diagnosis'] == "Asthma").sum())
print("Number of Patients with Bronchiectasis are: ",(df['Diagnosis'] == "Bronchiectasis").sum())
print("Number of Patients with Bronchiolitis are: ",(df['Diagnosis'] == "Bronchiolitis").sum())
print("Number of Patients with COPD are: ",(df['Diagnosis'] == "COPD").sum())
print("Number of Patients that are Healthy, are: ",(df['Diagnosis'] == "Healthy").sum())
print("Number of Patients with LRTI are: ",(df['Diagnosis'] == "LRTI").sum())
print("Number of Patients with Pneumonia are: ",(df['Diagnosis'] == "Pneumonia").sum())
print("Number of Patients with URTI are: ",(df['Diagnosis'] == "URTI").sum())


"""We realize that there are only 2 patients with Asthma and LRTI respectively, and thus it makes more sense to remove them"""

df = df[ df["Diagnosis"] != "Asthma"]
df = df[ df["Diagnosis"] != "LRTI"  ]
df.reset_index(inplace=True)

print(df.info())

df.to_pickle("Final_Data.pkl")

"""Now we have our dataset and we can begin to train our models and to understand our results in Models.ipynb """