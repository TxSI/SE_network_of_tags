from dbm import DBM
from tqdm import tqdm
'''
This script assigns a set of tags to every user based on their interactions.
'''

db = DBM()
upd_handler = DBM()
#The following line adds a '@Tags' attribute to each user doc
# db.db.users.update({}, {'$set':{'@Tags':[]}}, upsert=False, multi=True)

def append_tags(user_id, tags):
    '''
    This method appends a set of tags to a specific user's list of tags.
    '''
    upd_handler.db.users.update(
       { '@Id': user_id },
       { '$push': { '@Tags': { '$each': tags } } })

def tags_list_to_dict(user):
    if '@Id' not in user or '@Tags' not in user:
        return
    tag_dict = {}
    for tag in user['@Tags']:
        if tag not in tag_dict:
            tag_dict[tag] = 1
        else:
            tag_dict[tag] += 1

    upd_handler.db.users.update(
       { '@Id': user['@Id'] },
       { '$set': { '@Tags': tag_dict}})

# Iterate overall posts; append the post-tags to the owner user's prof
# for post in tqdm(db.get_post()):
#     if '@OwnerUserId' in post and '@Tags' in post:
#         append_tags(post['@OwnerUserId'], post['@Tags'])


# Iterate overall users; convert their list of tags to a freq-dist
for user in tqdm(list(db.get_user({'@Tags.1': {'$exists':True}}))):
    tags_list_to_dict(user)
