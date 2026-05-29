#i will recreat(not exactly ) a couple of plots that i did in r 
#it qill not be the best plot i did i r because the data set won't allow me to do that 
#but the could be a good exaple for data visualation for regression models
#(i will not interpret the results statistically)
import matplotlib.pyplot as plot
import seaborn as sns
import pandas as pd 
import os 

os.chdir("C:/Users/Lenovo/AI-Agents-Internship/day05")
dataframe=pd.read_csv("Teen_Mental_Health_Dataset.csv")
#regression plot bwtween stress level and hours of sleep
#show the lineare relationship and confidence level

plot.figure(figsize=(10,6))
sns.regplot(data=dataframe,x="sleep_hours", y="stress_level",
            scatter_kws={"alpha": 0.4, "color": "steelblue"},
            line_kws={"color": "red", "linewidth": 2})
plot.title("does less sleep=more stress?")
plot.xlabel("sleep hours")
plot.ylabel("stress level")
plot.savefig("C:/Users/Lenovo/AI-Agents-Internship/day06/screenshots/regplot.png")
plot.show()


#correlation heatmap (all numeric variable)=correlation matrix in r (corr(df))
plot.figure(figsize=(10,6))
sns.heatmap(dataframe.select_dtypes(include="number").corr(),
            annot=True #to show the numer
            ,cmap="coolwarm") #red=positive,blue=negative
plot.title("correlation between all numeric variables", fontsize=16)
plot.savefig("C:/Users/Lenovo/AI-Agents-Internship/day06/screenshots/heatmap.png")
plot.show()



