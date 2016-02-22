import codecs
import pickle
import datetime


def load_raw_logs(input_file, session_index, item_index):
    '''
    load yoochoose-clicks.dat and yoochoose-buys.dat into a list of each session
    :param input_file: yoochoose-clicks.dat or yoochoose-buys.dat
    :param session_index: the index of the session id of a row in the data file
    :param item_index: the index of the item id of a row in the data file
    :return logs: lists of click logs divided by sessions
    '''
    with codecs.open(input_file, 'r') as fr:
        logs = {}
        index = 0
        for row in fr:
            cols = row.strip().split(',')
            index += 1
            if index % 1000000 == 0:
                print(index)
            session = cols[session_index]
            item = cols[item_index]
            if  session not in logs:
                logs[session] = []
            logs[session].append(item)
            '''
            if len(logs[session]) > 0:
                if logs[session][-1] != item:
                    logs[session].append(item)
            else:
                logs[session].append(item)
            '''
    return logs


def load_item_cat():
    item_cat = {}
    with codecs.open('../data/yoochoose/item_cat.txt', 'r') as fr:
        for row in fr:
            cols = row.strip().split(',')
            item_cat[cols[0]] = cols[1]

    return item_cat


def cal_popularity(train_file, item_index):
    popularity = {}
    with codecs.open(train_file, 'r') as fr:
        index = 0
        for row in fr:
            index += 1
            if (index % 100000) == 0:
                print(index)
            cols = row.strip().split(',')

            item = cols[item_index]

            if item not in popularity:
                popularity[item] = 0

            popularity[item] += 1

    return popularity


def exp_popularity(popularity, input_file, out_file):
    item_set = set()
    with codecs.open(input_file, 'r') as fr:
        for row in fr:
            #TODO need to revise when evaluating top-k
            cols = row.strip().split('\t')
            for i in cols[3:]:
                item_set.add(i)
            #item_set.add(cols[2])

    fw = codecs.open(out_file, 'w')
    for i in item_set:
        if i in popularity:
            fw.write(i + ',' + str(popularity[i]) + '\n')

    fw.close()


def exp_recall(infile, answers):
    pre_hit = 0
    post_hit = 0
    pre_test = 0
    post_test = 0
    with codecs.open(infile, 'r') as fr:
        for row in fr:
            cols = row.strip().split('\t')
            hit = 0
            if cols[0] not in answers:
                continue

            for a in answers[cols[0]]:
                if a in cols[3:]:
                    hit = 1
                    break

            if cols[2] == 'True':
                post_hit += hit
                post_test += 1
            else:
                pre_hit += hit
                pre_test += 1

    return float(pre_hit / pre_test), float(post_hit / post_test), float((pre_hit + post_hit) / (pre_test + post_test))


def offline_CTR(infile, clicks):
    hit = 0
    test = 0
    with codecs.open(infile, 'r') as fr:
        for row in fr:
            cols = row.strip().split('\t')
            test += 1
            for i in cols[3:]:
                if i in clicks[cols[0]]:
                    hit += 1
                    break
    return float(hit / test)


def click_similarity(clicks, buys, sim_matrix_file,  outfile):
    print('Read similarity matrix')
    fp = open(sim_matrix_file, 'rb')
    W = pickle.load(fp)
    index = 0
    similarities = {}
    num_log_i = {}
    fw = codecs.open(outfile, 'w')
    for s in buys:
        index += 1
        if (index % 100000) == 0:
            print(index)

        click_items = clicks[s]
        #similarities[s] = []
        for buy_item in buys[s]:
            similarity = 0
            for i in range(len(click_items)):
                if click_items[i] != buy_item:
                    similarity += W[buy_item][click_items[i]]
            fw.write(str(s) + ',' + str(similarity / len(click_items)) + '\n')

            '''
            if i not in similarities:
                similarities[i] = 0
                num_log_i[i] = 0
            similarities[i] += W[buy_item][click_items[i]]
            num_log_i[i] += 1
            try:
                similarities[s].append(str(W[buy_item][click_items[i]]))
            except:
                print(buy_item, click_items[i])
                raise
            '''

    fw.close()


def target_visit_rate(clicks, buys, out_file):
    item_cat = load_item_cat()
    with codecs.open(out_file, 'w') as fw:
        for s in buys:
            click_cats = [item_cat[i] for i in clicks[s]]
            for i in buys[s]:
                for cat in click_cats:
                    if cat == item_cat[i]:
                        fw.write(s + ',' + str(1) + '\n')
                    else:
                        fw.write(s + ',' + str(0) + '\n')


def action_time_diff(infile):
    with codecs.open(infile, 'r') as fr:
        current_session = '0'
        pre_time = datetime.datetime.strptime('2014-04-03T10:46:57.355Z', "%Y-%m-%dT%H:%M:%S.%fZ")
        fw = codecs.open('tmp_exp.csv', 'w')
        index = 0
        t_diff = 0
        for row in fr:
            index += 1
            if (index % 1000) == 0:
                print(index)

            cols = row.strip().split(',')
            if current_session == cols[0]:
                current_time = datetime.datetime.strptime(cols[1], "%Y-%m-%dT%H:%M:%S.%fZ")
                t_diff = (current_time - pre_time).total_seconds()
            else:
                fw.write(str(t_diff) + '\n')
                current_session = cols[0]
                pre_time = datetime.datetime.strptime(cols[1], "%Y-%m-%dT%H:%M:%S.%fZ")

        fw.close()


def item_life_cycle(click_logs_file):
    item_index = -2
    time_index = 1
    click_count_day = {}
    with codecs.open(click_logs_file, 'r') as fr:
        item_logs = {}
        item_begin = {}
        print('Extract date from logs')
        index = 0
        for row in fr:
            index += 1
            if (index % 1000000) == 0:
                print(index)

            cols = row.strip().split(',')
            click_time = datetime.datetime.strptime(cols[time_index], "%Y-%m-%dT%H:%M:%S.%fZ")
            if cols[item_index] not in item_logs:
                item_logs[cols[item_index]] = []
                item_begin[cols[item_index]] = click_time
            item_logs[cols[item_index]].append(click_time)
            if click_time < item_begin[cols[item_index]]:
                item_begin[cols[item_index]] = click_time

        print('date to day difference')
        item_count_day = {}
        group ={}
        for i in item_logs:
            day_set = set()
            min_date = item_begin[i]
            item_count_day[i] = []
            group[i] = 0
            for t in item_logs[i]:
                day_diff = (t - min_date).days
                item_count_day[i].append(day_diff)
                if day_diff > group[i]:
                    group[i] = day_diff

        life_cycle = {}
        group_count = {}
        for i in item_count_day:
            if group[i] not in life_cycle:
                life_cycle[group[i]] = {}
                group_count[group[i]] = 0
            group_count[group[i]] += 1

            for d in item_count_day[i]:
                if d not in life_cycle[group[i]]:
                    life_cycle[group[i]][d] = 0
                life_cycle[group[i]][d] += 1



    print('output file')
    with codecs.open('tmp_exp.csv', 'w') as fw:
        for g in group_count:
            fw.write(str(g))
            for d in range(0,30):
                if d in life_cycle[g]:
                    fw.write(',' + str(life_cycle[g][d] / group_count[g]))
                else:
                    fw.write(',0')
            fw.write('\n')


def session_length_dist(click_log, buy_log):
    fw_buy = codecs.open('tmp_exp.csv', 'w')
    fw_no = codecs.open('tmp_time.csv', 'w')
    for s in click_log:
        if s in buy_log:
            if len(click_log[s]) < 50:
                fw_buy.write(str(len(click_log[s])) + '\n')
        else:
            if len(click_log[s]) < 50:
                fw_no.write(str(len(click_log[s])) + '\n')

    fw_buy.close()
    fw_no.close()


def purchase_probability(click_log, buy_log):
    count_index = {}
    for s in buy_log:
        for i in buy_log[s]:
            index = click_log[s].index(i)
            if index not in count_index:
                count_index[index] = 0
            count_index[index] += 1

    total = sum(count_index.values())
    with codecs.open('tmp_exp.csv', 'w') as fw:
        for index in sorted(count_index):
            fw.write(str(index) + ',' + str(float(count_index[index] / total)) + '\n')


def main():
    train_file = '../data/yoochoose/click_logs_4.dat'
    buy_logs_file = '../data/yoochoose/buy_logs_4.dat'
    click_logs_file = '../data/yoochoose/click_logs_4.dat'

    #action_time_diff(train_file)
    #item_life_cycle('../data/yoochoose/click_logs_4.dat')
    buy_logs = load_raw_logs(buy_logs_file, 0, 2)
    click_logs = load_raw_logs(click_logs_file, 0, 2)
    #CTRs = {}
    recalls = {}
    #item_popularity = cal_popularity(train_file, 2)
    #session_length_dist(click_logs, buy_logs)
    '''
    for k in range(5, 31, 5):
        print(('top %s')%(k))

        pre_recall, post_recall, recall = exp_recall(('D:\\Exp Result\\SRRCF\\SRRCF_top_%s.txt')%(k), buy_logs)
        recalls[k] = []
        recalls[k].append(str(pre_recall))
        recalls[k].append(str(post_recall))
        recalls[k].append(str(recall))

        exp_popularity(item_popularity, ('update_item_base_CF_top_%s.txt')%(k), ('exp_popularity_top_%s.csv')%(k))

        CTR = offline_CTR(('D:\Exp Result\Item-based CF\item_base_CF_top_%s.txt')%(k), click_logs)
        CTR2 = offline_CTR(('D:\Exp Result\\updated item-based CF\\update_item_base_CF_top_%s.txt')%(k), click_logs)
        CTRs[k] = []
        CTRs[k].append(str(CTR))
        CTRs[k].append(str(CTR2))

    fw = codecs.open('D:\\Exp Result\\SRRCF\\exp_recall.csv', 'w')
    fw.write('top-k,Pre_Recall,Post_Recall,All_Recall\n')
    for k in sorted(recalls):
        fw.write(str(k) + ',' + (',').join(recalls[k]) + '\n')
    fw.close()
    target_visit_rate(click_logs, buy_logs, 'exp_visit_rate.csv')
    click_similarity(click_logs, buy_logs, 'yoochoose.matrix', 'exp_click_sim.csv')
    '''
    purchase_probability(click_logs, buy_logs)

main()
