import pandas as pd
import os

arr = [
    ['1', '2', '3'],
    ['4', '5', '6'],
    ['7', '8',]
]

print(os.getcwd())
print(pd.DataFrame(arr))
df = pd.DataFrame(arr)
df.to_csv(os.getcwd() + "\\test.csv", index=False)