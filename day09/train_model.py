import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

#titatic data set got it from kaggle 
df=pd.read_csv("day09/train.csv")
print(df.head())
print(df.isnull().sum())   #to check how many missing values we have 

#now we can see that the variables age and cabin and embarked has missing 
#values so we gonna solve that before we start working 
#and i will drop also passenger name since i wanna study survival here (0,1)
#and i will remove also passenger id and ticket because they dont have nothing to do with survival
#in my opinion they are statically non significant for the dipendent variable survived that i wanna study 
#droped also cabin a lot of missing values 

df=df.drop(columns=["Cabin", "Ticket", "Name", "PassengerId"])

#now lets replance missing values in the other variables 
df["Age"] = df["Age"].fillna(df["Age"].median()) #chose median here because it more robust than mean 
df["Embarked"]=df["Embarked"].fillna(df["Embarked"].mode()[0]) # fill with the most common port 

#convert text to factor(numbers) better for machine learning
df["Sex"]=df["Sex"].map({"male": 0, "female": 1})
df["Embarked"]=df["Embarked"].map({"S": 0, "C": 1, "Q": 2})

#now lets choose the regressors and the dipendent variable 
x = df.drop(columns=["Survived"]) 
y = df["Survived"] #binary variable (0/1)


# split data into train and test
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)


#train the model
model=LogisticRegression(max_iter=200)
model.fit(x_train,y_train)

# evaluate
y_pred = model.predict(x_test)
print(f"accuracy: {accuracy_score(y_test, y_pred):.3f}")

# save models
import joblib
joblib.dump(model, "day09/titanic_model.pkl") #this is my model
#saved in binary file so after that stream lit can load it and use it 
print("model saved")


