import pandas as pd 
import os 
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

os.chdir("C:/Users/Lenovo/AI-Agents-Internship/day05")
df=pd.read_csv("Teen_Mental_Health_Dataset.csv")

class prediction_pipeline:
    def __init__(self,model):
        self.model=model    #here i can pass any model i want (ridge,lasso,ecc...)
        self.scaler=StandardScaler()  #to get all the variable on the same scale like scale() in r
    
    def fit(self,x,y):
        x_scaled=self.scaler.fit_transform(x)
        self.model.fit(x_scaled,y)   #train set 

    def predict(self,x):
        x_scaled=self.scaler.transform(x)
        return self.model.predict(x_scaled)  #predict 
    
    def score (self,x,y):
        predc =self.predict(x)
        return round(r2_score(y,predc),3) #evaluation of my prediction (evaluation of my model)
    


#let's test it 
x=df[["sleep_hours","age"]]
y=df["stress_level"]

x_train,x_test,y_train,y_test=train_test_split(x,y,test_size=0.2,random_state=50)
pipeline = prediction_pipeline(Ridge())
pipeline.fit(x_train, y_train)
print(f"pipeline R2: {pipeline.score(x_test, y_test)}") #score call predict and passes x_test into it 