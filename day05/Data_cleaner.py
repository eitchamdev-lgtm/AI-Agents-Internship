#class datacleaner just trying to apply it data cleaning
#and data structur and data fitlring and grouping and selcting 
#all the explanation of the syntax are in pandasbasics.py


import pandas as pd
import os
from loguru import logger

class DataCleaner:
    def __init__(self, filepath):
        os.chdir("C:/Users/Lenovo/AI-Agents-Internship/day05")
        self.df = pd.read_csv(filepath)
        logger.info("dataset loaded!")

    def inspect(self):
        print("shape:", self.df.shape)
        print("types:\n", self.df.dtypes)

    def clean(self):
        self.df.fillna(self.df.select_dtypes(include="number").mean(), inplace=True)
        logger.success("cleaned")

    def filter_data(self):
        high_stress = self.df[self.df["stress_level"] > 3]
        print("high stress teens:", high_stress.shape[0])
        females = self.df[self.df["gender"] == "Female"]
        print("female teens:", females.shape[0])
        stress_and_sleep = self.df[(self.df["stress_level"] > 3) & (self.df["sleep_hours"] < 6)]
        print("high stress and poor sleep:", stress_and_sleep.shape[0])

    def select_columns(self):
        numeric = self.df.select_dtypes(include="number")
        print("numeric columns:", numeric.columns.tolist())
        manual = self.df[["age", "gender", "stress_level"]]
        print("manual selection:\n", manual.head())

    def group_data(self):
        by_gender = self.df.groupby("gender")["stress_level"].mean()
        print("stress by gender:\n", by_gender)
        by_platform = self.df.groupby("platform_usage")["sleep_hours"].mean()
        print("slwep by platform:\n", by_platform)

    def run(self):
        self.inspect()
        self.clean()
        self.filter_data()
        self.select_columns()
        self.group_data()


cleaner = DataCleaner("Teen_Mental_Health_Dataset.csv")
cleaner.run()

#its useful to have class that clean this data set because 
#if i wanna work on this data set again i shoulds rewrite all the code 

#and then if i wanna do other things(like filtring or grouping ) by other conditions 
#that exist in this data set i can add it easily 
