#1#
#listes 
Teams=["OKC","GSW","SPURS","LAL","INDIANA PEACERS"]
for Team in Teams:
    print(Team.upper())
Teams.append("Bulls")

#dictionary
Me ={"name":"elias","age":23}
print(Me["name"])
#there is also other types of dictionaries:

#1 ordered dict
import collections
d=collections.OrderedDict(one=1,two=2,three=3)
print(d) #keep the keys ordered in the same order that I inseted it in the d
d["four"]=4 #it's equal to append in the list case 

#2 defaultdict 
#is a dictionary that the main diffrence from a normale 
#disctionary  is if i try to access a key that dosen't exist 
#instead of crashing it will automaticly creats it with adefault empty value 

from collections import defaultdict
dd=defaultdict(list) #if the kkey dosent exists create an empty list 
dd["x"].append(1)  #x dosent exists so willl create automaticly dd["x"]=[]
print(dd["x"]) 

#3 chainmap to unifie two or more dictionaries 
from collections import ChainMap
dict1={"one":1,"two":2}
dict2={"three":3,"four":4}
chain=ChainMap(dict1,dict2)
print(chain["three"])
print(chain["one"])

#4 mappingproxytype  read only dictionary 
from types import MappingProxyType
write={"one":1,"two":2}
read=MappingProxyType(write)
print(read["one"]) # to modify or add a key i should do it on the write document 

#functions (basics)
def greet (name):
    return f" Hello,{name}"

print(greet("Elias"))

#function to calculate mean:
def calculate_average(numbers):
    if len(numbers)==0:
        return 0
    total=sum(numbers)
    return total/len(numbers)

list_numbers=[32,45,59,68]
average=calculate_average(list_numbers)
print(f"the avg is {average}")


#file I/O
#read 
with open("output.txt","w") as f:#write
    f.write("file")
print("file created")

with open("output.txt","r") as f:
    content=f.read()
    print(content)





