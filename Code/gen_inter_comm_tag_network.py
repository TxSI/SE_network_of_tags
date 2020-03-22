 import sys, os
import csv
import networkx as nx
import community
import xmltodict
from tqdm import tqdm
from matplotlib import pyplot as plt
from matplotlib_venn import venn3, venn3_circles

def gen_network():
    '''
    time_windows:  3month   2019-03-04 --- 2019-06-04  ---  2019-09-04
                   6month   2018-09-04 --- 2019-03-04  ---  2019-09-04
                   annually 2017-09-04 --- 2018-09-04 ---  2019-09-04
    '''

    graph = nx.Graph()
    base_path = "/Volumes/BigMatch/StackExchange_dump_04SEPT2019/stackexchange/"
    # top 10 popular
    # communities = ["electronics", "unix", "math", "askubuntu",
    #                 "codereview",  "physics", "stackoverflow",
    #                 "serverfault", "stats", "superuser"]
    # 9 relevant
    communities = ["datascience", "softwareengineering", "ux",
                    "cs", "stackoverflow",  "opendata", "ai","iot", "devops"]
    for community in communities:
        posts_path = base_path+community+"/"+os.listdir(base_path+community)[0]+"/posts.xml"
        print("Proceeding with: ", community)
        fin = open(posts_path, mode="r", encoding='utf-8')
        error_cnt = 0
        for line in tqdm(fin):
            try:
                post = xmltodict.parse(line)['row']
                # print(post['Tags'], post['CreationDate'])
                if "Tags" in post and "CreationDate" in post:
                    if post['CreationDate'] < "2017-09-04": #skip posts older than two years
                        continue
                    tags = post['Tags'][1:-1].replace("><", " ").split(" ")
                    if len(tags) > 1:
                        for i in range(0, len(tags)):
                            # add note(tag) attributes
                            if tags[i] not in graph.node:
                                graph.add_node(tags[i], last_3month=0, this_3month=0,
                                        last_6month=0,
                                        this_6month=0,
                                        last_year=0,
                                        this_year=0
                                        )
                            # print(graph.node[tags[i]]['last_year'])
                            # exit()
                            # Update attributes
                            if post['CreationDate'] < "2018-09-04":
                                graph.node[tags[i]]['last_year'] += 1
                            else:
                                graph.node[tags[i]]['this_year'] += 1

                                if post['CreationDate'] < "2019-03-04" :
                                    graph.node[tags[i]]['last_6month'] += 1
                                else:
                                    graph.node[tags[i]]['this_6month'] += 1

                                    if post['CreationDate'] < "2019-06-04":
                                        graph.node[tags[i]]['last_3month'] += 1
                                    else:
                                        graph.node[tags[i]]['this_3month'] += 1

                            for j in range(i+1, len(tags)):
                                if tags[j] not in graph.node:
                                    graph.add_node(tags[j], last_3month=0, this_3month=0,
                                        last_6month=0,
                                        this_6month=0,
                                        last_year=0,
                                        this_year=0
                                        )
                                if graph.has_edge(tags[i], tags[j])==False:
                                    # Instantiate attributes
                                    graph.add_edge(tags[i], tags[j])
                                    graph[tags[i]][tags[j]]['weight'] = 1
                                else:
                                    graph[tags[i]][tags[j]]['weight'] += 1

            except Exception as e:

                print("ERROR", error_cnt, e)
                error_cnt += 1
        # break
        fin.close()

    nx.write_gexf(graph, "inter_comm_tags_popularity_change.gexf")


def gen_all_tags_csv():
    base_path = "/Volumes/BigMatch/StackExchange_dump_04SEPT2019/stackexchange/"
    communities = ["datascience", "softwareengineering", "ux",
                    "cs", "stackoverflow",  "opendata", "ai","iot", "devops"]
    fout_csv = open("SE_network_of_tags/tag_comm_date.csv", mode='w')
    with fout_csv:
        writer = csv.writer(fout_csv)
        for community in communities:
            posts_path = base_path+community+"/"+os.listdir(base_path+community)[0]+"/posts.xml"
            print("Proceeding with: ", community)
            fin = open(posts_path, mode="r", encoding='utf-8')
            for line in tqdm(fin):
                try:
                    post = xmltodict.parse(line)['row']
                    if 'Tags' in post and "CreationDate" in post:
                        tags = post['Tags'][1:-1].replace("><", " ").split(" ")
                        for tag in tags:
                            writer.writerow([tag, community, post['CreationDate']])
                except:
                    pass

def get_ratio(a1, a0):
    return max(1.0, 100.0*(a1-a0)/max(a0, 1))
def post_process_graph():
    graph = nx.read_gexf("inter_comm_tags_popularity_change.gexf")
    print('Network loaded. Partitioning...')
    partition = community.best_partition(graph)
    print('Partitioning is finished.')
    nx.set_node_attributes(graph, partition, 'modularity_class')
    '''UPDATE DEGREE'''
    for tag in tqdm(graph.nodes):
        graph.node[tag]['change'] = get_ratio(graph.node[tag]['this_3month'], graph.node[tag]['last_3month'])
    nx.write_gexf(graph, "ic_tags_popularity_change_quarterly.gexf")

    for tag in tqdm(graph.nodes):
        graph.node[tag]['change'] = get_ratio(graph.node[tag]['this_6month'], graph.node[tag]['last_6month'])
    nx.write_gexf(graph, "ic_tags_popularity_change_semi_annually.gexf")

    for tag in tqdm(graph.nodes):
        graph.node[tag]['change'] = get_ratio(graph.node[tag]['this_year'], graph.node[tag]['last_year'])
    nx.write_gexf(graph, "ic_tags_popularity_change_annually.gexf")

def filter_graph(limit=1000, path="", top_pop_n=50):
    # This method filters the graph's top nodes sorted by 'change' field's value
    graph = nx.read_gexf(path)
    top_popular = sorted(graph.nodes, reverse=True, key= lambda t: graph.node[t]['last_year'])[:top_pop_n]

    for tag in tqdm(graph.nodes):
        for attr in ['last_3month','this_3month','last_6month','this_6month','last_year','this_year']:
            del graph.node[tag][attr]
    sorted_tags = sorted(graph.nodes, key=lambda x: -graph.node[x]['change'])
    tags_to_filter = [t for t in sorted_tags[limit:] if t not in top_popular]
    graph.remove_nodes_from(tags_to_filter)
    nx.write_gexf(graph, path.split('.gex')[0]+"lim"+str(limit)+".gexf")
    print('Done', path.split('.gex')[0]+"lim"+str(limit)+".gexf")

def plot_tag_venns():
    distinct_tags_path = "distinct_tags/"
    all_communities = {}
    for com_tags in os.listdir(distinct_tags_path):
        if com_tags.startswith("."):
            continue
        fin = open(distinct_tags_path+com_tags, mode='r')
        all_communities[com_tags[13:-4]] = set([tag.replace("\n","") for tag in fin])
        # print(com_tags[13:-4], len(all_communities[com_tags[:-4]]))
    # print(all_communities)
    labels = list(all_communities)
    for i in range(0, len(labels)):
        for j in range(i+1, len(labels)):
            for k in range(j+1, len(labels)):
                set1 = all_communities[labels[i]]
                set2 = all_communities[labels[j]]
                set3 = all_communities[labels[k]]
                venn3([set1, set2, set3], (labels[i],labels[j],labels[k]))

        # plt.show()
                plt.savefig(distinct_tags_path+"-".join([labels[i],labels[j],labels[k]]))
                plt.cla()
                plt.clf()


def get_intersections():
    distinct_tags_path = "distinct_tags/"
    all_communities = {}
    for com_tags in os.listdir(distinct_tags_path):
        if not com_tags.endswith(".txt"):
            continue
        fin = open(distinct_tags_path+com_tags, mode='r')
        all_communities[com_tags[13:-4]] = set([tag.replace("\n","") for tag in fin])

    #print(set(all_communities))
    print(set(all_communities['unix']).intersection(set(all_communities['math'])))


def gen_network_samples():
    subgraph = nx.read_gexf("inter_comm_post_tags.gexf")
    edges = list(subgraph.edges)
    (lower_thresh, higher_thresh) = (50, 100) #max_higher = 538082
    for (u, v) in edges:
        if (u, v) not in subgraph.edges:
            continue
        if subgraph[u][v]['weight_total'] < lower_thresh or  subgraph[u][v]['weight_total'] > higher_thresh:
            subgraph.remove_edge(u, v)

    partition = community.best_partition(subgraph)
    nx.set_node_attributes(subgraph, partition, 'modularity_class')

    nx.write_gexf(subgraph, "sub_networks/ICTags_{}_{}_{}n_{}e.gexf".format(lower_thresh, higher_thresh,
                                                            len(subgraph.nodes), len(subgraph.edges)))
# gen_network()
# post_process_graph()
for l in [5000]:
    filter_graph(limit=l, path="sub_networks/ic_tags_popularity_change_quarterly.gexf")
    filter_graph(limit=l, path="sub_networks/ic_tags_popularity_change_semi_annually.gexf")
    filter_graph(limit=l, path="sub_networks/ic_tags_popularity_change_annually.gexf")
# plot_tag_venns()
# get_intersections()
# gen_network_samples()
# gen_all_tags_csv()





