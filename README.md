# CMPT 340 Final Project

# Topic: Diagnosing lung diseases using respiratory sounds

## Project Summary
Using machine learning (ML) to automatically classify respiratory sounds (RS)is not a new application. However, the bottleneck to developments in this field results from the lack of publicly-available databases containing RS, both healthyand unhealthy, and expert classification of these sounds. To address this issue,the  International  Conference  on  Biomedical  and  Health  Informatics  (ICBHI) has publicly published a large dataset in 2017 containing 920 respiratory soundrecorded from 126 subjects as part of a Kaggle challenge. 

We will be using this dataset by applying ML classifiers to features extracted from this dataset. The classification of RS using ML can lead to a quick and improved diagnosis of respiratory conditions, sometimes providing a better and more consistentclassification than a manual diagnosis by experts. It can also lead to discoveriesof new and improved methods to diagnose conditions.

## Enivironment used
* Python - version 3.0 or higher
* GoogleColab (**Optional**)

## Required installations 
`pip install -r requirements.txt`

## Data
* All files used and produced are in `All_Features` folder 
### Getting Audio Files
* In order to get the audio files you must download and unzip them
`Link: https://www.kaggle.com/vbookshelf/respiratory-sound-database/download` 

### Unzipping
Now all the other files have already been put in the dataset, so using "unzip_files.py" function in All_features/audio_files on the download should give you everything. And all you must do on lines 34,36 of all_features.py located in All_Features is indicate where all the sound files are at, in your local machine. Then make sure you run your code inside /All_Features.
### Plots
* This file contains all the plots and visualizations

## Order of Execution
* `Optional: Run audio_files/unzip_files.py`
 	* extracts audio files from zip to audio_files

* Run `All_Features/all_features.py` 
	* Extracts the Requred features from the kaggle dataset

* Run `All_Features/Models.py`
	* This file performs various supervised and unsupervised machine learning algorithms on the features.

## Aside
Since all of us worked on GoogleColab for this Project, A comment with the name of the developer is assigned to their respective contribution in 'all_features.py' and 'Models.py'. Since we already set up a discord channel (which was our main source of communication), we didn't use Slack. Please refer to the 'Contributions' part of the report for individual contributions.

## Developers
* Pranav Sood (**301335687**)
* Anuj Rattam (**301339825**)
* Jyotiraditya Mayor (**301401591**)
* Nathaniel Chan (**301314801**)
* Vaibhav Saini (**301386847**)

## Link
https://colab.research.google.com/drive/1hN6gvnhnJSdLHkk7_v_IkS2srr2IGkR-?usp=sharing
This is where we completed the project. 

## Discord Discussion
All of the discussions are on discord and will be provided in the supplementary materials.
