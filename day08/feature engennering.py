import pandas as pd
import os
from sklearn.preprocessing import StandardScaler ,LabelEncoder
from sklearn.linear_model import Ridge,Lasso,ElasticNet
from sklearn.model_selection import train_test_split ,GridSearchCV
from sklearn.metrics import r2_score


os.chdir("C:/Users/Lenovo/AI-Agents-Internship/day05")
df = pd.read_csv("Teen_Mental_Health_Dataset.csv") #same dataset as before
print(df.head())


#handle categrial variable as.factor() in r to trasform chr or other type of variable in a dummy
le=LabelEncoder()
df["gender_encoded"]=le.fit_transform(df["gender"]) #create a new variable tha
#assumes 1 if variable gender=male and assume 0 if variable gender =female
print(df[["gender", "gender_encoded"]].head())


#feature scaling scale() in r we use it when variable have diffrent scale of mesurment
#for example we have two variables age that have range from 0 to 100 and stress that
#habe range 1 to 10 so we need to scale them to be able to work with it and do plots
#and make fair comparison (boxplot for example)



x= df[["sleep_hours", "age", "gender_encoded"]] #features
y=df["stress_level"]

scale=StandardScaler()
x_scaled=scale.fit_transform(x)

print("before scaling sleep hours mean:",x["sleep_hours"].mean())
print("after scaling mean:",x_scaled[:, 0].mean().round(5)) #x_scaled is no longer
#a data frame is a matrix [row,col] so x_scaled[:,0] is that i want
#all rows and the first column that is for sleep hours



#_______________________________________________________
#Penalized regression these models are used when we have
# high correlation(coef instabel) or when we have p>n
#numeber of variable>number and whe i have that i will get high variability(it can do ok on training set ) so when i go
#try my model on the test set i will gwt an overfitting problem so i should penalize the variable
#to reduce the errore and the error(mse) has two parts variability and bias so iwand to reduce
#the variability doing bias-variance trade off

x_train, x_test, y_train, y_test = train_test_split(x_scaled, y, test_size=0.2, random_state=42)
# Ridge: the penality ∑βj^2
# (ridge donsent select variable and cant get an coefficient to 0 it used more for correlation problem )
ridge = Ridge(alpha=1.0)
ridge.fit(x_train, y_train)
ridge_pred = ridge.predict(x_test)
print(f"ridge R2: {round(r2_score(y_test, ridge_pred), 3)}")

# Lasso : the penality  ∑∣βj∣
# (it select variables and it can get some coefficients to 0 it used more when we have
# few rilevent variables  )
lasso = Lasso(alpha=0.1)
lasso.fit(x_train, y_train)
lasso_pred = lasso.predict(x_test)
print(f"lasso R2: {round(r2_score(y_test, lasso_pred), 3)}")

#alpha here is the same as lambda in R's glmnet
#we can use elastic net that is a combination of both
# GridSearchCV - find best alpha for Ridge
#is like finding the best lambda in r with k folds cross validation
param_grid = {"alpha": [0.01, 0.1, 1.0, 10.0, 100.0]}
grid_search = GridSearchCV(Ridge(), param_grid, cv=5, scoring="r2")
grid_search.fit(x_train, y_train)
print(f"best alpha: {grid_search.best_params_}")
print(f"best R2: {round(grid_search.best_score_, 3)}") 

#we can use elastic net that combine both lasso and ridge 
elastic = ElasticNet(alpha=0.1, l1_ratio=0.5)  # l1_ratio=0.5 means 50% lasso 50% ridge
elastic.fit(x_train, y_train)
elastic_pred = elastic.predict(x_test)
print(f"elasticnet R2: {round(r2_score(y_test, elastic_pred), 3)}")