"""Script to take the Iowa SOS political candidate information PDF and turn it into an
excel sheet that is organized by contested races. Note this was created for the 2022 races.
Future races may use a different PDF format and so you would need to edit this code.

@author Riley Troyer
scipol@rileytroyer.com
"""

# Import needed libraries
import pandas as pd
from tabula import read_pdf

#filename = 'primarycandidatelist2022'
filename = 'generalcandidatelist2022'

# Read in PDF and create a list of dataframes for each page
df = read_pdf(f'data/raw/candidate-information/{filename}.pdf',
              pages='all')

# Loop through each dataframe and combine into one
for n in range(0, len(df)):
    
    if n==0:
        df_all = df[n]
        
    else:
        df_all = pd.concat([df_all, df[n]],
                                   ignore_index=True)

# Fill in all the race names
office_col = 'For the Office Of...'
df_all[office_col] = df_all[office_col].fillna(method='ffill')

# Fix issue with unnamed columns
df_all['Address'] = df_all['Address'].fillna(df_all['Unnamed: 0'])
df_all['Phone'] = df_all['Phone'].fillna(df_all['Unnamed: 1'])
df_all['Email'] = df_all['Email'].fillna(df_all['Unnamed: 2'])
df_all['Filing Date'] = df_all['Filing Date'].fillna(df_all['Unnamed: 3'])

# Remove unanamed columns
df_all = df_all.drop(['Unnamed: 0',
                      'Unnamed: 1',
                      'Unnamed: 2',
                      'Unnamed: 3'], axis=1)

# Drop address and filing date
df_all = df_all.drop(['Address', 'Filing Date'], axis=1)

# Remove blank/filler lines
df_all = df_all.dropna(axis=0, subset=['Ballot Name(s)'])

# Get only races with a candidate
df_all = df_all.loc[df_all['Ballot Name(s)'] != 'No Candidate']

# Reorder the columns
df_all = df_all.reindex([office_col,
                                         'Ballot Name(s)',
                                         'Party',
                                         'Email',
                                         'Phone'], axis=1)

# Remove races we are not asking
df_all = df_all[df_all[office_col].str
                                .contains('Auditor of State') == False]
df_all = df_all[df_all[office_col].str
                            .contains('Treasurer of State') == False]
df_all = df_all[df_all[office_col].str
                                .contains('Attorney General') == False]

# Figure out which races are contested
df_all['Contested'] = 'yes'

# Loop through each unique offices
for office in df_all[office_col].unique():
    
    df_office = df_all[df_all[office_col] == office]
    
    # Check number in each party running
    num_running = df_office.pivot_table(columns=['Party'],
                                        aggfunc='size')
    
    # Loop through each party and specify if it is contested
    #...obviously this is only for primary
    for party in num_running.index:
        
        if num_running[party] < 2:
            df_all['Contested'][(df_all[office_col] == office)
                                & (df_all['Party'] == party)] = 'no'

# Split into contested and uncontested
df_contested = df_all[df_all['Contested'] == 'yes']
df_uncontested = df_all[df_all['Contested'] == 'no']

# Write lists to different excel sheets
with pd.ExcelWriter(f'data/processed/candidate-information/{filename}.xlsx') as writer:

    df_contested.to_excel(writer, sheet_name='contested',
                          index=False)
    df_uncontested.to_excel(writer, sheet_name='uncontested',
                            index=False)

    