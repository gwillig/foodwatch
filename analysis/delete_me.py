n = int(input())
arr = map(int, input().split())

arr = [2, 3, 6, 6, 5]
arr_raw = "57 57 -57 57"
arr_list = arr_raw.split(" ")
arr_proc = list(map(lambda x: int(x), arr_list))

'#1.Step: Define all variables'


'#2.Step: Loop through arr to find highest numb'
highest = -101
for el in arr:
    if el > highest:
        highest = el

'#3.Step: Remove highest number'
new_arr = list(filter(lambda x: x!= highest,arr))

'#3.1Step: Loop through arr to find highest numb'
runner = -101
for el in new_arr:
    if el > runner:
        runner=el
print(runner)