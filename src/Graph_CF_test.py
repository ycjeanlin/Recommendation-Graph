import pickle
import operator
import math
import codecs
import time


def load_graph(filename):
    with open(filename, 'rb') as fp:
        W = pickle.load(fp)
    return W


def load_raw_logs(input_file, user_index, POI_index):
    with codecs.open(input_file, 'r') as fr:
        train = {}
        index = 0
        for row in fr:
            cols = row.strip().split('\t')
            index += 1
            if index % 10000 == 0:
                print(index)
            user = cols[user_index]
            item = cols[POI_index]
            if  user not in train:
                train[user] = {}
                train[user][item] = 1

            if item not in train[user]:
                train[user][item] = 1

    return train


def item_phase(graph, node_id):
    pois = graph.neighbors(node_id)
    max_vote = float(len(pois))
    w_pois = {}
    for poi in pois:
        if poi not in w_pois:
            w_pois[poi] = {}
        poi_degree = graph.degree(poi)
        for n in graph.neighbors(poi):
            for new_poi in graph.neighbors(n):
                if poi == new_poi:
                    continue

                if new_poi not in w_pois[poi]:
                    w_pois[poi][new_poi] = 0
                w_pois[poi][new_poi] += 1


def user_phase(graph, node_id):
    pois = graph.neighbors(node_id)
    max_vote = float(len(pois))
    voters = {}
    for poi in pois:
        poi_degree = graph.degree(poi)
        for n in graph.neighbors(poi):
            if n not in voters:
                voters[n] = 0
            voters[n] += math.log(1 + poi_degree)

    scores = {}
    for voter in voters:
        pois = graph.neighbors(voter)
        similarity = voters[voter]
        for poi in pois:
            if poi in scores:
                scores[poi] += similarity / math.sqrt(max_vote * graph.degree(voter))
            else:
                scores[poi] = similarity / math.sqrt(max_vote * graph.degree(voter))

    return scores




if __name__ == '__main__':
    train_file = '../data/SG_foursquare/train.txt'
    graph_file = 'SG.graph'

    user_logs = load_raw_logs(train_file, 0, 1)
    recommend_graph = load_graph(graph_file)
    start_time = time.time()
    for user in user_logs:
        print(user)
        scores = user_phase(recommend_graph, user)
        sorted_scores = sorted(scores.items(), key=operator.itemgetter(1), reverse=True)

    end_time = time.time()
    print("--- %s seconds ---" % (end_time - start_time))


