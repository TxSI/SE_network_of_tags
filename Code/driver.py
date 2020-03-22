from dbm import DBM
from xml.dom import minidom
import xmltodict
import requests
import time

def load_posts(path):
    dbm = DBM()
    fin = open(path, mode='r', encoding='utf-8')
    dcnt = 1
    for line in fin:
        try:
            post = xmltodict.parse(line)['row']
            # print(post)
            dbm.add_post(post)
            # print(post)
        except:
            print("ERROR")
            print(post)

        if dcnt > 1000000:
            dcnt = 1
            del dbm
            dbm = DBM()

def load_users(path):
    dbm = DBM()
    fin = open(path, encoding='utf-8', mode='r')
    cnt = 1
    for line in fin:
        cnt += 1
        try:
            user = xmltodict.parse(line)['row']
            dbm.add_user(user)
            print(cnt)
        except:
            print("ERROR")
            print(line)


#load posts to mongodb
# load_posts(path="data/stackoverflow/posts.xml")

#load users to mongodb
# load_users(path="data/stackoverflow/posts.xml")

#set db indexes to speed up queries
# dbm = DBM()
# dbm.db.posts.create_index([('@CreationDate', 1),
#                             ('@OwnerUserId', 1)])
# dbm.db.users.create_index([('@Id', 1)])

#Set post's creation location && refactor tags/Id
# conn1 = DBM()
# conn2 = DBM()
# cnt = 0
# for post in conn1.get_post():
#     if cnt < 42000000:
#         cnt += 1
#         print(cnt)
#         continue
#     if '@Tags' in post and '@OwnerUserId' in post:
#         tags = post['@Tags']
#         if type(tags) != type(list()):
#             tags = tags.replace('<', '')\
#                         .replace('>', ' ')\
#                         .split()
#         else:
#             continue
#         owner_id = post['@OwnerUserId']
#         owner = conn2.get_user({'@Id':owner_id})[0]
#         if '@Location' not in owner or owner['@Location']=="":
#             continue
#         owner_location = owner['@Location']

#         update = { "$set": { "@OwnerLocation": owner_location, "@Tags": tags} }
#         conn2.update_post({'_id':post['_id']}, update)

#         # print(owner_id)
#         # exit()
#         cnt += 1
#         if cnt%1000 == 0:
#             print(cnt, owner_id, owner_location, tags)
#     # print(post)




