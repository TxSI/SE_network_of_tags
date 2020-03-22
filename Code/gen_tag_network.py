from dbm import DBM
import networkx as nx

db = DBM()
db2 = DBM()
post_filter = {'@CreationDate' : {'$gt':'2019'}}
post_filter = {}
# post_filter = {'@Tags' : {'$type':'string', '$not':{'$type':'array'}}}

posts = db.get_post(post_filter)

graph = nx.Graph()
# cnt = 0
# for post in posts:
#     if cnt%100==0:
#         print(cnt, post['@Tags'])
#     cnt += 1
#     tags = post['@Tags'][1:-1].replace("><", " ").split(" ")
#     # print(tags)
#     post['@Tags'] = tags
#     update = { "$set": {"@Tags": tags} }
#     db2.update_post({'_id':post['_id']}, update)

cnt = 0
for post in posts:
    if '@Tags' not in post or type(post['@Tags'])==type(""):
        continue
    tags = post['@Tags']
    cnt += 1
    if cnt%10000==0:
        print(cnt, tags)
        break
    if len(tags) > 1:
        for i in range(0, len(tags)):
            for j in range(i, len(tags)):
                if graph.has_edge(tags[i], tags[j]):
                    graph[tags[i]][tags[j]]['weight'] += 1
                else:
                    graph.add_edge(tags[i], tags[j], weight=1)

nx.write_gexf(graph, "tags_10.000_posts.gexf")



#gefx.jx
