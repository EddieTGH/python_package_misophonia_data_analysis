import pandas as pd
import os
import random


subjN = int(input("Enter Subject Number: "))
#df_path = input("Enter Qualtrics CSV file path without quotes (i.e. 'raw_data.csv'): ")


mapping = pd.read_csv("Misophonia Mapping Sounds.csv")
mapping = mapping[['Name', 'Number']]
mapping.columns = ['Name', 'Sound']


# Creating the DataFrame
#df = pd.read_csv(df_path)
df = pd.read_csv("Miso Raw Data 3.csv")

#remove uneccessary columns
columns_list = df.columns.tolist()
#print(columns_list)
columns_to_remove = ['StartDate', 'EndDate', 'Status', 'IPAddress', 'Progress', 'Duration (in seconds)', 'Finished', 'RecordedDate', 'ResponseId', 'RecipientLastName', 'RecipientFirstName', 'RecipientEmail', 'ExternalReference', 'LocationLatitude', 'LocationLongitude', 'DistributionChannel', 'UserLanguage', 'Browser Type_Browser', 'Browser Type_Version', 'Browser Type_Operating System', 'Browser Type_Resolution', 'sounds', '3Min_Timer_First Click', '3Min_Timer_Last Click', '3Min_Timer_Page Submit', '3Min_Timer_Click Count']
df = df.drop(columns=columns_to_remove)
df.rename(columns={'Subject#': 'Subject Number'}, inplace=True)


# Pivoting the DataFrame to match the desired format

# Melting the dataframe to make it long
df_melted = df.melt(id_vars=["Subject Number"],
                    var_name="Sound_Trigger",
                    value_name="Value")
#df_melted


# Splitting the Sound_Trigger column into two separate columns: one for Sound, another for Trigger/Rating
df_melted['Sound'] = df_melted['Sound_Trigger'].apply(lambda x: x.split('_')[0])
df_melted['Type'] = df_melted['Sound_Trigger'].apply(lambda x: x.split('_')[1])
#df_melted


# Pivoting the table to get the correct format
df_pivoted = df_melted.pivot_table(index=['Subject Number', 'Sound'], columns='Type', values='Value', aggfunc='first').reset_index()
#df_pivoted


# Renaming columns for clarity
df_final = df_pivoted.rename(columns={"Subject Number": "Subject", "Rating": "Rating", "Trigger": "Trigger"})
df_final['Sound'] = df_final['Sound'].astype(int)  # Converting Sound to numeric for proper sorting

df_final = df_final.sort_values(by=['Sound']).reset_index(drop=True)


#merge mapping + df_final
df_final = pd.merge(df_final, mapping, on="Sound")


#Delete this
df_final.rename(columns={'Q49': 'Rating'}, inplace=True)
df_final.rename(columns={'Q51': 'Trigger'}, inplace=True)
df_final.rename(columns={'Q52': 'Memory'}, inplace=True)


#get rid of all NaN values in Trigger column (get rid of positive sounds)
df_final = df_final.dropna(subset=['Trigger'])


#Drop Memory Column (not needed)
df_final = df_final.drop(columns=['Memory'])


df_final['Rating'] = df_final['Rating'].abs()


#print(df_final[df_final['Subject'] == subjN].sort_values(by=['Trigger']).reset_index(drop=True))



sound_rating = df_final[ (df_final['Subject'] == subjN) ]
sound_rating = sound_rating[['Name', 'Trigger', 'Rating']].reset_index(drop=True)



#Create Ranking

# Group by 'Trigger', rank each group, and map the rankings back to the original DataFrame.
sound_rating['Ranking'] = sound_rating.groupby('Trigger')['Rating'].rank(ascending=True, method='first').astype(int)

# Now sort by 'Trigger' and then by 'Ranking' within each group to see the results.
sound_rating.sort_values(by=['Trigger', 'Ranking'], inplace=True)



#Create Order Label
dictionary = {1: "A",
              2: "B",
              3: "C",
              4: "D",
              5: "E",
              6: "F",
              7: "G",
              8: "H",
              9: "I",
              10: "J" }

dictionary2 = {"A": 1,
               "B": 5,
               "C": 2,
               "D": 6,
               "E": 3,
               "F": 7,
               "G": 9,
               "H": 4,
               "I": 8,
               "J": 10}

sound_rating['Alpha'] = sound_rating['Ranking'].map(dictionary)
sound_rating['Order_Label'] = sound_rating['Alpha'].map(dictionary2)

column_to_remove = ['Alpha']
sound_rating = sound_rating.drop(columns=column_to_remove)
print(sound_rating)



# Filtering rows where Trigger is 'Yes', then grouping by 'Subject' and taking the top 2 rows per group based on 'Rating'
df_yes = df_final[ (df_final['Trigger'] == 'Yes') & (df_final['Subject'] == subjN) ].sort_values(by=['Subject', 'Rating'], ascending=[True, False])


# Taking top 10 per person (Subject)
YesMiso_top10 = df_yes.groupby('Subject').head(10).reset_index(drop=True)


#set warning
numRows = YesMiso_top10.shape[0]
numRepeats = 10 - numRows
warning = True if numRows < 10 else False

#repeats < 5 sounds
if numRows < 5:
    items = YesMiso_top10['Name'].tolist()
    duplicates = random.choices(items, k=numRepeats)
elif numRows < 10:
    items = YesMiso_top10['Name'].tolist() #will be more than 5
    duplicates = random.sample(items, k=numRepeats)


# Filtering rows where Trigger is 'No', then grouping by 'Subject' and taking the top 2 rows per group based on 'Rating'
df_no = df_final[ (df_final['Trigger'] == 'No') & (df_final['Subject'] == subjN) ].sort_values(by=['Subject', 'Rating'], ascending=[True, False])

# Taking top 10 per person (Subject)
NoMiso_top10 = df_no.groupby('Subject').head(10).reset_index(drop=True)



# Saving just the Sound column to a new CSV file for each subject number

# Name of the subdirectory to create within the current directory
subdirectory_name = 'SubjectData/subject_' + str(subjN)

# Create the subdirectory if it doesn't exist
if not os.path.exists(subdirectory_name):
    os.makedirs(subdirectory_name)
    
# Filtering out unique subjects
unique_subjects = YesMiso_top10['Subject'].unique()

# Creating a CSV file for each subject containing only the Sound column
csv_paths = []
for subject in unique_subjects:
    # Filter dataframe for each subject
    df_subject_yes = YesMiso_top10[YesMiso_top10['Subject'] == subject]['Name']
    df_subject_no = NoMiso_top10[NoMiso_top10['Subject'] == subject]['Name']

    #if warning is true
    if warning:
        #add those duplicates to the output file

        #create warning text file. Populate with numDuplicates and what are the duplicates?
        csv_file_path_warning = os.path.join(subdirectory_name, f'subject_{subject}_warning.txt')
        dup_set = set(duplicates)
        with open(csv_file_path_warning, 'w') as file:
            file.write("WARNING! SUBJECT DID NOT CLASSIFY 10 UNIQUE SOUNDS AS MISOPHONIC." + "\n\n" + 
                       "Total Number of Missing Miso Sounds (i.e. # Audio Files Repeated to bring total to 10): "
                       + str(numRepeats) + "\n\n" + 
                       "Audio Files that were repeated: " + str(dup_set))
        #print(f"File saved to {csv_file_path_warning}")
        csv_paths.append(csv_file_path_warning)

        # Add duplicates to the existing sounds to create the final sounds (with repeats)
        duplicates_df = pd.DataFrame(duplicates)
        df_subject_yes = pd.concat([df_subject_yes, duplicates_df], ignore_index=True)
        
    
    # Define file path
    csv_file_path_10Miso = os.path.join(subdirectory_name, f'subject_{subject}_Miso_sound.csv')
    csv_file_path_10NonMiso = os.path.join(subdirectory_name, f'subject_{subject}_Aversive_sound.csv')
    csv_file_path_sound_rating = os.path.join(subdirectory_name, f'subject_{subject}_sound_ratings.csv')
    
    # Save the Sound column to CSV
    df_subject_yes.to_csv(csv_file_path_10Miso, index=False, header=False)
    df_subject_no.to_csv(csv_file_path_10NonMiso, index=False, header=False)
    sound_rating.to_csv(csv_file_path_sound_rating, index=False, header=False)
    
    # Collecting file paths for download links
    csv_paths.append(csv_file_path_10Miso)
    csv_paths.append(csv_file_path_10NonMiso)
    csv_paths.append(csv_file_path_sound_rating)

    print(csv_paths)

