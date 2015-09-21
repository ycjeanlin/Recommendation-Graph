import pickle
from math import radians, cos, sin, asin, sqrt
import codecs
import operator


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
    return km * 1000

def load_graph(filename):
    with open(filename, 'rb') as fp:
        graph = pickle.load(fp)
    return graph


def load_hash_file(hash_file):
    hash_table = {}

    with codecs.open(hash_file, 'r') as fr:
        for row in fr:
            cols = row.strip().split('\t')
            position = [float(x) for x in cols[1].split(',')]
            hash_table[cols[0]] = (position[0], position[1])

    return hash_table


def user_phase(graph, node_id, time, lat, lon, poi_hash):

    pois = graph.neighbors(node_id)
    max_vote = float(len(pois))
    voters = {}
    for poi in pois:
        for n in graph.neighbors(poi):
            if graph.node[n]['type'] == 'session' and graph.node[n]['time'] != time:
                continue
            else:
                if n in voters:
                    voters[n] += 1
                else:
                    voters[n] = 1

    scores = {}
    for voter in voters:
        pois = graph.neighbors(voter)
        similarity = voters[voter]
        for poi in pois:
            poi_lat, poi_lon = poi_hash[poi]
            distance = haversine(lat, lon, poi_lat, poi_lon)
            if distance == 0:
                distance = 1

            if poi in scores:
                #scores[poi] += graph[voter][poi]['weight'] * similarity / max_vote
                #scores[poi] += similarity / max_vote
                scores[poi] += 1 / distance
            else:
                #scores[poi] = graph[voter][poi]['weight'] * similarity / max_vote
                #scores[poi] = similarity / max_vote
                scores[poi] =  1 / distance


    return scores


def session_phase(graph, node_id, time, lat, lon, poi_hash):
    scores = {}

    if node_id+'_'+time in graph.node:
        pois = graph.neighbors(node_id+'_'+time)
        max_vote = float(len(pois))
        voters = {}
        for poi in pois:
            for n in graph.neighbors(poi):
                if graph.node[n]['type'] != 'session' or (graph.node[n]['type'] == 'session' and graph.node[n]['time'] != time):
                    continue
                else:
                    if n in voters:
                        voters[n] += 1
                    else:
                        voters[n] = 1

        for voter in voters:
            pois = graph.neighbors(voter)
            similarity = voters[voter]
            for poi in pois:
                poi_lat, poi_lon = poi_hash[poi]
                distance = haversine(lat, lon, poi_lat, poi_lon)
                if distance == 0:
                    distance = 1

                if poi in scores:
                    #scores[poi] += graph[voter][poi]['weight'] * similarity / max_vote
                    #scores[poi] += similarity / max_vote
                    scores[poi] += 1 / distance
                else:
                    #scores[poi] = graph[voter][poi]['weight'] * similarity / max_vote
                    #scores[poi] = similarity / max_vote
                    scores[poi] = 1 / distance

    return scores


if __name__ == '__main__':
    model = 'SG_foursquare.graph'
    test_file = 'SG_time_test.dat'

    print('Graph loading')
    foursquare_graph = load_graph(model)

    print('POI to position')
    poi_position =  load_hash_file('poi_to_position.dat')

    query = ''
    print('Enter [node_id] [time]')
    while query != 'exit':
        query = input('Enter:')
        try:
            if query == 'exit':
                break

            user_id, current_time, location = query.strip().split()
            latitude, longitude = poi_position[location]
            print('== graph ==')
            user_scores = user_phase(foursquare_graph, user_id, current_time, latitude, longitude, poi_position)
            session_scores = session_phase(foursquare_graph, user_id, current_time, latitude, longitude, poi_position)

            poi_scores = {}
            if len(session_scores) > 0:
                for poi in user_scores:
                    if poi in session_scores:
                        poi_scores[poi] = user_scores[poi] + session_scores[poi]
                    else:
                        poi_scores[poi] = user_scores[poi]
            else:
                poi_scores = user_scores

            sorted_scores = sorted(poi_scores.items(), key=operator.itemgetter(1), reverse=True)
            for i in range(5):
                print(i, ':', sorted_scores[i][0], sorted_scores[i][1])

        except Exception as e:
            print(str(e))
            raise