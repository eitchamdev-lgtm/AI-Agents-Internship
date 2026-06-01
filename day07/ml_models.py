import pandas as pd
import os 
import numpy as np 
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error ,r2_score
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

#same data set as day 5 and day 6 
os.chdir("C:/Users/Lenovo/AI-Agents-Internship/day05")
df=pd.read_csv("Teen_Mental_Health_Dataset.csv")


#features and tanget :now we want to choose the predictor x(regressor)
# and see what effet havethis predictor on the target (y) dependent variable

x=df[["sleep_hours"]] #predictor
y=df["stress_level"] #target

## train/test split (80% train, 20% test) this random train test split 
#we can use also leave one out coross validation or k-folds
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
#randome state=42 equale set.seed(42) in r 

print(f"train size: {x_train.shape[0]}")
print(f"test size: {x_test.shape[0]}")


#train linear regression model >> ml( ) in r
model=LinearRegression()
model.fit(x_train,y_train)

#lets see the coefficiets (like summary in r)
print(f"intercept: {model.intercept_:.2f}")  #intercp is mean(y) when all regressor/predictors are =0
print(f"coefficient (slope): {model.coef_[0]:.2f}") #marginal effect of the prector on the mean(y) when all 
#other predictors are equal
#i will not interpret here the results and what does it mean in this context 

#prection on test set 
y_pred=model.predict(x_test)
print(f"r2 score:{r2_score(y_test, y_pred):.2f}") #r2 mesure the proportion of variation in the dipendent variable 
#that the model can explain (here its negative so the model is wors than mean(y))
print(f"mse: {mean_squared_error(y_test, y_pred):.2f}")   # mean squared error

#____________________________________________________________________________________________________
#now lets add multiple predictors to elevate r2 (note:r2 qill get elevated when we add variables x
#even if those variable are not statisticallt significant sow i prefere always to 
#evaluate the model with adjusted r2 becaus it allows me too to compare 2 models with different number of predictors)
def adjusted_r2(r2, n, k):
    return 1 - (1 - r2) * (n - 1) / (n - k - 1)

x2= df[["sleep_hours", "daily_social_media_hours", "screen_time_before_sleep", "physical_activity"]]
x2_train, x2_test, y_train, y_test = train_test_split(x2, y, test_size=0.2, random_state=42)
model2 = LinearRegression()
model2.fit(x2_train, y_train)
y_pred2 = model2.predict(x2_test)
r2_2 = r2_score(y_test, y_pred2)
print("\n model predictors")
print(f"r2: {r2_2:.2f}")
print(f"adjusted r2: {adjusted_r2(r2_2, len(y_test), 4):.2f}")
print(f"mse: {mean_squared_error(y_test, y_pred2):.2f}")
#still negative r2 it just means this dataset is synthetic/randomly generated and the variables have no real linear relationship with stress level

#______________________________________________________________________________
#logistic regression : is a regression where the dependet variable is 
#binary (0;1) not numeric as the example before so here were not in a lineare 
#regression and the y in logistic regression follow a bernoulli with pi probbility 
#of success and this pi is connectected with the regressor using an logistic random variable 

x_log = df[["sleep_hours", "stress_level", "anxiety_level", "addiction_level"]]
# like ifelse(stress_level > 4, 1, 0) in r
y_log = (df["stress_level"] > 4).astype(int) #because the y should be binary in logidtic model
x_log_train, x_log_test, y_log_train, y_log_test = train_test_split(x_log, y_log, test_size=0.2, random_state=42)
log_model = LogisticRegression()
log_model.fit(x_log_train, y_log_train)
y_log_pred = log_model.predict(x_log_test)
print("_logistic reg_")
print(f"accuracy: {accuracy_score(y_log_test, y_log_pred):.2f}")


#bomus multinomialbecaus its related to logit multimial is an extention of logit 
#where y is a categorial variable y=(1,2,3,4) and where every category 
#in a binnary logistic variables so here we have 4 categories so 4 logit 

x_multi = df[["sleep_hours", "daily_social_media_hours", "anxiety_level", "addiction_level"]]
y_multi = pd.cut(df["stress_level"], 
                 bins=[0, 3, 6, 8, 10], 
                 labels=[1, 2, 3, 4])
x_multi_train, x_multi_test, y_multi_train, y_multi_test = train_test_split(x_multi, y_multi, test_size=0.2, random_state=42)

multi_model = LogisticRegression( max_iter=1000)
multi_model.fit(x_multi_train, y_multi_train)
y_multi_pred = multi_model.predict(x_multi_test)

print("multinom reg")
print(f"accuracy: {accuracy_score(y_multi_test, y_multi_pred):.2f}")

#we can also build here a confiusion matrix for the logitic model if we wanted to 
#ps: we could do the model without spliting so like that we will be consedering the 
#entire dataset as a training test but we could risk overfitting