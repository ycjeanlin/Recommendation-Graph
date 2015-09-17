import cPickle
import operator


def decode_time(encoded_time):
    weekday = encoded_time / 24
    time = encoded_time % 24

    return weekday, time


def user_phase(graph, node_id, time):

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
            if poi in scores:
                #scores[poi] += graph[voter][poi]['weight'] * similarity / max_vote
                scores[poi] += similarity / max_vote
                #scores[poi] += 1
            else:
                #scores[poi] = graph[voter][poi]['weight'] * similarity / max_vote
                scores[poi] = similarity / max_vote
                #scores[poi] = 1


    return scores


def session_phase(graph, node_id, time):
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
                if poi in scores:
                    #scores[poi] += graph[voter][poi]['weight'] * similarity / max_vote
                    scores[poi] += similarity / max_vote
                    #scores[poi] += 1
                else:
                    #scores[poi] = graph[voter][poi]['weight'] * similarity / max_vote
                    scores[poi] = similarity / max_vote
                    #scores[poi] = 1

    return scores


def load_graph(filename):
    with open(filename, 'rb') as fp:
        graph = cPickle.load(fp)
    return graph

if __name__ == '__main__':
    model = 'foursquare_SG.graph'
    test_file = 'SG_time_test.dat'

    print 'Graph loading'
    foursquare_graph = load_graph(model)

    query = ''
    print "Enter [node_id] [time]"
    while query != 'exit':
        query = raw_input('Enter:')
        try:
            if query == 'exit':
                break

            user_id, current_time = query.strip().split()

            print '== graph =='
            user_scores = user_phase(foursquare_graph, user_id, current_time)
            session_scores = session_phase(foursquare_graph, user_id, current_time)

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
                print i, ':', sorted_scores[i][0], sorted_scores[i][1]

        except Exception, e:
            print str(e)
            raise
