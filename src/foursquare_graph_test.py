import cPickle
import operator


def decode_time(encoded_time):
    weekday = encoded_time / 24
    time = encoded_time % 24

    return weekday, time


def user_phase(graph, node_id, time):

    pois = graph.neighbors(node_id)
    max_vote = len(pois)
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
            if poi in scores:
                scores[poi] += graph[voter][poi]['weight'] * similarity / max_vote
            else:
                scores[poi] = graph[voter][poi]['weight'] * similarity / max_vote

    return scores


def session_phase(graph, node_id, time):
    scores = {}

    if node_id+'_'+time in graph.node:
        pois = graph.neighbors(node_id+'_'+time)
        max_vote = len(pois)
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
                if poi in scores:
                    scores[poi] += graph[voter][poi]['weight'] * similarity / max_vote
                else:
                    scores[poi] = graph[voter][poi]['weight'] * similarity / max_vote

    return scores


def load_user_logs(log_file):
    print 'Log loading'
    with codecs.open(log_file, 'r') as fr:
        user_logs = {}
        for row in fr:
            cols = row.strip().split('\t')
            user = cols[0]
            for i in range(1, len(cols)):
                encoded_time, POI = cols[i].strip('()').split(',')
                if user in user_logs:
                    user_logs[user].append((encoded_time, POI))
                else:
                    user_logs[user] = []
                    user_logs[user].append((encoded_time, POI))

    return user_logs


def load_graph(filename):
    with open(filename, 'rb') as fp:
        graph = cPickle.load(fp)
    return graph

if __name__ == '__main__':
    model = 'foursquare.graph'
    test_file = 'NYC_time_test.dat'

    print 'Graph loading'
    foursquare_graph = load_graph(model)

    test_logs = load_user_logs(test_file)

    total = 0.0
    hit = 0.0
    for user in test_logs:
        print user
        for t in test_logs[user]:
            total += 1
            encoded_time, target_poi = t
            current_weekday, current_time = decode_time(int(encoded_time))

            try:
                user_scores = user_phase(foursquare_graph, user, current_time)
                session_scores = session_phase(foursquare_graph, user, current_time)

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
                for i in range(1):
                    print i, ':', sorted_scores[i][0], sorted_scores[i][1]
                    if sorted_scores[i][0] == target_poi:
                        hit += 1

                print 'Accuracy: ', hit / total
            except Exception, e:
                print str(e)
