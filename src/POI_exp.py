import codecs


def load_conv_logs(input_file, session_index, item_index):
    # Note: the input file must be converted to session, item format
    logs = {}
    index = 0
    with codecs.open(input_file, 'r') as fr:
        for row in fr:
            index += 1
            if (index % 1000) == 0:
                print(index)

            cols = row.strip().split(',')

            session = cols[session_index]
            item = cols[item_index]
            if session not in logs:
                logs[session] = []

            logs[session].append(item)

    return logs

def count_num_feature(input_raw_file, col_index, seperator):
    user_set = set()
    with codecs.open(input_raw_file, 'r') as fr:
        for row in fr:
            cols = row.strip().split(seperator)
            user_set.add(cols[col_index])

        print('Number = ', len(user_set))


def count_activities_session(logs, output_file):
    with codecs.open(output_file, 'w') as fw:
        for s in logs:
            fw.write(str(len(logs[s])) + '\n')


def exp_recall(infile, test_logs):
    hit = 0
    test = 0
    with codecs.open(infile, 'r') as fr:
        for row in fr:
            cols = row.strip().split('\t')
            answers = test_logs[cols[0]][-1]
            test += 1
            for i in range(2, len(cols)):
                if cols[i] == answers:
                    #if cols[i] in answers[answers.index(cols[i]):]:
                    #answers.remove(cols[i])
                    hit += 1
                    break

    return float(hit / test)


def main(output_path):
    train_file = '../data/CA_foursquare/conv_train.dat'
    test_file =  '../data/CA_foursquare/conv_test.dat'
    #train_logs = load_conv_logs(train_file, 0, 1)
    test_logs = load_conv_logs(test_file, 0, 1)
    #count_activities_session(train_logs, 'tmp_exp.csv')
    #count_num_feature('../data/SG_gowalla/conv_train.dat', 0, ',')

    recalls = {}
    #for k in range(5, 6, 5):
    for k in range(5, 32, 5):
        print(('top %s')%(k))
        #recall = exp_recall(output_path + 'iteration_%s.txt'%k, test_logs)
        recall = exp_recall(output_path + ('top_%s.txt')%(k), test_logs)

        recalls[k] = str(recall)

    #fw = codecs.open(output_path+'exp_recall.csv', 'w')
    fw = codecs.open(output_path + 'exp_recall_top.csv', 'w')

    #fw.write('iteration,Recall\n')
    fw.write('top,Recall\n')
    for k in sorted(recalls):
        fw.write(str(k) + ',' + recalls[k] + '\n')
    fw.close()



if __name__ == "__main__":
    main('D:\\Exp Result\\CA_foursquare\\CRRRW\\')

