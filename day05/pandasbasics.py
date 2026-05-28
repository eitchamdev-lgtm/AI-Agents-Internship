

import pandas as pd 
import os 


#imported os to get the working directory and set the directory 
#where i saved my data set 


os.getcwd()
os.chdir("C:/Users/Lenovo/AI-Agents-Internship/day05")
dataframe = pd.read_csv("Teen_Mental_Health_Dataset.csv") #read_csv tradform csv into data frame 


#see the first 5 rows of the data set (using head)
print(dataframe.head())
print(dataframe.shape) #data set dim (1200 obs )

#lets see the structur (type) of the data set variables 
print(dataframe.dtypes)
#how many missing values missing values 
print(dataframe.isnull().sum())
#decpritve statistics  (basics)
print (dataframe.describe()) 


#how to handle missing values? we can handle it so many ways i will give some examples 
#even if the data set that i have have none
dataframe=dataframe.dropna ()

dataframe=dataframe.fillna(0) #replace na with 0 

dataframe.fillna(dataframe.mean()) #replave missing values with 
#col mean 
# Fill missing values only in numeric columns with the mean
dataframe.fillna(dataframe.select_dtypes(include="number").mean())

#filtering teen with stress level above 3 
high_stress=dataframe[dataframe["stress_level"]>3]

print(high_stress.shape)

# female teens
females = dataframe[dataframe["gender"] == "Female"]
print( females.shape)

#multiple conditions  high stress and poor sleep

high_stress_poor_sleep = dataframe[(dataframe["stress_level"] > 3) & (dataframe["sleep_hours"] < 6)]
print( high_stress_poor_sleep.shape)


# only numeric columns (like is.numeric in R)
numeric_cols = dataframe.select_dtypes(include="number")
print(numeric_cols.head())

# only text/categorical columns
text_cols = dataframe.select_dtypes(include="object")
print(text_cols.head())

#I can also select columns/variables mannualy but name 

# Average stress level by gender ( group_by() %>% summarise(mean_stress = mean(stress_level)))
stress_by_gender = dataframe.groupby("gender")["stress_level"].mean()
print(stress_by_gender)

# average sleep hours by platform usage
sleep_by_platform = dataframe.groupby("platform_usage")["sleep_hours"].mean()
print(sleep_by_platform)


#wanna save the output in excel file for example

dataframe.to_excel("mental_health_data.xlsx", index=False)

