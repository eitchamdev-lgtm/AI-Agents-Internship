#traditional class 
class player:
    def __init__(self,name,age,height,position):
        self.name=name 
        self.age=age
        self.height=height
        self.position=position
    def introduce(self):
        print(f"Hello my name is {self.name}, I'm {self.age} years old and I play the {self.position} position")

player1=player("elias",23,190,"point guard")
print(player1.name)
player1.introduce()

#data class
from dataclasses import dataclass
@dataclass
class playerData:
    name:str
    age:int
    height:float
    position:str

player2=playerData("hanna",33,199,"center")
print(player2.name)

#inherited class (takes from class player)
class Professionalplayer(player):
    def __init__(self,name,age,height,position,team,salary):
        super().__init__(name,age,height,position)
        self.team=team
        self.salary=salary

    def contract(self):
        print(f"{self.name} plays for {self.team} and earns ${self.salary}")

pro=Professionalplayer("elias",23,190,"point guard","sagesse",50000)
pro.introduce() #for the player class
pro.contract()  #for professional player class 

try:
    number=int(input("choose a number:"))
    print(10/number)
except ZeroDivisionError:
    print("cannot dovide by 0")
except NameError:
    print("variable not found")
except:
    print("this is an error")
finally:
    print("u will see me no matter what")


try:
    filename=input("please enter the file name")
    with open(filename , "r") as file:
        content=file.read()
        print(content)
except FileNotFoundError :
    print(f"file {filename} not found, please check the correct file name first and try again")



