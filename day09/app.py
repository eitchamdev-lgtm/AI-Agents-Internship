import streamlit as st 
import joblib
import numpy as np 
import pandas as pd 

model =joblib.load("day09/titanic_model.pkl") #load the model created in the other file 
st.title("Titanic survival predctor ")
st.markdown("enter passenger details to predict survival")




#input------------------------------------------------------------------------

#selectbox is a function that allow the user to select an option (drop down menu)

pclass=st.selectbox("Passenger Class",[1,2,3]) #so if the user select that 
#he want the passenger in the first class st set pclass=1

sex=st.selectbox("Sex",["female","male"])

age=st.slider("Age",1,80,25) #this is a slider bar that allow the user to drag 
#slide left or right to select the age where 1 is the minimum and 80 is the max 
#and 25 is the default age on the slide bar where by defualt the curser is on it 

sibsp = st.slider("Siblings/Spouses on board", 0, 8, 0) #family member 0min 8 max and 0 default
parch = st.slider("Parents/Children on board", 0, 6, 0) #parents and children 0 min 6 max 0 default 

fare = st.number_input("Fare paid", 0.0, 500.0, 32.0) #number input 
#it creat a box that the user can enter numbers inside of it and there is next 
#to it + and - signs to go up or doen with the fare (0 min,500 max,32 default )

port=st.selectbox("Port",["S","C","Q"]) #S for Southampton C for CherbourgQ for Queenstown


#text to number--------------------------------------------------------------
sex_num=0 if sex=="male" else 1
embarked_num = {"S": 0, "C": 1, "Q": 2}[port]



#predict---------------------------------------------------------------------
if st.button("predict survival probability"):
    #put the inputs in 1 row data frame that matches the feature 
    X = pd.DataFrame([[pclass, sex_num, age, sibsp, parch, fare, embarked_num]], 
                     columns=["Pclass", "Sex", "Age", "SibSp", "Parch", "Fare", "Embarked"])
            
    prediction = model.predict(X)[0] #predict using the model that we created 
                                     #and return 0 if dead and 1 if survived

    probability = model.predict_proba(X)[0] #exctract the distribiution probability
                                            #.predict_proba(X) exctract row proba calculated by the model
    st.markdown("____________________")
    if prediction == 1:
        st.success(f" ✅ **passenger survived** ({probability[1]*100:.1f}% statistical confidence)") #p(class(0),class(1)) #is the output of .predict_proba(X)
                                                                                                    #so here che chosprobability[1] because we wanna know for survived the proba

    else:
        st.error(f" ❌ **passenger did not survive.** ({probability[0]*100:.1f}% statistical confidence)")

#ok so here before i do the app with the file upload option only on the same 
#exact titanic data set because it would be easy to test my pipline (file upload app)
#on the data set that i did traained my model on but i thaught it would be 
#limited so why not to create an app where the user can upload any csv file 
#and my ligit model do his work on this model 
#so idk if this would be a better idea i just thaught its better to try it 
#but the only limit of this idea is that the pipline and my model cannot
#identify automatically from a radom data set wich is the dipendet variable 
#(that should be binary too , logit ), and which regressors i have and what is the context 
#of the data set i solved some of these problems by makin the user chose y and x 

#file upload
st.markdown("_________________")
st.header("predictions via csv upload")

upload_file=st.file_uploader("please choose a csv file ",type="csv")
#allow the user to select from their file system a csv file and drag it in the browser 

if upload_file is not None:
    df=pd.read_csv(upload_file)
    st.write("uploaded data preview",df.head()) #st write draw a 
    #scorallable spreadsheet data table 

    all_columns = df.columns.tolist()#let the user select the columns to analyse
    
    st.subheader("configure your model variables") #rend small sixe border to seperate 
    
    dependent_var=st.selectbox("pleas select your binary dipendent variable",all_columns)

    #lets filter the chosen target 
    remaining_columns = [col for col in all_columns if col != dependent_var]
    
    # select multiple Independent Variables (Regressors)
    regressors = st.multiselect(" Choose Independent Variables (Regressors 'X'):", remaining_columns)
    
    st.markdown("---")
    st.header(" Validation & Matrix Split")
    
    # check if the user selected at least one independent feature
    if len(regressors) > 0:
        y = df[dependent_var]    
        X = df[regressors]       

        # Verify if y is s binary (0 and 1)
        # checks that there are exactly 2 unique values and they belong to 0, 1}
        is_binary = y.nunique() == 2 and set(y.unique()).issubset({0, 1})
        
        if is_binary:
            st.success(f"✅ Target variable '**{dependent_var}**' is perfectly binary! Matrix successfully split.")
        
            st.subheader(" Independent Variables Matrix (X)")
            st.write(X.head(3))
            
            st.subheader(" Dependent Target Array (y)")
            st.write(y.head(3))
            
            #  visualizations based on the target distribution
            st.subheader("  class Distribution")
            target_counts = y.value_counts().rename(index={0: "Class 0 (Negative / Died)", 1: "Class 1 (Positive / Survived)"})
            st.bar_chart(target_counts)
            
        else:
            st.error(f"❌ **invalid target selection** The selected column '**{dependent_var}**' contains {y.nunique()} unique values: {list(y.unique())}. Logistic Regression requires a binary only 0 and 1 values.")
            
    else:
        st.warning("action required: please select at least one independent regressor from the multiselect box above to build the feature matrix.")

