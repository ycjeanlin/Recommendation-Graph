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


def load_raw_logs(input_file, output_file,  hash_POI_file, user_index, time_index, POI_index):
    with codecs.open(input_file, 'r') as fr:
        user_logs = {}
        POI_category = {}
        index = 0
        for row in fr:
            cols = row.strip().split('\t')
            index += 1
            if index % 10000 == 0:
                print(index)

            POI_category[cols[POI_index]] = cols[POI_index]

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
            logs.append('(' + str(encoded_time) + ',' + POI + ')')

        fw.write(user + '\t' + '\t'.join(logs) + '\n')

    fw.close()

    fw = codecs.open(hash_POI_file, 'w')
    print('Output POI to category')
    for poi in POI_category:
        fw.write(poi + '\t' + POI_category[poi] + '\n')

    fw.close()

    return user_logs


def load_user_logs(log_file):
    print('Log loading')
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


def load_hash_file(hash_file):
    hash_table = {}

    with codecs.open(hash_file, 'r') as fr:
        for row in fr:
            cols = row.strip().split('\t')
            hash_table[cols[0]] = cols[1]

    return hash_table


def person_profile(user_logs, hash_poi, output_file):
    print('Build user profile')
    user_preference = {}

    index = 0
    for user in user_logs:
        for t in user_logs[user]:
            index += 1
            if index % 10000 == 0:
                print(index)

            encoded_time, POI = t
            category = hash_poi[POI]
            if user in user_preference:
                if category in user_preference[user]:
                    user_preference[user][category] += 1
                else:
                    user_preference[user][category] = 1
            else:
                user_preference[user] = {}
                user_preference[user][category] = 1

    fw = codecs.open(output_file, 'w')

    print('Output Users Preference')
    for user in user_preference:
        preference = []
        for cat in user_preference[user]:
            preference.append('(' + cat + ',' + str(user_preference[user][cat]) + ')')

        fw.write(user + '\t' + '\t'.join(preference) + '\n')

    fw.close()

    return user_preference


if __name__ == '__main__':
    train_file = '../poidata/Foursquare/train.txt'
    test_file = '../poidata/Foursquare/test.txt'

    convert_time(train_file, 'train.txt')
    convert_time(test_file, 'test.txt')
    load_raw_logs('train.txt', 'SG_time_train.dat', 'occurence.dat', 0, 3, 1)
    load_raw_logs('test.txt', 'SG_time_test.dat', 'delete.dat', 0, 3, 1)

    user_activity_train = load_user_logs('SG_time_train.dat')
    poi_category = load_hash_file('occurence.dat')
    person_profile(user_activity_train, poi_category, 'user_preference.dat')

