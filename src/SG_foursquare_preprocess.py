import codecs


def convert_time(input_file, output_file):
    with codecs.open(input_file, 'r') as fr:
        index = 0
        fw = codecs.open(output_file, 'w')
        for row in fr:
            index += 1
            if (index % 1000) == 0:
                print(index)

            cols = row.strip().split('\t')
            parse_time = cols[-2].split(':')

            for i in range(3):
                fw.write(cols[i] + '\t')

            fw.write(parse_time[0] + '\t' + cols[-1] + '\n')

        fw.close()


def load_raw_logs(input_file, output_file,  hash_POI_file, user_index, time_index, POI_index, pos_index):
    with codecs.open(input_file, 'r') as fr:
        user_logs = {}
        POI_position = {}
        index = 0
        for row in fr:
            cols = row.strip().split('\t')
            index += 1
            if index % 10000 == 0:
                print(index)

            POI_position[cols[POI_index]] = cols[pos_index]

            user = cols[user_index]
            if user in user_logs:
                user_logs[user].append((cols[time_index], cols[POI_index]))
            else:
                user_logs[user] = []
                user_logs[user].append((cols[time_index], cols[POI_index]))

    fw = codecs.open(output_file, 'w')
    print('Output User Logs')
    for user in user_logs:
        logs = []
        for t in user_logs[user]:
            encoded_time, POI = t
            logs.append('(' + encoded_time + ',' + POI + ')')

        fw.write(user + '\t' + '\t'.join(logs) + '\n')

    fw.close()

    fw = codecs.open(hash_POI_file, 'w')
    print('Output POI to category')
    for poi in POI_position:
        fw.write(poi + '\t' + POI_position[poi] + '\n')

    fw.close()

    return user_logs


def raw_log_to_checkin_transaction(input_file, user_index, time_index, POI_index, date_index, output_file):
    with codecs.open(input_file, 'r') as fr:
        user_logs = {}
        index = 0
        for row in fr:
            cols = row.strip().split('\t')
            user = cols[user_index]
            date = cols[date_index]
            time = int(cols[time_index])
            poi = cols[POI_index]
            index += 1
            if index % 10000 == 0:
                print(index)

            if user in user_logs:
                if date in user_logs[user]:
                    user_logs[user][date][time] = poi
                else:
                    user_logs[user][date] = {}
                    user_logs[user][date][time] = poi
            else:
                user_logs[user] = {}
                user_logs[user][date] = {}
                user_logs[user][date][time] = poi

    with codecs.open(output_file, 'w') as fw:
        for user in user_logs:
            for date in user_logs[user]:
                fw.write(user)
                for time in user_logs[user][date]:
                    fw.write('\t' + '(' + str(time) + ',' + user_logs[user][date][time] + ')')

                fw.write('\n')


if __name__ == '__main__':
    train_file = '../data/SG_foursquare/train.txt'
    test_file = '../data/SG_foursquare/test.txt'

    #convert_time(train_file, 'train.txt')
    convert_time(test_file, 'test.txt')
    #load_raw_logs('train.txt', 'SG_time_train.dat', 'poi_to_position.dat', 0, -2, 1, 2)
    #load_raw_logs('test.txt', 'SG_time_test.dat', 'delete.dat', 0, -2, 1, 2)

    raw_log_to_checkin_transaction('train.txt', 0, -2, 1, -1, 'SG_transaction_train.dat')
    raw_log_to_checkin_transaction('test.txt', 0, -2, 1, -1, 'SG_transaction_test.dat')

