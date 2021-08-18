# -*- coding: utf-8 -*-
"""K-Means.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1tcPin-yiV_CroDHCINhqmVSepBUmQiUR

# Importing libraries and pre-processed data
"""

import numpy as np
import pandas as pd 
import os
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, Conv2D, MaxPooling2D, MaxPooling1D, Dense, Flatten, Dropout, SeparableConv1D
import matplotlib.pyplot as plt
import pickle as pkl
import seaborn as sns
import librosa
import librosa.display
from sklearn.model_selection import train_test_split,cross_val_score
from sklearn.metrics import mean_squared_error,r2_score, completeness_score, accuracy_score
from sklearn.metrics.cluster import contingency_matrix
from sklearn.preprocessing import StandardScaler
from os import listdir
from os.path import isfile, join
from tensorflow.keras.utils import plot_model,to_categorical
from google.colab import drive
import scipy
import glob
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

# Commented out IPython magic to ensure Python compatibility.
drive.mount('/content/gdrive', force_remount=True)
# %cd gdrive/MyDrive/'CMPT 340 Project'/audio_and_txt_files

dataset = pd.read_pickle('Final_Data.pkl') 

dataset_non_Augmented = dataset[dataset['rand int i'] == -1]
dataset_Augmented = dataset[dataset['rand int i'] != -1]
dataset_Augmented.reset_index(inplace=True)

dataset = dataset[ dataset["Diagnosis"] != "Asthma"]
dataset = dataset[ dataset["Diagnosis"] != "LRTI"  ]
dataset.reset_index(inplace=True)

dataset_non_Augmented = dataset_non_Augmented[dataset_non_Augmented["Diagnosis"] != "Asthma"]
dataset_non_Augmented = dataset_non_Augmented[dataset_non_Augmented["Diagnosis"] != "LRTI"]
dataset_non_Augmented.reset_index(inplace=True)

dataset_Augmented = dataset_Augmented[dataset_Augmented["Diagnosis"] != "Asthma"]
dataset_Augmented = dataset_Augmented[dataset_Augmented["Diagnosis"] != "LRTI"]
dataset_Augmented.reset_index(inplace=True)

"""Now we have the joined dataset as well as the split versions to properly organize our models testing and training"""

dataset_sequential = dataset.copy() 
dataset

plt.figure(figsize = (33,33))
sns.heatmap(dataset.corr().round(1), annot = True)

dataset["Diagnosis"] = dataset["Diagnosis"].astype('category')
dataset["Diagnosis"] = dataset["Diagnosis"].cat.codes
dataset['Binary_diagnosis'] = (dataset['Binary_diagnosis'] == "Healthy").astype(int)

dataset_non_Augmented["Diagnosis"] = dataset_non_Augmented["Diagnosis"].astype('category')
dataset_non_Augmented["Diagnosis"] = dataset_non_Augmented["Diagnosis"].cat.codes
dataset_non_Augmented['Binary_diagnosis'] = (dataset_non_Augmented['Binary_diagnosis'] == "Healthy").astype(int)

dataset_Augmented["Diagnosis"] = dataset_Augmented["Diagnosis"].astype('category')
dataset_Augmented["Diagnosis"] = dataset_Augmented["Diagnosis"].cat.codes
dataset_Augmented['Binary_diagnosis'] = (dataset_Augmented['Binary_diagnosis'] == "Healthy").astype(int)

correlation_heatmap = dataset[['Patient number', 'Sex' ,	'Age'	,'Diagnosis',	'Binary_diagnosis',	'zero_crossing',	'centroids',	'energy',	'new BMI']]
plt.figure(figsize = (33,33))
sns.heatmap(correlation_heatmap.corr().round(1), annot = True)

print("Number of Healthy Patients: ",(dataset['Binary_diagnosis'] == 1).sum())
print("Number of Unhealthy Patients: ",(dataset['Binary_diagnosis'] == 0).sum())
print("\n")
#print("Number of Patients with Asthma are: ",(dataset['Diagnosis'] == 0).sum())
print("Number of Patients with Bronchiectasis are: ",(dataset['Diagnosis'] == 0).sum())
print("Number of Patients with Bronchiolitis are: ",(dataset['Diagnosis'] == 1).sum())
print("Number of Patients with COPD are: ",(dataset['Diagnosis'] == 2).sum())
print("Number of Patients that are Healthy, are: ",(dataset['Diagnosis'] == 3).sum())
#print("Number of Patients with LRTI are: ",(dataset['Diagnosis'] == 5).sum())
print("Number of Patients with Pneumonia are: ",(dataset['Diagnosis'] == 4).sum())
print("Number of Patients with URTI are: ",(dataset['Diagnosis'] == 5).sum())

"""## Multi Classification of Whole Dataset"""

features = dataset.drop(columns = ['Diagnosis','Binary_diagnosis','Patient number','Recording index',"rand int i"])

targets = dataset[['Diagnosis']]

X_train, X_test, y_train, y_test=train_test_split(features, targets, test_size=0.2) # rand state sets a seed so that it will be the same

X_train_whole_dataset = X_train.values
X_test_whole_dataset = X_test.values

y_train_multi_whole_dataset = y_train.values.reshape(-1,)
y_test_multi_whole_dataset = y_test.values.reshape(-1,)

"""## Binary Classification of Whole Dataset"""

# targets = dataset[['Binary_diagnosis']]

# y = targets.values.reshape(-1,)

y_train_binary_whole_dataset = (y_train["Diagnosis"] == 4).astype(int).values.reshape(-1,)
y_test_binary_whole_dataset = (y_test["Diagnosis"] == 4).astype(int).values.reshape(-1,)

"""## Multi Classification of Augmented Dataset"""

features = dataset_Augmented.drop(columns = ['Diagnosis','Binary_diagnosis','Patient number','Recording index',"rand int i"])
targets = dataset_Augmented[['Diagnosis']]
print(dataset_Augmented)
X_train, X_test, y_train, y_test=train_test_split(features, targets, test_size=0.2) # rand state sets a seed so that it will be the same

X_train_augmented_dataset = X_train.values
X_test_augmented_dataset = X_test.values

y_train_multi = y_train.values.reshape(-1,)
y_test_multi = y_test.values.reshape(-1,)

y_test_multi

"""## Binary Classification of Augmented Dataset

"""

y_train_binary = (y_train["Diagnosis"] == 4).astype(int).values.reshape(-1,)
y_test_binary = (y_test["Diagnosis"] == 4).astype(int).values.reshape(-1,)

"""Training on the augmented dataset will be interesting, especially in relation to non-augmented

We want to use the same data rows, so all we do is change the X_trains to be from the non augmented dataset, now the binary and multi classification values will stay the same
"""

X_train_non = dataset_non_Augmented.loc[X_train.index].drop(columns = ['Diagnosis','Binary_diagnosis','Patient number','Recording index',"rand int i"])
X_test_non = dataset_non_Augmented.loc[X_test.index].drop(columns = ['Diagnosis','Binary_diagnosis','Patient number','Recording index',"rand int i"])

X_train_non_augmented_dataset =  X_train_non.values
X_test_non_augmented_dataset = X_test_non.values

"""Training on the augmented dataset will be interesting, especially in relation to non-augmented

# Agglomerate Clustering

First we will work on all of the data both augmented and non augmented
"""

from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import homogeneity_score

Agg_Cluster = AgglomerativeClustering()

Agg_Cluster.fit(X_train)

y_train_predict = Agg_Cluster.fit_predict(X_train)

y_test_predict = Agg_Cluster.fit_predict(X_test)

confusion_matrix_train = contingency_matrix(y_train,y_train_predict)
confusion_matrix_test = contingency_matrix(y_test,y_test_predict)

confusion = [confusion_matrix_train,confusion_matrix_test]
title = ["confusion_matrix_train","confusion_matrix_test"]
for x in confusion:
  print(x)

"""We see that our contingency matrix is just a confusion matrix, without the labels so lets make it look nice, however before we do that we also notice that their predicted cluster put everything on 1, but in actuality that clustering label is unhealthy, and is defined as 0 in our dataset"""

y_train_predict[:] = [abs(x - 1) for x in y_train_predict]
y_test_predict[:] = [abs(x - 1) for x in y_test_predict]

confusion_matrix_train = contingency_matrix(y_train,y_train_predict)
confusion_matrix_test = contingency_matrix(y_test,y_test_predict)

confusion = [confusion_matrix_train,confusion_matrix_test]
title = ["confusion_matrix_train","confusion_matrix_test"]
for x in confusion:
  print(x)

"""Notice now that the data is in their correct spots according to the way we have defined it"""

for i in range(2):
  fig, ax = plt.subplots(figsize=(10,10))
  sns.heatmap(confusion[i], annot=True)
  plt.xlabel('Predicted')
  plt.ylabel('Actual')
  plt.title(title[i])
  plt.show()

print("**Training Score:** {}\\".format(accuracy_score(y_train,y_train_predict)))
print("**Test Score:** {}\\".format(accuracy_score(y_test,y_test_predict)))

print("**Training Score:** {}\\".format(homogeneity_score(y_train,y_train_predict)))
print("**Test Score:** {}\\".format(homogeneity_score(y_test,y_test_predict)))

"""### Now lets change Targets to be all of the diagnosis and see if there is any difference"""

Agg_Cluster = AgglomerativeClustering(n_clusters=8)

Agg_Cluster.fit(X_train)

y_train_predict = Agg_Cluster.fit_predict(X_train)

y_test_predict = Agg_Cluster.fit_predict(X_test)

confusion_matrix_train = contingency_matrix(y_train,y_train_predict)
confusion_matrix_test = contingency_matrix(y_test,y_test_predict)

confusion = [confusion_matrix_train,confusion_matrix_test]
title = ["confusion_matrix_train","confusion_matrix_test"]

confusion_matrix_test

for i in range(2):
  fig, ax = plt.subplots(figsize=(10,10))
  sns.heatmap(confusion[i], annot=True)
  plt.xlabel('Predicted')
  plt.ylabel('Actual')
  plt.title(title[i])
  plt.show()

print("**Training Score:** {}\\".format(homogeneity_score(y_train,y_train_predict)))
print("**Validation Score:** {}\\".format(homogeneity_score(y_val,y_valid_predict)))
print("**Test Score:** {}\\".format(homogeneity_score(y_test,y_test_predict)))

"""## Binary Classification:

**Training Score:** 0.001812854636527089\
**Validation Score:** 0.01021899390226609\
**Test Score:** 0.010783291182002285

## Multi Classification:

**Training Score:** 0.19128155848883716\
**Validation Score:** 0.24404191663198627\
**Test Score:** 0.341059022281443

We can see that our Multi Classification worked overall much better then our Binary.\
Why is this the case?

Let's investigate.
"""

print("Number of Healthy Patients: ",(dataset['Binary_diagnosis'] == 1).sum())
print("Number of Unhealthy Patients: ",(dataset['Binary_diagnosis'] == 0).sum())

print("Number of Patients with Asthma are: ",(dataset['Diagnosis'] == 0).sum())
print("Number of Patients with Bronchiectasis are: ",(dataset['Diagnosis'] == 1).sum())
print("Number of Patients with Bronchiolitis are: ",(dataset['Diagnosis'] == 2).sum())
print("Number of Patients with COPD are: ",(dataset['Diagnosis'] == 3).sum())
print("Number of Patients with Healthy are: ",(dataset['Diagnosis'] == 4).sum())
print("Number of Patients with LRTI are: ",(dataset['Diagnosis'] == 5).sum())
print("Number of Patients with Pneumonia are: ",(dataset['Diagnosis'] == 6).sum())
print("Number of Patients with URTI are: ",(dataset['Diagnosis'] == 7).sum())

"""As we can see here, we have a huge data imbalance when we choose Binary with 765 sick. This is because Agglomertaive clustering is unsupervised in nature and thus it is trying to look and identify patterns within the data to then cluster together.Thus the model will believe that everybody will be sick. However even with 694 COPD, (which just gives us a difference of 69) it makes a world of difference. Given that 6 more labels are used for those 69 extra patients."""

from sklearn.linear_model import LinearRegression

# Initialize the linear regression model
linear_regressor = LinearRegression()

# Train the model on the training data
linear_regressor.fit(X_train, y_train)

y_predict = linear_regressor.predict(X_test)

cross_val_scores = cross_val_score(linear_regressor, X , y)

print("**Training Score:** {}\\".format(linear_regressor.score(X_train, y_train)))
print("**Validation Score:** {}\\".format(linear_regressor.score(X_val, y_val)))
print("**Test Score:** {}\\".format(linear_regressor.score(X_test, y_test)))
print("**Mean Squared Error:** {}\\".format(mean_squared_error(y_test, y_predict)))
print("**R2:** {}\\".format(r2_score(y_test, y_predict)))
print("**Accuracy:** {}\\".format(cross_val_scores.mean()))
print("**Standard Deviation:** {}".format(cross_val_scores.std()))

"""**Training Score:** 0.7313958532228526\
**Validation Score:** -751.0012538581755\
**Test Score:** -160032810042718.44\
**Mean Squared Error:** 5198438854576.015\
**R2:** -160032810042718.44\
**Accuracy:** -2922762041999611.0\
**Standard Deviation:** 5845524083855530.0

**Training Score:** 0.5471429949855255\
**Validation Score:** -1631.2089520180195\
**Test Score:** -75.63409963566522\
**Mean Squared Error:** 92.23616090004434\
**R2:** -75.63409963566522\
**Accuracy:** -1.3532494069768252e+16\
**Standard Deviation:** 2.7064988139203736e+16
"""

from sklearn.svm import SVC

svr_regressor = SVC()

svr_regressor.fit(X_train, y_train)

y_predict = svr_regressor.predict(X_test)

cross_val_scores = cross_val_score(svr_regressor, X , y)
print("**Training Score:** {}\\".format(svr_regressor.score(X_train, y_train)))
print("**Validation Score:** {}\\".format(svr_regressor.score(X_val, y_val)))
print("**Test Score:** {}\\".format(svr_regressor.score(X_test, y_test)))
print("**Mean Squared Error:** {}\\".format(mean_squared_error(y_test, y_predict)))
print("**R2:** {}\\".format(r2_score(y_test, y_predict)))
print("**Accuracy:** {}\\".format(cross_val_scores.mean()))
print("**Standard Deviation:** {}".format(cross_val_scores.std()))

"""**Training Score:** 0.9664948453608248\
**Validation Score:** 0.9580838323353293\
**Test Score:** 0.9663865546218487\
**Mean Squared Error:** 0.03361344537815126\
**R2:** -0.034782608695652195\
**Accuracy:** 0.9647002627179365\
**Standard Deviation:** 0.0029836154020048485

**Training Score:** 0.8856015779092702\
**Validation Score:** 0.889763779527559\
**Test Score:** 0.8301886792452831\
**Mean Squared Error:** 1.2767295597484276\
**R2:** -0.06076639936900241\
**Accuracy:** 0.8751691744287877\
**Standard Deviation:** 0.004386802923024295

# Sequential Modelling

collecting required data
"""

dataset_sequential.columns = dataset_sequential.columns.map(str)

start = dataset_sequential.columns.get_loc("0") 
end = dataset_sequential.columns.get_loc("192")

data = dataset_sequential.iloc[:, start: end]

patient_diagnosis = dataset_sequential.iloc[:, dataset_sequential.columns.get_loc("Diagnosis")]

"""refining and spliting data"""

def data_points():
    labels = []
    images = []

    to_hot_one = {"COPD":0, "Healthy":1, "URTI":2, "Bronchiectasis":3, "Pneumonia":4, "Bronchiolitis":5, "Asthma":6, "LRTI":7}

    #count = 0
    for i in range (0, 793):
      labels.append(to_hot_one[patient_diagnosis[i]])
      images.append(np.array(data.iloc[i, :]))

    return np.array(labels), np.array(images)

def preprocessing(labels, images):    

  # Remove Asthma and LRTI
    images = np.delete(images, np.where((labels == 7) | (labels == 6))[0], axis=0) 
    labels = np.delete(labels, np.where((labels == 7) | (labels == 6))[0], axis=0)      
    
  # Split data
    X_train, X_test, y_train, y_test = train_test_split(images, labels, test_size=0.2, random_state=10)

  # Hot one encode the labels
    y_train = to_categorical(y_train)
    y_test = to_categorical(y_test)  

  # Format new data
    y_train = np.reshape(y_train, (y_train.shape[0], 6))
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
    y_test = np.reshape(y_test, (y_test.shape[0], 6))
    X_test = np.reshape(X_test, (X_test.shape[0], X_train.shape[1],  1))

    return X_train, X_test, y_train, y_test

labels, images = data_points()

X_train, X_test, y_train, y_test = preprocessing(labels, images)

"""sequential model implimentation and training"""

model = Sequential()
model.add(Conv1D(64, kernel_size=5, activation='relu', input_shape=(193, 1)))

model.add(Conv1D(128, kernel_size=5, activation='relu'))
model.add(MaxPooling1D(2)) 

model.add(SeparableConv1D(256, kernel_size=5, activation='relu'))
model.add(MaxPooling1D(2)) 

model.add(SeparableConv1D(256, kernel_size=5, activation='relu'))
model.add(MaxPooling1D(2)) 

model.add(Dropout(0.5))
model.add(Flatten())

model.add(Dense(512, activation='relu'))   
model.add(Dense(6, activation='softmax'))

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
history = model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=70, batch_size=200, verbose=1)

"""visualizing the results"""

def visualize_training(history, lw = 3):
    plt.figure(figsize=(10,6))
    plt.plot(history.history['accuracy'], label = 'training', marker = '*', linewidth = lw)
    plt.plot(history.history['val_accuracy'], label = 'validation', marker = 'o', linewidth = lw)
    plt.title('Training Accuracy vs Validation Accuracy')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.legend(fontsize = 'x-large')
    plt.show()

    plt.figure(figsize=(10,6))
    plt.plot(history.history['loss'], label = 'training', marker = '*', linewidth = lw)
    plt.plot(history.history['val_loss'], label = 'validation', marker = 'o', linewidth = lw)
    plt.title('Training Loss vs Validation Loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend(fontsize = 'x-large')
    plt.show()
visualize_training(history)

from sklearn.metrics import roc_auc_score, classification_report, confusion_matrix
matrix_index = ["COPD", "Healthy", "URTI", "Bronchiectasis", "Pneumoina", "Bronchiolitis"]

preds = model.predict(X_test)
classpreds = np.argmax(preds, axis=1) # predicted classes 
y_testclass = np.argmax(y_test, axis=1) # true classes

cm = confusion_matrix(y_testclass, classpreds)
print(classification_report(y_testclass, classpreds, target_names=matrix_index))

# Get percentage value for each element of the matrix
cm_sum = np.sum(cm, axis=1, keepdims=True)
cm_perc = cm / cm_sum.astype(float) * 100
annot = np.empty_like(cm).astype(str)
nrows, ncols = cm.shape
for i in range(nrows):
    for j in range(ncols):
        c = cm[i, j]
        p = cm_perc[i, j]
        if i == j:
            s = cm_sum[i]
            annot[i, j] = '%.1f%%\n%d/%d' % (p, c, s)
        elif c == 0:
            annot[i, j] = ''
        else:
            annot[i, j] = '%.1f%%\n%d' % (p, c)


# Display confusion matrix 
df_cm = pd.DataFrame(cm, index = matrix_index, columns = matrix_index)
df_cm.index.name = 'Actual'
df_cm.columns.name = 'Predicted'
fig, ax = plt.subplots(figsize=(10,7))
sns.heatmap(df_cm, annot=annot, fmt='')

"""evaluating model's efficiency"""

model.evaluate(X_test, y_test)

"""#K-Means Model"""

from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

"""### Binary Diagnosis - Whole Data"""

pca = PCA(2)

X_pca_train = pca.fit_transform(X_train_whole_dataset)
X_pca_test = pca.fit_transform(X_test_whole_dataset)
k_means_model = KMeans(n_clusters = 2) 
k_means_model.fit(X_pca_train)

y_train_predict = k_means_model.predict(X_pca_train)
y_test_predict = k_means_model.predict(X_pca_test)

# Commented out IPython magic to ensure Python compatibility.
!pwd
# %cd ../report_figures/

plt.scatter(X_pca_train[:, 0] , X_pca_train[: , 1])
plt.savefig('whole_data.png')

u_labels = np.unique(y_train_predict)
centroids = k_means_model.cluster_centers_

for i in u_labels:
    plt.scatter(X_pca_train[y_train_predict == i , 0] , X_pca_train[y_train_predict == i , 1] , label = i)
plt.scatter(centroids[:,0] , centroids[:,1] , s = 40, color = 'k')
plt.savefig('KMeans_binary_whole_data.png')
plt.legend()
plt.show()

"""Clearly we can see from this that 0 must be our unhealthy and 1 must be healthy.  This is easy to re-label """

confusion_matrix_train = contingency_matrix(y_train_binary_whole_dataset,y_train_predict)
confusion_matrix_test = contingency_matrix(y_test_binary_whole_dataset,y_test_predict)

confusion = [confusion_matrix_train,confusion_matrix_test]
title = ["confusion_matrix_train","confusion_matrix_test"]
for x in confusion:
  print(x)

for i in range(2):
  fig, ax = plt.subplots(figsize=(10,10))
  sns.heatmap(confusion[i], annot=True)
  plt.xlabel('Predicted')
  plt.ylabel('Actual')
  plt.title(title[i])
  plt.show()

print("**Training Score:** {}\\".format(accuracy_score(y_train_binary_whole_dataset,y_train_predict)))
print("**Test Score:** {}\\".format(accuracy_score(y_test_binary_whole_dataset,y_test_predict)))

"""### Multi Diagnosis - Whole Data"""

k_means_model = KMeans(n_clusters=6)

k_means_model.fit(X_pca_train)

y_train_predict = k_means_model.predict(X_pca_train)
y_test_predict = k_means_model.predict(X_pca_test)

u_labels = np.unique(y_train_predict)
centroids = k_means_model.cluster_centers_

for i in u_labels:
    plt.scatter(X_pca_train[y_train_predict == i , 0] , X_pca_train[y_train_predict == i , 1] , label = i)
 
plt.scatter(centroids[:,0] , centroids[:,1] , s = 40, color = 'k')
plt.savefig('KMeans_multi_whole_data.png')

plt.legend()
plt.show()

"""Which cluster is healthy?  Which is unhealthy?  This becomes a challenge"""

confusion_matrix_train = contingency_matrix(y_train_multi_whole_dataset,y_train_predict)
confusion_matrix_test = contingency_matrix(y_test_multi_whole_dataset,y_test_predict)

confusion = [confusion_matrix_train,confusion_matrix_test]
title = ["confusion_matrix_train","confusion_matrix_test"]

for i in range(2):
  fig, ax = plt.subplots(figsize=(10,10))
  sns.heatmap(confusion[i], annot=True)
  plt.xlabel('Predicted')
  plt.ylabel('Actual')
  plt.title(title[i])
  plt.show()

print("**Training Score:** {}\\".format(accuracy_score(y_train_multi_whole_dataset,y_train_predict)))
print("**Test Score:** {}\\".format(accuracy_score(y_test_multi_whole_dataset,y_test_predict)))

"""### Binary Diagnosis - Non Augmented"""

X_pca_train_non_augmented = pca.fit_transform(X_train_non_augmented_dataset)
X_pca_test_non_augmented = pca.fit_transform(X_test_non_augmented_dataset)

k_means_model = KMeans(n_clusters=2)

k_means_model.fit(X_pca_train_non_augmented)

y_train_predict = k_means_model.predict(X_pca_train_non_augmented)

y_test_predict = k_means_model.predict(X_pca_test_non_augmented)

plt.scatter(X_pca_train_non_augmented[: , 0] , X_pca_train_non_augmented[: , 1])
 plt.savefig('non_augmented.png')

u_labels = np.unique(y_train_predict)
centroids = k_means_model.cluster_centers_

for i in u_labels:
    plt.scatter(X_pca_train_non_augmented[y_train_predict == i , 0] , X_pca_train_non_augmented[y_train_predict == i , 1] , label = i)
plt.scatter(centroids[:,0] , centroids[:,1] , s = 40, color = 'k')
plt.savefig('KMeans_binary_non_augmented_data.png')
plt.legend()
plt.show()

confusion_matrix_train = contingency_matrix(y_train_binary,y_train_predict)
confusion_matrix_test = contingency_matrix(y_test_binary,y_test_predict)

confusion = [confusion_matrix_train,confusion_matrix_test]
title = ["confusion_matrix_train_non_augment","confusion_matrix_test_non_augment"]
for x in confusion:
  print(x)

"""We see that our contingency matrix is just a confusion matrix, without the labels so lets make it look nice, however before we do that we also notice that their predicted cluster put everything on 1, but in actuality that clustering label is unhealthy, and is defined as 0 in our dataset"""

for i in range(2):
  fig, ax = plt.subplots(figsize=(10,10))
  sns.heatmap(confusion[i], annot=True)
  plt.xlabel('Predicted')
  plt.ylabel('Actual')
  plt.title(title[i])
  plt.show()

print("**Training Score:** {}\\".format(accuracy_score(y_train_binary,y_train_predict)))
print("**Test Score:** {}\\".format(accuracy_score(y_test_binary,y_test_predict)))

"""### Multi Diagnosis - Non Augmented"""

k_means_model = KMeans(n_clusters=6)

k_means_model.fit(X_pca_train_non_augmented)

y_train_predict = k_means_model.predict(X_pca_train_non_augmented)
y_test_predict = k_means_model.predict(X_pca_test_non_augmented)

u_labels = np.unique(y_train_predict)
centroids = k_means_model.cluster_centers_

for i in u_labels:
    plt.scatter(X_pca_train_non_augmented[y_train_predict == i , 0] , X_pca_train_non_augmented[y_train_predict == i , 1] , label = i)

plt.scatter(centroids[:,0] , centroids[:,1] , s = 40, color = 'k')
plt.savefig('KMeans_multi_non_augmented_data.png')


plt.legend()
plt.show()

confusion_matrix_train = contingency_matrix(y_train_multi,y_train_predict)
confusion_matrix_test = contingency_matrix(y_test_multi,y_test_predict)

confusion = [confusion_matrix_train,confusion_matrix_test]
title = ["confusion_matrix_train","confusion_matrix_test"]

for i in range(2):
  fig, ax = plt.subplots(figsize=(10,10))
  sns.heatmap(confusion[i], annot=True)
  plt.xlabel('Predicted')
  plt.ylabel('Actual')
  plt.title(title[i])
  plt.show()

print("**Training Score:** {}\\".format(accuracy_score(y_train_multi,y_train_predict)))
print("**Test Score:** {}\\".format(accuracy_score(y_test_multi,y_test_predict)))

"""### Binary Diagnosis - Augmented"""

X_pca_train_augmented = pca.fit_transform(X_train_augmented_dataset)
X_pca_test_augmented = pca.fit_transform(X_test_augmented_dataset)

k_means_model = KMeans(n_clusters=2)

k_means_model.fit(X_pca_train_augmented)

y_train_predict = k_means_model.predict(X_pca_train_augmented)

y_test_predict = k_means_model.predict(X_pca_test_augmented)

confusion_matrix_train = contingency_matrix(y_train_binary,y_train_predict)
confusion_matrix_test = contingency_matrix(y_test_binary,y_test_predict)

confusion = [confusion_matrix_train,confusion_matrix_test]
title = ["confusion_matrix_train_non_augment","confusion_matrix_test_non_augment"]
for x in confusion:
  print(x)

u_labels = np.unique(y_train_predict)
centroids = k_means_model.cluster_centers_

for i in u_labels:
    plt.scatter(X_pca_train_augmented[y_train_predict == i , 0] , X_pca_train_augmented[y_train_predict == i , 1] , label = i)
 
plt.scatter(centroids[:,0] , centroids[:,1] , s = 40, color = 'k')
plt.savefig('KMeans_binary_augmented_data.png')


plt.legend()
plt.show()

for i in range(2):
  fig, ax = plt.subplots(figsize=(10,10))
  sns.heatmap(confusion[i], annot=True)
  plt.xlabel('Predicted')
  plt.ylabel('Actual')
  plt.title(title[i])
  plt.show()

print("**Training Score:** {}\\".format(accuracy_score(y_train_binary,y_train_predict)))
print("**Test Score:** {}\\".format(accuracy_score(y_test_binary,y_test_predict)))

"""### Multi Diagnosis - Augmented"""

k_means_model = KMeans(n_clusters=6)

k_means_model.fit(X_pca_train_augmented)

y_train_predict = k_means_model.predict(X_pca_train_augmented)
y_test_predict = k_means_model.predict(X_pca_test_augmented)

plt.scatter(X_pca_train_augmented[:,0], X_pca_train_augmented[: , 1])
plt.savefig('augmented_data.png')

u_labels = np.unique(y_train_predict)
centroids = k_means_model.cluster_centers_

for i in u_labels:
    plt.scatter(X_pca_train_augmented[y_train_predict == i , 0] , X_pca_train_augmented[y_train_predict == i , 1] , label = i)
 
plt.scatter(centroids[:,0] , centroids[:,1] , s = 40, color = 'k')
plt.savefig('KMeans_multi_augmented_data.png')

plt.legend()
plt.show()

confusion_matrix_train = contingency_matrix(y_train_multi,y_train_predict)
confusion_matrix_test = contingency_matrix(y_test_multi,y_test_predict)

confusion = [confusion_matrix_train,confusion_matrix_test]
title = ["confusion_matrix_train","confusion_matrix_test"]

confusion_matrix_train

confusion_matrix_train = confusion_matrix_train[:,[0,1,5,3,4,2]]
confusion = [confusion_matrix_train,confusion_matrix_test]

confusion_matrix_test

confusion_matrix_test = confusion_matrix_test[:,[0,1,4,3,2]]
confusion = [confusion_matrix_train,confusion_matrix_test]

y_train_predict2 = np.where(y_train_predict == 2, -1, y_train_predict)
y_train_predict2 = np.where(y_train_predict2 == 5, 2, y_train_predict2)
y_train_predict2 = np.where(y_train_predict2 == -1, 5, y_train_predict2)

y_test_predict2 = np.where(y_test_predict == 2, -1, y_test_predict)
y_test_predict2 = np.where(y_test_predict == 4, 2, y_test_predict)
y_test_predict2 = np.where(y_test_predict == -1, 4, y_test_predict)

for i in range(2):
  fig, ax = plt.subplots(figsize=(10,10))
  sns.heatmap(confusion[i], annot=True)
  plt.xlabel('Predicted')
  plt.ylabel('Actual')
  plt.title(title[i])
  plt.show()

print("**Training Score:** {}\\".format(accuracy_score(y_train_multi,y_train_predict)))
print("**Test Score:** {}\\".format(accuracy_score(y_test_multi,y_test_predict)))

print("**Training Score:** {}\\".format(accuracy_score(y_train_multi,y_train_predict2)))
print("**Test Score:** {}\\".format(accuracy_score(y_test_multi,y_test_predict2)))