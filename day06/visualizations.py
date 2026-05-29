import matplotlib.pyplot as plot
import seaborn as sns
import pandas as pd 
import os 

os.chdir("C:/Users/Lenovo/AI-Agents-Internship/day05") #same data set as day 5 and its saveed in day 5 file 
dataframe=pd.read_csv("Teen_Mental_Health_Dataset.csv")


#plots
#histogram of ditribiution of stress level 
plot.figure(figsize=(8,5)) #8 inches width 5 inches height 
plot.hist(dataframe["stress_level"],bins=10,color="blue") #its better to use only numeric variable when doing histograms
plot.title("ditribiution of stress level ")
plot.xlabel("stresslevel")
plot.ylabel("count")
plot.savefig("C:/Users/Lenovo/AI-Agents-Internship/day06/screenshots/histogram.png")
plot.show()

#bar plot
#average stress level by gender
plot.figure(figsize=(8,5))
stress_by_gender=dataframe.groupby("gender")["stress_level"].mean()
stress_by_gender.plot(kind="bar",color=["red","blue"])
plot.title("average stress level by gender ")
plot.xlabel("gender")
plot.ylabel("average stress level")
plot.savefig("C:/Users/Lenovo/AI-Agents-Internship/day06/screenshots/barplo.png")
plot.show()


#scatter plot (we have sono many types of scatter)
# (for correlation between two variables mainly before modeling )
#and it can be used to spot outliers, verify linearity ,
#identify sub population ,verify homoscedasticity and to see the model is predicting well the data 
 
#basic
#sleep_hours vs stress_level
plot.figure(figsize=(8,5))
plot.scatter(dataframe["sleep_hours"],dataframe["stress_level"])
plot.title("relation between sleep hours and stress level")
plot.xlabel("sleep_hours")
plot.ylabel("stress_level")
plot.savefig("C:/Users/Lenovo/AI-Agents-Internship/day06/screenshots/scatter.png")
plot.show()
#the scatter above can't tell a lot so lets use seaborn and see 
#if we are able to get a nicer scatter (colored by gender)

plot.figure(figsize=(8, 5))
sns.scatterplot(data=dataframe, x="sleep_hours", y="stress_level", hue="gender")
plot.title("Sleep Hours vs Stress Level by Gender")
plot.savefig("C:/Users/Lenovo/AI-Agents-Internship/day06/screenshots/seaborn_scatter.png")
plot.show()

