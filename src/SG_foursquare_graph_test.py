import pickle
import operator
import codecs
from math import radians, cos, sin, asin, sqrt


def haversine(lon1, lat1, lon2, lat2):
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


def user_phase(graph, node_id, time):

    pois = graph.neighbors(node_id)
    max_vote = float(len(pois))
    voters = {}
    for poi in pois:
        for n in graph.neighbors(poi):
            if (graph.node[n]['type'] == 'session' and graph.node[n]['time'] != time) or n == node_id:
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
            if poi in scores:
                scores[poi] += graph[voter][poi]['weight'] * similarity / max_vote
                #scores[poi] += similarity / max_vote
                #scores[poi] += similarity
            else:
                scores[poi] = graph[voter][poi]['weight'] * similarity / max_vote
                #scores[poi] = similarity / max_vote
                #scores[poi] = similarity

    return scores


def session_phase(graph, node_id, time):
    scores = {}

    if node_id+'_'+time in graph.node:
        pois = graph.neighbors(node_id+'_'+time)
        max_vote = float(len(pois))
        voters = {}
        for poi in pois:
            for n in graph.neighbors(poi):
                if graph.node[n]['type'] != 'session' \
                        or (graph.node[n]['type'] == 'session' and graph.node[n]['time'] != time)\
                        or n == node_id +'_'+time:
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
                if poi in scores:
                    scores[poi] += graph[voter][poi]['weight'] * similarity / max_vote
                    #scores[poi] += similarity / max_vote
                    #scores[poi] += similarity
                else:
                    scores[poi] = graph[voter][poi]['weight'] * similarity / max_vote
                    #scores[poi] = similarity / max_vote
                    #scores[poi] = similarity

    return scores

def load_user_logs(log_file):
    print('User logs loading')
    with codecs.open(log_file, 'r') as fr:
        user_logs = {}
        for row in fr:
            cols = row.strip().split('\t')
            user = cols[0]
            for i in range(1, len(cols)):
                encoded_time, POI = cols[i].strip('|').split(',')
                weekday, time = decode_time(int(encoded_time))
                if user in user_logs:
                    if time in user_logs[user]:
                         user_logs[user][time].add(POI)
                    else:
                        user_logs[user][time] = set()
                        user_logs[user][time].add(POI)
                else:
                    user_logs[user] = {}
                    user_logs[user][time] = set()
                    user_logs[user][time].add(POI)

    return user_logs


def load_graph(filename):
    with open(filename, 'rb') as fp:
        graph = pickle.load(fp)
    return graph

if __name__ == '__main__':
    model = 'foursquare_NYC.graph'
    test_file = 'NYC_time_test.dat'

    print('Graph loading')
    foursquare_graph = load_graph(model)

    test_logs = load_user_logs(test_file)

    total = {}
    tp = {}
    tn = {}
    for i in range(24):
        total[str(i)] = 0
        tp[str(i)] = 0
        tn[str(i)] = 0


    for user in test_logs:
        print(user)
        for t in test_logs[user]:

            activities = test_logs[user][t]

            #try:
            user_scores = user_phase(foursquare_graph, user, t)
            session_scores = session_phase(foursquare_graph, user, t)

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
            total[t] += 5
            hit = 0
            for i in range(5):
                #print i, ':', sorted_scores[i][0], sorted_scores[i][1]
                if sorted_scores[i][0] in activities:
                    hit += 1
            tp[t] += hit
            tn[t] += len(activities) - hit

            #print 'Accuracy: ', hit / total
            #except Exception, e:
            #    print str(e)

    print('Precision: ', float(sum(tp.values())) / float(sum(total.values())) / 24.0)
    print('Recall: ', float(sum(tp.values())) / float(sum(tp.values()) + sum(tn.values())) / 24.0)

