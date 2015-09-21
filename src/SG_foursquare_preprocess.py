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

            fw.write(parse_time[0] + '\n')

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


if __name__ == '__main__':
    train_file = '../data/SG_foursquare/train.txt'
    test_file = '../data/SG_foursquare/test.txt'

    convert_time(train_file, 'train.txt')
    convert_time(test_file, 'test.txt')
    load_raw_logs('train.txt', 'SG_time_train.dat', 'poi_to_position.dat', 0, -1, 1, -2)
    load_raw_logs('test.txt', 'SG_time_test.dat', 'delete.dat', 0, -1, 1, -2)

