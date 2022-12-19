from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
import os
import numpy as np
import pandas as pd
import pickle as pkl
from azure.devops.v5_1.work_item_tracking.models import Wiql

pd.options.mode.chained_assignment = None

from dotenv import load_dotenv
load_dotenv()

personal_access_token = os.getenv('PERSONAL_ACCESS_TOKEN')
organization_url = os.getenv('ORGANIZATION_URL')
user_name = os.getenv('USER_NAME')

credentials = BasicAuthentication(username=user_name, password=personal_access_token)
connection = Connection(base_url=organization_url, creds=credentials)

core_client = connection.clients.get_core_client()

get_projects_response = core_client.get_projects()
work_item_tracking_client = connection.clients.get_work_item_tracking_client()

project = '[Data Science]'
team = 'Data Science Team'

wiql = Wiql(
        query=f"""
        select [System.Id],
            [System.WorkItemType],
            [System.Title],
            [System.State],
            [System.AreaPath],
            [System.IterationPath],
            [System.AssignedTo],
            [Microsoft.VSTS.Common.ClosedDate],
            [System.CreatedDate],
            [Microsoft.VSTS.Scheduling.CompletedWork],
            [Microsoft.VSTS.Scheduling.OriginalEstimate],
            [Microsoft.VSTS.Common.Priority],
            [System.State]            
        from WorkItems
        where [System.IterationPath] = @CurrentIteration('{project}\\{team}')
        """
    )
#
work_item_info = []
wiql_results = work_item_tracking_client.query_by_wiql(wiql).work_items
if wiql_results:
        print('Retrieving Data...', end=' ')
        work_items = (work_item_tracking_client.get_work_item(int(res.id)) for res in wiql_results)
        for work_item in work_items:
            # print(work_item.id)            
            work_item_ID = work_item.id
            
            try: 
                work_item_WIT = work_item.fields['System.WorkItemType']
            except:
                work_item_WIT = 'NA'
                
            try: 
                work_item_TITLE = work_item.fields['System.Title']
            except:
                work_item_TITLE = 'NA'
                    
            try: 
                work_item_STATE = work_item.fields['System.State']
            except:
                work_item_STATE = 'NA'
                    
            try: 
                work_item_AREAPATH = work_item.fields['System.AreaPath']
            except:
                work_item_AREAPATH = 'NA'
                    
            try: 
                work_item_ITERPATH = work_item.fields['System.IterationPath']
            except:
                work_item_ITERPATH = 'NA'
                    
            try: 
                work_item_ASSIGNEDTO = work_item.fields['System.AssignedTo']['uniqueName']
            except:
                work_item_ASSIGNEDTO = 'NA'
            
            try: 
                work_item_CLOSEDDATE = work_item.fields['Microsoft.VSTS.Common.ClosedDate']
            except:
                work_item_CLOSEDDATE = 'NA'
                
            try: 
                work_item_CREATEDDATE = work_item.fields['System.CreatedDate']
            except:
                work_item_CREATEDDATE = 'NA'

            try: 
                work_item_COMPLETEDWORK = work_item.fields['Microsoft.VSTS.Scheduling.CompletedWork']
            except:
                work_item_COMPLETEDWORK = 'NA'
                    
            try: 
                work_item_ORIGINALESTIMATE = work_item.fields['Microsoft.VSTS.Scheduling.OriginalEstimate']
            except:
                work_item_ORIGINALESTIMATE = 'NA'
                    
            try: 
                work_item_PRIORITY = work_item.fields['Microsoft.VSTS.Common.Priority']
            except:
                work_item_PRIORITY = 'NA'
            
            work_item_info.append([work_item_ID, work_item_WIT, work_item_TITLE, work_item_AREAPATH, work_item_ITERPATH, 
                                   work_item_ASSIGNEDTO, work_item_CLOSEDDATE, work_item_CREATEDDATE, work_item_STATE,
                                   work_item_COMPLETEDWORK, work_item_ORIGINALESTIMATE, work_item_PRIORITY])
        print('done.')
        
df = pd.DataFrame(work_item_info)
df.columns = ['work_item_ID', 'work_item_WIT', 'work_item_TITLE', 'work_item_AREAPATH', 'work_item_ITERPATH', 
              'work_item_ASSIGNEDTO', 'work_item_CLOSEDDATE', 'work_item_CREATEDDATE', 'work_item_STATE',
              'work_item_COMPLETEDWORK', 'work_item_ORIGINALESTIMATE', 'work_item_PRIORITY']

df2 = pd.DataFrame()

df2['Employee'] = df['work_item_ASSIGNEDTO'].unique()
df2['TotalTaskCount'] = 0
df2['TasksCompleted'] = 0
df2['TotalEstimated'] = 0
df2['TotalCompleted'] = 0
df2['TotalPriority'] = 0
df2['TasksDelayedCount'] = 0
df2['TasksDelayedHours'] = 0
df2['TasksBeforeDue'] = 0
df2['TasksBeforeDueHours'] = 0
df2['TotalEstimatedNACount'] = 0
df2['TotalCompletedNACount'] = 0
df2['TotalPriorityNACount'] = 0

#dropping user stories
df = df[df["work_item_WIT"].str.contains("User Story")==False]
df = df.reset_index(drop=True)

for i, df2_employee in enumerate(df2['Employee'].values):
    #total task count
    for df_assignedto in df['work_item_ASSIGNEDTO'].values:
        if df2_employee == df_assignedto:
            df2['TotalTaskCount'][i] += 1 
    
    #total tasks completed        
    for j, df_state in enumerate(df['work_item_STATE'].values):
        if df2_employee == df['work_item_ASSIGNEDTO'][j] and df['work_item_STATE'][j] == 'Done':
            df2['TasksCompleted'][i] += 1
    
        #total estimated hours
        if df2_employee == df['work_item_ASSIGNEDTO'][j] and df['work_item_ORIGINALESTIMATE'][j] != 'NA':
            df2['TotalEstimated'][i] += df['work_item_ORIGINALESTIMATE'][j]
            
        #total completed hours
        if df2_employee == df['work_item_ASSIGNEDTO'][j] and df['work_item_COMPLETEDWORK'][j] != 'NA':
            df2['TotalCompleted'][i] += df['work_item_COMPLETEDWORK'][j]
            
        #priority
        if df2_employee == df['work_item_ASSIGNEDTO'][j] and df['work_item_PRIORITY'][j] != 'NA':
            df2['TotalPriority'][i] += df['work_item_PRIORITY'][j]
        
        #track how many na for each. ie, if they havent filled og values in devops
        if df2_employee == df['work_item_ASSIGNEDTO'][j] and df['work_item_ORIGINALESTIMATE'][j] == 'NA':
            df2['TotalEstimatedNACount'][i] += 1
            
        if df2_employee == df['work_item_ASSIGNEDTO'][j] and df['work_item_COMPLETEDWORK'][j] == 'NA':
            df2['TotalCompletedNACount'][i] += 1
            
        if df2_employee == df['work_item_ASSIGNEDTO'][j] and df['work_item_PRIORITY'][j] == 'NA':
            df2['TotalPriorityNACount'][i] += 1
        
        #check if task was completed on time or delayed
        if df2_employee == df['work_item_ASSIGNEDTO'][j] and df['work_item_ORIGINALESTIMATE'][j] != 'NA' and df['work_item_COMPLETEDWORK'][j] != 'NA' and df['work_item_STATE'][j] == 'Done':
            if df['work_item_ORIGINALESTIMATE'][j] > df['work_item_COMPLETEDWORK'][j]:
                df2['TasksDelayedCount'] += 1
                df2['TasksDelayedHours'] = df['work_item_ORIGINALESTIMATE'][j] - df['work_item_COMPLETEDWORK'][j]
            
            elif df['work_item_ORIGINALESTIMATE'][j] < df['work_item_COMPLETEDWORK'][j]:
                df2['TasksBeforeDue'] += 1
                df2['TasksBeforeDueHours'] = df['work_item_COMPLETEDWORK'][j] - df['work_item_ORIGINALESTIMATE'][j]

#implementing formula - only for features. pred and testing will be based on the value.
df2['EstimationRating'] = 0.0
df2['EstimationRatingFactor1'] = 0
df2['EstimationRatingFactor2'] = 0
df2['EfficiencyRatingFactor1'] = df2['TasksBeforeDue']/df2['TotalTaskCount']
df2['EfficiencyRatingFactor2'] = df2['TasksBeforeDueHours']/df2['TasksCompleted']
df2['EfficiencyRatingFactor1'].fillna(0, inplace=True)
df2['EfficiencyRatingFactor2'].fillna(0, inplace=True)
df2['EstimationRating'] = (df2['EfficiencyRatingFactor1']) +(df2['EfficiencyRatingFactor2'])
df2['PriorityRating'] = 0.0
df2['TaskWeightageRating'] = 0.0

for i, df2_employee in enumerate(df2['Employee'].values):
    #add or remove a point depending on tasks count and hours for delayed and completed before due
    if df2['TasksDelayedCount'][i] > df2['TasksBeforeDue'][i]:
        df2['EstimationRatingFactor1'][i] -= 1
    
    if df2['TasksDelayedCount'][i] < df2['TasksBeforeDue'][i]:
        df2['EstimationRatingFactor1'][i] += 1
        
    if df2['TasksDelayedHours'][i] > df2['TasksBeforeDueHours'][i]:
        df2['EstimationRatingFactor2'][i] -= 1
    
    if df2['TasksDelayedHours'][i] < df2['TasksBeforeDueHours'][i]:
        df2['EstimationRatingFactor2'][i] += 1
    
    #priority rating = sum (wit priority/sum(totaltasks))
    for j, df_state in enumerate(df['work_item_STATE'].values):
        if df2_employee == df['work_item_ASSIGNEDTO'][j] and df['work_item_PRIORITY'][j] != 'NA':
            df2['PriorityRating'][i] += (df['work_item_PRIORITY'][j]/df2['TotalTaskCount'].sum())
    
    #task weight rating = tasks of individual/total tasks present
    df2['TaskWeightageRating'][i] += df2['TotalTaskCount'][i]/df2['TotalTaskCount'].sum()

employee_names = pd.DataFrame()
employee_names['names'] = df2['Employee']
df2.fillna(0, inplace=True)
df2.drop(columns=['Employee'], inplace=True)
# df2.to_csv('another.csv', mode='a', header=False)
df2.replace([np.inf, -np.inf], 0, inplace=True)
print(df2)

model = pkl.load(open('linear_model.pkl', 'rb'))
scaler = pkl.load(open('scaler.pkl', 'rb'))

scaled_df = scaler.transform(df2)
scaled_df = pd.DataFrame(scaled_df, columns=['TotalTaskCount','TasksCompleted','TotalEstimated','TotalCompleted','TotalPriority',
                                             'TasksDelayedCount','TasksDelayedHours','TasksBeforeDue','TasksBeforeDueHours',
                                             'TotalEstimatedNACount','TotalCompletedNACount','TotalPriorityNACount','EstimationRating',
                                             'EstimationRatingFactor1','EstimationRatingFactor2','EfficiencyRatingFactor1',
                                             'EfficiencyRatingFactor2','PriorityRating','TaskWeightageRating'])

y_pred = model.predict(scaled_df)

results = pd.DataFrame()
results['COG'] = pd.DataFrame(y_pred)
results['Employee Name'] = employee_names['names']
df2[['COGScore', 'UniqueName']] = results[['COG', 'Employee Name']]
df2.to_csv('RESULTS.csv', mode='a', header=False)
print(results)
del df, df2, results