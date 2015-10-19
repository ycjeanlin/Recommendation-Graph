import codecs
import pickle
import operator
from math import radians, cos, sin, asin, sqrt
import numpy as np
import matplotlib.pyplot as plt


def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6367 * c
    return km


def decode_time(encoded_time):
    weekday = encoded_time / 24
    time = encoded_time % 24

    return str(weekday), str(time)


def load_poi_logs(input_file, hash_POI_file, user_index, time_index, POI_index, pos_index):
    with codecs.open(input_file, 'r') as fr:
        poi_logs = {}
        POI_position = {}
        index = 0
        for row in fr:
            cols = row.strip().split('\t')
            index += 1
            if index % 10000 == 0:
                print(index)
            poi = cols[POI_index]
            lat, lon = cols[pos_index].split(',')
            POI_position[poi] = (lat, lon)

            if poi not in poi_logs:
                poi_logs[poi] = 0
            poi_logs[poi] += 1

    return poi_logs, POI_position


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
                train[user] = set()

            train[user].add(item)

    return train


def item_phase(graph, node_id):
    users = graph.neighbors(node_id)
    w_pois = {}
    for user in users:
        for p in graph.neighbors(user):
            if p == node_id:
                continue

            if p not in w_pois:
                w_pois[p] = 0.0
            w_pois[p] += 1

    return w_pois


def load_graph(filename):
    with open(filename, 'rb') as fp:
        W = pickle.load(fp)
    return W


if __name__=='__main__':
    graph_file = 'SG.graph'
    test_file = '../data/SG_foursquare/test.txt'
    train_file = '../data/SG_foursquare/train.txt'
    output_file = 'POI_similarity.dat'

    recommend_graph = load_graph(graph_file)
    poi_logs, poi_hash = load_poi_logs('train.txt', 'poi_to_position.dat', 0, -2, 1, 2)
    train_logs = load_raw_logs(train_file, 0, 1)
    test_logs = load_raw_logs(test_file, 0, 1)
    data = []
    with codecs.open(output_file, 'w') as fw:
        for user in test_logs:
            score = {}
            for poi in train_logs[user]:
                lat_poi, lon_poi = poi_hash[poi]
                w_pois = item_phase(recommend_graph, poi)
                num_users = float(recommend_graph.degree(poi))

                visited_pois = recommend_graph.neighbors(user)
                for p in w_pois:
                    if p not in train_logs[user]:
                        lat, lon = poi_hash[p]
                        distance = haversine(float(lat_poi), float(lon_poi), float(lat), float(lon)) * 0.9 + 0.01

                        if p not in score:
                            score[p] = 0.0

                        if num_users * recommend_graph.degree(p) == 0 or distance == 0:
                            print(p, poi, distance)
                        score[p] += w_pois[p] / sqrt(num_users * recommend_graph.degree(p)) / distance

            sorted_pois = sorted(score.items(), key=operator.itemgetter(1), reverse=True)

            fw.write(user)
            hit = 0
            for i in range(len(test_logs[user])):
                if sorted_pois[i][0] in test_logs[user]:
                    hit += 1
                #lat, lon = poi_hash[sorted_pois[i][0]]
                #distance = haversine(float(lat_poi), float(lon_poi), float(lat), float(lon)) * 0.9
                #data.append(distance)
            fw.write('\t' +  str(hit) + '/' + str(len(test_logs[user])) + '\t' + str(float(hit)/len(test_logs[user])))

            fw.write('\n')

    # Choose how many bins you want here
    #num_bins = 100

    # Use the histogram function to bin the data
    #counts, bin_edges = np.histogram(data, bins=range(int(max(data))))

    # Now find the cdf
    #cdf = np.cumsum(counts)

    # And finally plot the cdf
    #plt.plot(bin_edges[1:], cdf)

    #plt.show()
