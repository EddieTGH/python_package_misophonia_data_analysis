#1: import packages
import pandas as pd
import numpy as np
import os
import random
import warnings
warnings.filterwarnings('ignore')


def proc_data(subjN, raw_data_path, mapping_data_path):
    #2: get sujN input
    #subjN = int(input("Enter Subject Number: "))
    #df_path = input("Enter Qualtrics CSV file path without quotes (i.e. 'raw_data.csv'): ")



    #3: read in mappings csv
    #mapping = pd.read_csv("Mapping/Misophonia Mapping Sounds 2.csv")
    try:
        mapping = pd.read_csv(mapping_data_path)
    except FileNotFoundError:
        mapping = pd.read_csv(mapping_data_path[3:])

    
    mapping.columns = ['ID', 'Name', 'Sound']



    #4: create dataframe from raw data
    # Creating the DataFrame
    #df = pd.read_csv("Raw Data/miso raw data 10.csv")
    try:
        df = pd.read_csv(raw_data_path)
    except FileNotFoundError:
        df = pd.read_csv(raw_data_path[3:])



    #5: return current suject row and check if it exists
    df.rename(columns={'subject_number': 'Subject Number'}, inplace=True)
    df = df[df['Subject Number'] == str(subjN)]

    if df.shape[0] == 0:
        print("\n")
        print("Error: Subject Number: " + str(subjN) + " not found!")
        print("\n")
        return
    else:
        print("\n")
        print("Subject Number: " + str(subjN) + " found!!")
        print("\n")



    #6: get date and remove uneccessary columns
    date = df['StartDate'].iloc[0]
    date = date[:10]

    #remove uneccessary columns
    columns_list = df.columns.tolist()
    #V1
    columns_to_remove = ['StartDate', 'EndDate', 'Status', 'IPAddress', 'Progress', 'Duration (in seconds)', 'Finished', 'RecordedDate', 'ResponseId', 'RecipientLastName', 'RecipientFirstName', 'RecipientEmail', 'ExternalReference', 'LocationLatitude', 'LocationLongitude', 'DistributionChannel', 'UserLanguage', 'Browser Type_Browser', 'Browser Type_Version', 'Browser Type_Operating System', 'Browser Type_Resolution', 'sounds', 'txtFile', 'subject_numbers', 'foundSubject', 'Order', 'EndLoop']
    
    #V2
    #columns_to_remove = ['StartDate', 'EndDate', 'Status', 'IPAddress', 'Progress', 'Duration (in seconds)', 'Finished', 'RecordedDate', 'ResponseId', 'RecipientLastName', 'RecipientFirstName', 'RecipientEmail', 'ExternalReference', 'LocationLatitude', 'LocationLongitude', 'DistributionChannel', 'UserLanguage', 'Browser Type_Browser', 'Browser Type_Version', 'Browser Type_Operating System', 'Browser Type_Resolution', 'sounds', 'txtFile1', 'txtFile2', 'txtFile3', 'txtFile4', 'txtFile5', 'subject_numbers', 'foundSubject', 'Order', 'EndLoop']
    
    df = df.drop(columns=columns_to_remove)



    #7: Pivoting the DataFrame to match the desired format
    # Melting the dataframe to make it long
    df_melted = df.melt(id_vars=["Subject Number"],
                        var_name="Sound_Trigger",
                        value_name="Value")



    #8: Splitting the Sound_Trigger column into two separate columns: one for Sound, another for Trigger/Rating
    df_melted['Sound'] = df_melted['Sound_Trigger'].apply(lambda x: x.split('_')[0])
    df_melted['Type'] = df_melted['Sound_Trigger'].apply(lambda x: x.split('_')[1])



    #9: Pivoting the table to get the correct format
    df_pivoted = df_melted.pivot_table(index=['Subject Number', 'Sound'], columns='Type', values='Value', aggfunc='first').reset_index()



    #10: Renaming columns for clarity and additional cleaning
    df_final = df_pivoted.rename(columns={"Subject Number": "Subject", "Rating": "Rating", "Trigger": "Trigger"})
    df_final['Sound'] = df_final['Sound'].astype(int)  # Converting Sound to numeric for proper sorting

    df_final = df_final.sort_values(by=['Sound']).reset_index(drop=True)
    #fix qualtrics bug
    df_final.loc[df_final['Sound'] > 56, 'Sound'] -= 3

    #merge mapping + df_final
    df_final = pd.merge(df_final, mapping, on="Sound")

    #check if all columns exist
    if 'Rating' not in df_final.columns:
        print("Subject did not rate any sounds in the Sound Task Form. Sound stimuli unable to be generated. Have them retake the form or remove them from the study.")
        return
    if 'Trigger' not in df_final.columns:
        df_final['Trigger'] = np.nan
        print("Subject did not rate any sounds in the Sound Task Form as misophonic or aversive. Sound stimuli unable to be generated. Have them retake the form or remove them from the study.")
        return
    if 'Memory' not in df_final.columns:
        df_final['Memory'] = np.nan
        print("Subject did not rate any sounds in the Sound Task Form as positive or neutral.")  

    df_final = df_final[['Subject', 'Sound', 'Name', 'Rating', 'Trigger', 'Memory', 'Order']]
    df_final = df_final[df_final['Rating'].notna()]





    #23: Create Warning File for MRI
    # Name of the output directory to create within the current directory

    #check which directory i'm in:
    if os.path.exists('misophonia_data_analysis'):
        output_directory_name = '../output_data/subject_' + str(subjN)
    else:
        output_directory_name = '../../output_data/subject_' + str(subjN)

    csv_paths = []

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_directory_name):
        os.makedirs(output_directory_name)

    
    warning_NotComplete = False
    sounds_rated = df_final.shape[0]

    if sounds_rated < 106:
        warning_NotComplete = True


    #if warning is true
    if warning_NotComplete:
        csv_file_path_warning_NotComplete = os.path.join(output_directory_name, f'subject_{subjN}_Form_Not_Complete.txt')
        
        with open(csv_file_path_warning_NotComplete, 'w') as file:
            file.write("WARNING! SUBJECT DID NOT COMPLETE SOUND TASK FORM." + "\n\n" + 
                    "Total Number of Sounds Rated: " +  str(sounds_rated) + "\n\n" +
                    "Total Number of Sounds Not Rated: " + str(106-sounds_rated))
            
        print(f"File saved to {csv_file_path_warning_NotComplete}")
        csv_paths.append(csv_file_path_warning_NotComplete)
    






    #11: print NA rows
    nan_rows = df_final[df_final['Rating'].isna()]
    print("NA Rows: \n")
    print(nan_rows)
    print("\n\n")



    #13: Create sound_rating_all: Sound Rating Table for ALL sounds AND print
    sound_rating_all = df_final[['Subject', 'Sound', 'Name', 'Rating', 'Trigger', 'Memory', 'Order']]
    sound_rating_all['Date'] = date

    sound_rating_all = sound_rating_all[['Subject', 'Date', 'Order', 'Name', 'Rating', 'Trigger', 'Memory']]
    print("Sound Ratings All: \n")
    print(sound_rating_all)
    print("\n\n")



    #14: Create df_miso_aversive: Sound Rating Table for Miso and Aversive sounds AND print
    #get rid of all NaN values in Trigger column (get rid of positive sounds)
    df_miso_aversive = df_final.dropna(subset=['Trigger'])
    #Drop Memory Column (not needed)
    df_miso_aversive = df_miso_aversive.drop(columns=['Memory'])
    #convert str --> int
    df_miso_aversive['Rating'] = df_miso_aversive['Rating'].astype(int)
    #abs value of ratings
    df_miso_aversive['Rating'] = df_miso_aversive['Rating'].abs()


    df_miso = df_miso_aversive[df_miso_aversive['Trigger'] == 'Yes'].reset_index(drop=True)
    numMiso = df_miso.shape[0]
    if numMiso == 0:
        print("Subject did not rate any sounds as misophonic sounds. No stimuli files can be generated.")
        return

    df_aversive = df_miso_aversive[df_miso_aversive['Trigger'] == 'No'].reset_index(drop=True)
    numAver = df_miso.shape[0]
    if numAver == 0:
        print("Subject did not rate any sounds as aversive sounds. No stimuli files can be generated.")
        return





    #15: Create df_miso: Sound Rating Table for Miso sounds
    df_miso = df_miso_aversive[df_miso_aversive['Trigger'] == 'Yes'].reset_index(drop=True)



    #16: Create df_aversive: Sound Rating Table for Aversive sounds
    df_aversive = df_miso_aversive[df_miso_aversive['Trigger'] == 'No'].reset_index(drop=True)



    #17: Create df_mri_ratings: 20 mri sounds ratings table
    df_miso_10 = df_miso.sort_values(by=['Rating'], ascending = False).head(10).reset_index(drop=True)
    df_aversive_10 = df_aversive.sort_values(by=['Rating'], ascending = False).head(10).reset_index(drop=True)



    #18: Set Warning MRI Miso for df_miso (less than 10 sounds)
    warning_MRI_miso_less10 = False
    warning_MRI_numRows__miso = df_miso_10.shape[0] #num miso sounds provided
    #warning_MRI_numRows__miso = 9 #testing

    warning_MRI_miso_sounds_added = "None" #MISO Sounds ADDED
    warning_MRI_miso_sounds_repeated = "None" #MISO SoundsREPEATED
    warning_MRI_num_miso_sounds_ADD_REPEAT = 0 #NUM MISO ADDED/REPEATED

    #How do these warnings work:
    #If there are less than 6 misophonic sounds, pull from all m_ sounds.
    #Take all aversive sounds from m_ sounds and sort them from most negative to least negative (most negative --> least negative)
    #Take all neut/pos sounds from m_ sounds and sort them from least positive to most positive (most negative --> least negative)
    #Concat aversive --> neut/pos sounds together and take only the most negative x sounds needed to hit 10 sounds
    #Coerce all sounds to be miso and change all neg values to abs values

    #if there are 6 or more misophonic sounds, select randomly without repeating and hit 10 miso sounds (no more than 1 repeat per sound)

    if warning_MRI_numRows__miso <= 5:
        warning_MRI_miso_less10 = True
        warning_MRI_numRepeats_miso = 10 - warning_MRI_numRows__miso #num miso sounds needed

        nontriggerMiso_sounds_Mprefix = df_final[(df_final['Sound'] >= 26) & (df_final['Sound'] <= 95)].drop('Memory', axis=1)

        aversiveRatings = nontriggerMiso_sounds_Mprefix[nontriggerMiso_sounds_Mprefix['Trigger'] == 'No']
        aversiveRatings = aversiveRatings.sort_values(by=['Rating'], ascending=True) #.head(warning_MRI_numRepeats_miso)

        posNeutRatings = nontriggerMiso_sounds_Mprefix[nontriggerMiso_sounds_Mprefix['Trigger'].isna()]

        posNeutRatings['Rating'] = posNeutRatings['Rating'].astype(int)
        posNeutRatings = posNeutRatings.sort_values(by=['Rating'], ascending=True) #.head(warning_MRI_numRepeats_miso)
        #print(posNeutRatings)
        
        aversive_posNeut_Ratings = pd.concat([aversiveRatings, posNeutRatings])
        #print(aversive_posNeut_Ratings)
        aversive_posNeut_Ratings = aversive_posNeut_Ratings.head(warning_MRI_numRepeats_miso)

        #if not enough sounds
        numExtraSounds = aversive_posNeut_Ratings.shape[0]
        
        if numExtraSounds < warning_MRI_numRepeats_miso:
            DUPLICATES_MISO = df_miso_10.sample(n=warning_MRI_numRepeats_miso, replace=True)

            warning_MRI_miso_sounds_repeated = set(DUPLICATES_MISO['Name']) #which miso sounds added
            warning_MRI_num_miso_sounds_ADD_REPEAT = len(DUPLICATES_MISO) #num miso sound added 
            
            df_miso_10 = pd.concat([df_miso_10, DUPLICATES_MISO], ignore_index=True)
            
        else:
            #Coerce
            aversive_posNeut_Ratings['Trigger'] = 'Yes'
            aversive_posNeut_Ratings['Rating'] = aversive_posNeut_Ratings['Rating'].astype(int)
            aversive_posNeut_Ratings['Rating'] = aversive_posNeut_Ratings['Rating'].abs()
        
            warning_MRI_miso_sounds_added = set(aversive_posNeut_Ratings['Name']) #which miso sounds added
            warning_MRI_num_miso_sounds_ADD_REPEAT = len(aversive_posNeut_Ratings) #num miso sound added 
            
            df_miso_10 = pd.concat([df_miso_10, aversive_posNeut_Ratings], ignore_index=True)


    if (warning_MRI_numRows__miso > 5) and (warning_MRI_numRows__miso < 10):
        warning_MRI_miso_less10 = True
        warning_MRI_numRepeats_miso = 10 - warning_MRI_numRows__miso #num miso sounds needed

        DUPLICATES_5to10_MRI = df_miso_10.sample(n=warning_MRI_numRepeats_miso)
        
        warning_MRI_miso_sounds_repeated = set(DUPLICATES_5to10_MRI['Name'])  #which miso sounds repeated
        warning_MRI_num_miso_sounds_ADD_REPEAT = len(warning_MRI_miso_sounds_repeated) #num miso sound added 
        
        df_miso_10 = pd.concat([df_miso_10, DUPLICATES_5to10_MRI], ignore_index=True)




    #20 Set Warning MRI Aversive for df_aversive (less than 10 sounds)
    warning_MRI_aver_less10 = False
    warning_MRI_numRows__aversive = df_aversive_10.shape[0]

    warning_MRI_aver_sounds_added = "None"
    warning_MRI_aver_sounds_repeated = "None"
    warning_MRI_num_aver_sounds_ADD_REPEAT = 0

    #How do these warnings work:
    #If there are less than 6 aversive sounds, pull from all a_ sounds that are not misophonic or aversive
    #Take all neut/pos sounds from a_ sounds and sort them from least positive to most positive (worst --> best)
    #Coerce all sounds to be aversive

    #if there are 6 or more aversive sounds, select randomly without repeating and hit 10 aver sounds (no more than 1 repeat per sound)

    if warning_MRI_numRows__aversive <= 5:
        warning_MRI_aver_less10 = True
        warning_MRI_numRepeats_aver = 10 - warning_MRI_numRows__aversive #num aver sounds repeated

        aversive_sounds_Aprefix = df_final[(df_final['Sound'] >= 7) & 
                                    (df_final['Sound'] <= 25) & 
                                    (df_final['Trigger'] != 'Yes')].drop('Memory', axis=1) #aversive/pos/neut sounds

        
        #aversiveRatings = aversive_sounds_Aprefix[aversive_sounds_Aprefix['Trigger'] == 'No']
        #aversiveRatings = aversiveRatings.sort_values(by=['Rating'], ascending=True) #.head(warning_MRI_numRepeats_miso)

        posNeutRatings = aversive_sounds_Aprefix[aversive_sounds_Aprefix['Trigger'].isna()]

        posNeutRatings['Rating'] = posNeutRatings['Rating'].astype(int)
        posNeutRatings = posNeutRatings.sort_values(by=['Rating'], ascending=True).head(warning_MRI_numRepeats_aver)
        
        #if not enough sounds
        numExtraSounds = posNeutRatings.shape[0]
        
        if numExtraSounds < warning_MRI_numRepeats_aver:
            DUPLICATES_AVER = df_aversive_10.sample(n=warning_MRI_numRepeats_aver, replace=True)

            warning_MRI_aver_sounds_repeated = set(DUPLICATES_AVER['Name']) #which miso sounds added
            warning_MRI_num_aver_sounds_ADD_REPEAT = len(DUPLICATES_AVER) #num miso sound added 
            
            df_aversive_10 = pd.concat([df_aversive_10, DUPLICATES_AVER], ignore_index=True)
        
        else:
            #Coerce
            posNeutRatings['Trigger'] = 'No'
        
            warning_MRI_aver_sounds_added = set(posNeutRatings['Name']) #which aver sounds added
            warning_MRI_num_aver_sounds_ADD_REPEAT = len(warning_MRI_aver_sounds_added) #num aver sound added 
            
            df_aversive_10 = pd.concat([df_aversive_10, posNeutRatings], ignore_index=True)


    if (warning_MRI_numRows__aversive > 5) and (warning_MRI_numRows__aversive < 10):
        warning_MRI_aver_less10 = True
        warning_MRI_numRepeats_aver = 10 - warning_MRI_numRows__aversive

        DUPLICATES_5to10_MRI = df_aversive_10.sample(n=warning_MRI_numRepeats_aver)
        
        warning_MRI_aver_sounds_repeated = set(DUPLICATES_5to10_MRI['Name'])  #which aver sounds repeated
        warning_MRI_num_aver_sounds_ADD_REPEAT = len(warning_MRI_aver_sounds_repeated) #num aver sound added 
        
        df_aversive_10 = pd.concat([df_aversive_10, DUPLICATES_5to10_MRI], ignore_index=True)





    #if warning is true
    if warning_MRI_miso_less10 or warning_MRI_aver_less10:
        #create warning text file. Populate with numDuplicates and what are the duplicates?
        csv_file_path_warning_MRI = os.path.join(output_directory_name, f'subject_{subjN}_MRI_warning.txt')
        
        with open(csv_file_path_warning_MRI, 'w') as file:
            if warning_MRI_miso_less10:
                file.write("WARNING! SUBJECT DID NOT CLASSIFY 10 UNIQUE SOUNDS AS MISOPHONIC." + "\n\n" + 
                        "Total Number of Classified Misophonic Sounds: " +  str(warning_MRI_numRows__miso) + "\n\n" +
                        "Total Number of Missing Misophonic Sounds: " +  str(warning_MRI_numRepeats_miso) + "\n\n" + 
                        "Repeated Misophonic Sounds: " + str(warning_MRI_miso_sounds_repeated) + "\n\n" +
                        "Added Non-Trigger High Arousal 'Misophonic' (m_) Sounds: " + str(warning_MRI_miso_sounds_added) + "\n\n" +
                        "Total Number of Repeated/Added Misophonic Sounds: " + str(warning_MRI_num_miso_sounds_ADD_REPEAT) + "\n\n\n\n\n")
                
            if warning_MRI_aver_less10:
                file.write("WARNING! SUBJECT DID NOT CLASSIFY 10 UNIQUE SOUNDS AS AVERSIVE." + "\n\n" + 
                        "Total Number of Classified Misophonic Sounds: " +  str(warning_MRI_numRows__aversive) + "\n\n" +
                        "Total Number of Missing Aversive Sounds: " +  str(warning_MRI_numRepeats_aver) + "\n\n" + 
                        "Repeated Aversive Sounds: " + str(warning_MRI_aver_sounds_repeated) + "\n\n" +
                        "Added Positive/Neutral Low Arousal 'Aversive' (a_) Sounds: " + str(warning_MRI_aver_sounds_added) + "\n\n" +
                        "Total Number of Repeated/Added Misophonic Sounds: " + str(warning_MRI_num_aver_sounds_ADD_REPEAT) + "\n\n")
                
            
        print(f"\nMRI warning file generated and saved to {csv_file_path_warning_MRI}\n")
        csv_paths.append(csv_file_path_warning_MRI)





    #25: Create df_mri_ratings: concat miso+aversive
    df_mri_ratings = pd.concat([df_miso_10, df_aversive_10], ignore_index=True)
    print("MRI Ratings: \n")
    print(df_mri_ratings)
    print("\n\n")


    #26: Create Rankings/Order labels for Nimesha
    #Create Ranking

    # Group by 'Trigger', rank each group, and map the rankings back to the original DataFrame.
    df_mri_ratings['Rating'] = df_mri_ratings['Rating'].astype(int)
    df_mri_ratings['Ranking'] = df_mri_ratings.groupby('Trigger')['Rating'].rank(ascending=True, method='first').astype(int)

    # Now sort by 'Trigger' and then by 'Ranking' within each group to see the results.
    df_mri_ratings.sort_values(by=['Trigger', 'Ranking'], inplace=True)

    df_mri_ratings = df_mri_ratings.reset_index(drop=True)

    #Create Order Label
    dictionary11 = {1: "A",
                2: "C",
                3: "E",
                4: "H",
                5: "B",
                6: "D",
                7: "F",
                8: "I",
                9: "G",
                10: "J" }

    dictionary22 = {"A": 1,
                "B": 2,
                "C": 3,
                "D": 4,
                "E": 5,
                "F": 6,
                "G": 7,
                "H": 8,
                "I": 9,
                "J": 10}

    df_mri_ratings['Alpha'] = df_mri_ratings['Ranking'].map(dictionary11)
    df_mri_ratings['Order_Label'] = df_mri_ratings['Alpha'].map(dictionary22)

    column_to_remove = ['Subject', 'Sound', 'Alpha', 'Order']
    df_mri_ratings_nimesha = df_mri_ratings.drop(columns=column_to_remove)
    print("Nimesha MRI Ratings: \n")
    print(df_mri_ratings_nimesha)
    print("\n\n")



    #29: List of df_mri_sounds and print
    df_mri_sound_names = df_mri_ratings['Name']
    print("MRI Sound Names: \n")
    print(df_mri_sound_names)
    print("\n\n")



    #30: Create df_tms_ratings: 24 tms sounds ratings table
    #Warning
    warning_TMS_less12 = False
    warning_TMS_less24 = False

    numMiso = df_miso.shape[0]
    num_Mprefix_needed = 0
    warning_Miso_added = "None"

    num_Mprefix_needed = 0

    #How do these warnings work:
    #If there are less than 12 misophonic sounds, pull from all m_ sounds.
    #Take all aversive sounds from m_ sounds and sort them from most negative to least negative (most negative --> least negative)
    #Take all neut/pos sounds from m_ sounds and sort them from least positive to most positive (most negative --> least negative)
    #Concat aversive --> neut/pos sounds together and take only the most negative x sounds needed to hit 12 sounds
    #Coerce all sounds to be miso and change all neg values to abs values
    #Duplicate these 12 sounds (repeating each sound once) to hit 24

    if numMiso < 12: #if we need to add miso non-trigger sounds
        num_Mprefix_needed = 12 - numMiso
        #Create Highest Aversive Rating of Sounds 26-98 "m_...wav"

        nontriggerMiso_sounds_Mprefix = df_final[(df_final['Sound'] >= 26) & (df_final['Sound'] <= 95)].drop('Memory', axis=1)

        aversiveRatings = nontriggerMiso_sounds_Mprefix[nontriggerMiso_sounds_Mprefix['Trigger'] == 'No']
        aversiveRatings = aversiveRatings.sort_values(by=['Rating'], ascending=True) #.head(warning_MRI_numRepeats_miso)

        posNeutRatings = nontriggerMiso_sounds_Mprefix[nontriggerMiso_sounds_Mprefix['Trigger'].isna()]

        posNeutRatings['Rating'] = posNeutRatings['Rating'].astype(int)
        posNeutRatings = posNeutRatings.sort_values(by=['Rating'], ascending=True) #.head(warning_MRI_numRepeats_miso)
        #print(posNeutRatings)
        
        aversive_posNeut_Ratings = pd.concat([aversiveRatings, posNeutRatings])
        #print(aversive_posNeut_Ratings)
        aversive_posNeut_Ratings = aversive_posNeut_Ratings.head(num_Mprefix_needed)
        #print(aversive_posNeut_Ratings)

        #if not enough sounds
        numExtraSounds = aversive_posNeut_Ratings.shape[0]
        if numExtraSounds < num_Mprefix_needed:
            DUPLICATES_MISO = df_miso_10.sample(n=num_Mprefix_needed, replace=True)
            df_tms_ratings = pd.concat([df_miso, DUPLICATES_MISO], ignore_index=True)
        
        else:
            #Coerce
            aversive_posNeut_Ratings['Trigger'] = 'Yes'
            aversive_posNeut_Ratings['Rating'] = aversive_posNeut_Ratings['Rating'].astype(int)
            aversive_posNeut_Ratings['Rating'] = aversive_posNeut_Ratings['Rating'].abs()
            #print(aversive_posNeut_Ratings)
        
            warning_Miso_added = set(aversive_posNeut_Ratings['Name'])
        
            df_tms_ratings = pd.concat([df_miso, aversive_posNeut_Ratings], ignore_index=True)

        warning_Miso_repeated = set(df_tms_ratings['Name'])
        
        df_tms_ratings_copy = df_tms_ratings.copy()
        df_tms_ratings = pd.concat([df_tms_ratings, df_tms_ratings_copy], ignore_index=True)
        
        #coerce every trigger to be yes
        df_tms_ratings['Trigger'] = 'Yes'
        df_tms_ratings['Rating'] = df_tms_ratings['Rating'].astype(int)
        df_tms_ratings = df_tms_ratings.sort_values(by=['Rating'], ascending=True)

        category = [0,0,0,0,0,0,1,1,1,1,1,1,2,2,2,2,2,2,3,3,3,3,3,3]
        df_tms_ratings['Category'] = category


        warning_TMS_less12 = True


    #if there are between 13 and 23, select randomly without repeating and hit 24 miso sounds (no more than 1 repeat per sound)
    if (numMiso >= 12) and (numMiso < 24):
        num_Mprefix_needed = 24 - numMiso
        DUPLICATES_12to24_tms = df_miso.sample(n=num_Mprefix_needed)

        warning_Miso_repeated = set(DUPLICATES_12to24_tms['Name'])
        
        df_tms_ratings = pd.concat([df_miso, DUPLICATES_12to24_tms], ignore_index=True)

        #coerce every trigger to be yes
        df_tms_ratings['Trigger'] = 'Yes'
        df_tms_ratings['Rating'] = df_tms_ratings['Rating'].astype(int)
        df_tms_ratings = df_tms_ratings.sort_values(by=['Rating'], ascending=True)

        category = [0,0,0,0,0,0,1,1,1,1,1,1,2,2,2,2,2,2,3,3,3,3,3,3]
        df_tms_ratings['Category'] = category

        warning_TMS_less24 = True


    if numMiso >= 24:
        #create 6 personalized, and then choose 6 top and 6 bottom from nonpersonalized
        #change this
        df_miso_personalized = df_final[df_final['Sound'] <= 6]
        #df_miso_personalized = df_miso[df_miso['Sound'] <= 6]
        
        df_miso_noPersonalized = df_miso[df_miso['Sound'] > 6]
        df_miso_NP_6Highest = df_miso_noPersonalized.sort_values(by=['Rating'], ascending = False).head(6).reset_index(drop=True)
        df_miso_NP_6Lowest = df_miso_noPersonalized.sort_values(by=['Rating'], ascending = True).head(6).reset_index(drop=True)
        
        #Get rid of top 6 and bottom 6 sounds to pull random sounds for middle 6
        NP_Or6Highest = pd.concat([df_miso_noPersonalized, df_miso_NP_6Highest, df_miso_NP_6Highest]).drop_duplicates(keep=False)
        NP_Or6Highest_Or6Lowest = pd.concat([NP_Or6Highest, df_miso_NP_6Lowest, df_miso_NP_6Lowest]).drop_duplicates(keep=False)
        df_miso_NP_6Middle = NP_Or6Highest_Or6Lowest.sample(n=6)
        
        #concat all together
        df_tms_ratings = pd.concat([df_miso_NP_6Lowest, df_miso_NP_6Middle, df_miso_NP_6Highest, df_miso_personalized], ignore_index=True)
        category = [0,0,0,0,0,0,1,1,1,1,1,1,2,2,2,2,2,2,3,3,3,3,3,3]
        df_tms_ratings['Category'] = category


    #if warning is true
    if warning_TMS_less12 or warning_TMS_less24:
        #create warning text file. Populate with numDuplicates and what are the duplicates?
        csv_file_path_warning_TMS = os.path.join(output_directory_name, f'subject_{subjN}_TMS_warning.txt')
        
        with open(csv_file_path_warning_TMS, 'w') as file:
            if warning_TMS_less12:
                file.write("WARNING! SUBJECT CLASSIFIED LESS THAN 12 UNIQUE SOUNDS AS MISOPHONIC." + "\n\n" + 
                        "Total Number of Classified Misophonic Sounds: " +  str(numMiso) + "\n\n" +
                        "Total Number of Missing Misophonic Sounds: " +  str(num_Mprefix_needed+12) + "\n\n" + 
                        "Added Non-Trigger High Arousal 'Misophonic' (m_) Sounds: " + str(warning_Miso_added) + "\n\n" +
                        "Repeated Misophonic Sounds (Repeated Once): " + str(warning_Miso_repeated) + "\n\n" +
                        "Total Number of Repeated/Added Misophonic Sounds: " + str(num_Mprefix_needed+12) + "\n\n\n\n\n")
            else: #12 to 24 sounds
                file.write("WARNING! SUBJECT CLASSIFIED LESS THAN 24 UNIQUE SOUNDS AS MISOPHONIC." + "\n\n" + 
                        "Total Number of Classified Misophonic Sounds: " +  str(numMiso) + "\n\n" +
                        "Total Number of Missing Misophonic Sounds: " +  str(num_Mprefix_needed) + "\n\n" + 
                        "Repeated Misophonic Sounds: " + str(warning_Miso_repeated) + "\n\n" +
                        "Added Non-Trigger High Arousal 'Misophonic' (m_) Sounds: " + "None" + "\n\n" +
                        "Total Number of Repeated/Added Misophonic Sounds: " + str(num_Mprefix_needed) + "\n\n\n\n\n")
                
            
        print(f"\nTMS warning file generated and saved to {csv_file_path_warning_TMS}\n")
        csv_paths.append(csv_file_path_warning_TMS)


    df_tms_ratings_FINAL = df_tms_ratings[['Subject', 'Category', 'Name', 'Trigger', 'Rating']]
    print("TMS Ratings: \n")
    print(df_tms_ratings_FINAL)
    print("\n\n")

    df_tms_sound_names = df_tms_ratings['Name']
    print("TMS Sound Names: \n")
    print(df_tms_sound_names)
    print("\n\n")





    #Follow up Task
    #create miso sounds table not in stimuli
    miso_not_in_mri = pd.concat([df_miso, df_miso_10, df_miso_10]).drop_duplicates(keep=False)
    #print(miso_not_in_mri)

    mod_df_tms_ratings = df_tms_ratings[['Subject', 'Sound', 'Name', 'Rating', 'Trigger', 'Order']]
    miso_not_in_mri_tms = pd.concat([miso_not_in_mri, mod_df_tms_ratings, mod_df_tms_ratings]).drop_duplicates(keep=False)
    #print(miso_not_in_mri_tms)

    try: 
        subset_miso_not_in_mri_tms = miso_not_in_mri_tms.sample(n=4)
    except:
        subset_miso_not_in_mri_tms = miso_not_in_mri_tms.head(4)


    #generate UNIQUE total stimuli list (24+10-duplicates)
    total_stim = pd.concat([df_aversive_10['Name'], df_tms_sound_names]).reset_index(drop=True)
    total_stim = pd.concat([total_stim, subset_miso_not_in_mri_tms['Name']]).reset_index(drop=True)
    total_stim_set = set(total_stim)
    total_stim_list_unique = list(total_stim_set)
    #print(total_stim_list_unique)
    total_stim_unique = pd.DataFrame(total_stim_list_unique, columns=['Name'])


    #Fill up extra spaces with neutral/positive sounds
    total_received = total_stim_unique.shape[0]
    total_needed = 38 - total_received

    #add neutral sounds
    #get rid of all NaN values in Memory column (get rid of aver/miso sounds)
    df_pos_neut = df_final.dropna(subset=['Memory'])

    try:
        subset_df_pos_neut = df_pos_neut.sample(n=total_needed)
    except:
        subset_df_pos_neut = df_pos_neut.head(total_needed)

    #add neutral/positive sounds
    final_followup_stim = pd.concat([total_stim_unique['Name'], subset_df_pos_neut['Name']]).reset_index(drop=True)
    
    #randomize the rows
    final_followup_stim = final_followup_stim.sample(frac=1).reset_index(drop=True)

    print("Follow Up Stimuli: \n")
    print(final_followup_stim)
    print("\n\n")


    #Map these names to their unique IDs
    # Create a dictionary from 'mapping' DataFrame where 'Name' is the key and 'ID' is the value
    name_to_id = dict(zip(mapping['Name'], mapping['ID']))

    # Map the 'names' Series to get the corresponding 'ID' values
    matched_ids = final_followup_stim.map(name_to_id)

    # Convert the Series to a list
    ids_list = matched_ids.tolist()
    #print(ids_list)

    # Join the list into a string with comma-separated values
    csv_followup_stim_ids = ','.join(ids_list)

    print("Follow Up Stimuli Sound IDs List: \n")
    print(csv_followup_stim_ids)
    print("\n\n")

    #save txtfile
    csv_file_path_follow_up_stim = os.path.join(output_directory_name, f'subject_{subjN}_Follow_Up_Stimuli.txt')
        
    with open(csv_file_path_follow_up_stim, 'w') as file:
        file.write(csv_followup_stim_ids)
        
    csv_paths.append(csv_file_path_follow_up_stim)
    print(f"File saved to {csv_file_path_follow_up_stim}")
    print("\n")







    #37: Save file paths
    # Define file path
    csv_file_path_20MRI_sounds = os.path.join(output_directory_name, f'subject_{subjN}_20MRI_sounds_names.csv')
    csv_file_path_sound_rating_MRI = os.path.join(output_directory_name, f'subject_{subjN}_20MRI_sounds_ratings.csv')
    csv_file_path_24TMS_sounds = os.path.join(output_directory_name, f'subject_{subjN}_24TMS_sounds_names.csv')
    csv_file_path_sound_rating_TMS = os.path.join(output_directory_name, f'subject_{subjN}_24TMS_sounds_ratings.csv')
    csv_file_path_sound_rating_ALL = os.path.join(output_directory_name, f'subject_{subjN}_ALL_sounds_ratings.csv')


    # Save the Sound column to CSV
    df_mri_sound_names.to_csv(csv_file_path_20MRI_sounds, index=False, header=False)
    df_mri_ratings_nimesha.to_csv(csv_file_path_sound_rating_MRI, index=False, header=True)
    df_tms_sound_names.to_csv(csv_file_path_24TMS_sounds, index=False, header=False)
    df_tms_ratings_FINAL.to_csv(csv_file_path_sound_rating_TMS, index=False, header=True)
    sound_rating_all.to_csv(csv_file_path_sound_rating_ALL, index=False, header=True)

    # Collecting file paths for download links
    csv_paths.append(csv_file_path_20MRI_sounds)
    csv_paths.append(csv_file_path_sound_rating_MRI)
    csv_paths.append(csv_file_path_24TMS_sounds)
    csv_paths.append(csv_file_path_sound_rating_TMS)
    csv_paths.append(csv_file_path_sound_rating_ALL)

    print("All CSVs and txtFiles generated and populated into the corresponding subjects folder: \n")
    for i in range(len(csv_paths)):
        print(csv_paths[i])

    print("\nProgram Finished: Success!\n")