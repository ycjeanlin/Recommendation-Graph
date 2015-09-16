import codecs
import cPickle
import operator


def load_user_logs(log_file):
    #logs loading
    fr = codecs.open(log_file, 'r', encoding = 'utf-8')
    rows = fr.readlines()
    fr.close()

    user_logs = {}
    for row in rows:
        cols = row.strip().split()
        user = cols[0]
        for i in range(1, len(cols)):
            time, cat = cols[i].strip('()').split(',')
            if user_logs.has_key(user):
                if user_logs[user].has_key(time):
                    user_logs[user][time].append(cat)
                else:
                    user_logs[user][time] = []
                    user_logs[user][time].append(cat)
            else:
                user_logs[user] = {}
                user_logs[user][time] = []
                user_logs[user][time].append(cat)

    return user_logs

def load_user_preference(preference_file):
    #logs loading
    fr = codecs.open(preference_file, 'r', encoding = 'utf-8')
    rows = fr.readlines()
    fr.close()

    user_preference = {}
    for row in rows:
        cols = row.strip().split()
        user = cols[0]
        for i in range(1, len(cols)):
            cat, count = cols[i].strip('()').split(',')
            if user_preference.has_key(user):
                user_preference[user][cat] = int(count)
            else:
                user_preference[user] = {}
                user_preference[user][cat] = int(count)


    return user_preference

def user_phase(graph, node_id, time):
    scores = {}

    cats = graph.neighbors(node_id)
    max_vote = len(cats)
    voters = {}
    for cat in cats:
        for n in graph.neighbors(cat):
            if graph.node[n]['type'] == 'session' and graph.node[n]['time'] != time:
                continue
            else:
                if voters.has_key(n):
                    voters[n] += 1
                else:
                    voters[n] = 1
        

    for voter in voters:
        cats = graph.neighbors(voter)
        similarity = voters[voter]
        for cat in cats:
            if scores.has_key(cat):
                scores[cat] += graph[voter][cat]['weight'] * similarity / max_vote
            else:
                scores[cat] = graph[voter][cat]['weight'] * similarity / max_vote

    return scores

def session_phase(graph, node_id, time):
    scores = {}

    if graph.node.has_key(node_id+'_'+time):
        cats = graph.neighbors(node_id+'_'+time)
        max_vote = len(cats)
        voters = {}
        for cat in cats:
            for n in graph.neighbors(cat):
                if graph.node[n]['type'] != 'session' or (graph.node[n]['type'] == 'session' and graph.node[n]['time'] != time):
                    continue
                else:
                    if voters.has_key(n):
                        voters[n] += 1
                    else:
                        voters[n] = 1
            
        for voter in voters:
            cats = graph.neighbors(voter)
            similarity = voters[voter]
            for cat in cats:
                if scores.has_key(cat):
                    scores[cat] += graph[voter][cat]['weight'] * similarity / max_vote
                else:
                    scores[cat] = graph[voter][cat]['weight'] * similarity / max_vote

    return scores

def load_graph(filename):
    with open(filename, 'rb') as fp:
        graph = cPickle.load(fp)
    return graph

if __name__ == '__main__':
    model = 'foursquare.graph'

    print 'Graph loading'
    foursquare_graph = load_graph(model)
