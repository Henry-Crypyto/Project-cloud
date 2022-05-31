from traceback import FrameSummary
from firebase import firebase

url = 'https://henrydb1-69d3b-default-rtdb.asia-southeast1.firebasedatabase.app/'

fb = firebase.FirebaseApplication(url, None)
text1='Henry'
mtext='@N@Henry'
new_users = [
{'name': text1,'type':1},
{'name': 'Tom Wu','type':1},
{'name': 'Judy Chen','type':0},
{'name': 'Lisa Chang','type':0}
]
for data in new_users:			
	fb.post('/user', data)   
#在user下查詢新增的資料(.get讀取)
users = fb.get('/user', None)  #None全部讀取，1代表讀取第一筆，以此類推
print("資料庫中找到以下的使用者")
user_name=[]
for keysss in users:
       user_name.append(users[keysss]['name'])
usersss=",".join(user_name)
print(usersss)



            
            




fb.put('/管理員/admin', "林好棒", "好帥")
fb.put('/疫調/A班', "王小明", "有足跡重疊")
fb.put('/疫調/B班', "許大明", "無足跡重疊")
fb.put('/疫調/A班', "張小胖", "有足跡重疊")
fb.put('/疫調/B班', "吳小小", "無足跡重疊")

users=fb.get('疫調/A班',None)

print(users)

