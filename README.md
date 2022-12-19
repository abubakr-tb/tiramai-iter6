# Iteration 6 of TiramAI

## Model
### Multi Linear Regression

Training data - Data including from Iteration 4 and 5
```
X - 'TotalTaskCount','TasksCompleted','TotalEstimated','TotalCompleted','TotalPriority',
    'TasksDelayedCount','TasksDelayedHours','TasksBeforeDue','TasksBeforeDueHours',
    'TotalEstimatedNACount','TotalCompletedNACount','TotalPriorityNACount','EstimationRating',
    'EstimationRatingFactor1','EstimationRatingFactor2','EfficiencyRatingFactor1',
    'EfficiencyRatingFactor2','PriorityRating','TaskWeightageRating'
    
y - 'COG' --> from Iteration 4 and 5
```

## Derived Features
```
EstimationRating - Sum of EstimationRating1 and EstimationRating2
EstimationRating1 - Inc/Dec count depending on Task being completed on time or delayed
EstimationRating2 - Inc/Dec count depending on Task hours being completed on time or delayed
EfficiencyRating1 - Tasks before due completed / Total task count
EfficiencyRating2 - Tasks hours before due completed / Total task hours
PriorityRating - Work Item priority / Sum of Total task count 
TaskWeightageRating - Total task count of individual / Total tasks in iteration
```

## Scaling
### StandardScaler()

## Pickling
Model and Scaler are pickled using pythons ```pickle``` package.

## Metrics
r2 score: 0.992
mse: 3.9
rmse: 1.98

# Pipeline
## Package - ```azure-devops```
A Personal Access Token (PAT) is created in Azure DevOps to enable access to fetch metrics from task board. In Python, scripting is done along with WIQL (Work Item Query Language) to enable getting data from devops. The fetched data is then converted to the features that is implemented in model using Scikit and Pandas.

```
.env
USER_NAME
PERSONAL_ACCESS_TOKEN
ORGANIZATION_URL
```

# Prediction
Final COG is displayed and is appended to a CSV file.
Sample Output on CSV: 
```
[[0,6,2,24,8,12,0,0,0,0,0,4,0,0.0,0,0,0.0,0.0,0.5217391304347826,0.2608695652173913,2.400000000019531,mohamed.m@thinkbridge.in],
 [1,6,1,20,0,12,0,0,0,0,1,6,0,0.0,0,0,0.0,0.0,0.5217391304347826,0.2608695652173913,2.600000000019531,sample@thinkbridge.in],
 [2,5,5,20,20,10,0,0,0,0,0,0,0,0.0,0,0,0.0,0.0,0.43478260869565216,0.21739130434782608,2.0000000002061444,sample2@thinkbridge.in]]
```

Sample output on display:

```
#  COG        Employee
1. 2.4 mohamed.m@thinkbridge.in
2. 2.6 sample@thinkbridge.in
3. 2.0 sample2@thinkbridge.in
```
