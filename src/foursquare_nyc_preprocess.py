import codecs
import datetime as dt
from sklearn.cross_validation import train_test_split


def convert_time(input_file, output_file, time_offset):
    with codecs.open(input_file, 'r') as fr:
        index = 0
        fw = codecs.open(output_file, 'w')
        for row in fr:
            index += 1
            if (index % 10000) == 0:
                print(index)

            cols = row.strip().split('\t')
            parse_time =  cols[7].split()
            time_obj = dt.datetime.strptime(parse_time[0] + ' ' + parse_time[1] + ' ' + parse_time[2] + ' ' + parse_time[3] + ' ' + parse_time[5], '%a %b %d %H:%M:%S %Y') - dt.timedelta(hours=time_offset)

            for i in range(6):
                fw.write(cols[i] + '\t')

            fw.write(str(time_obj) + '\n')

        fw.close()


def time_encode(weekday, time):
    return weekday * 24 + time


def load_raw_logs(input_file, output_file,  hash_POI_file, user_index, time_index, POI_index, cat_index):
    with codecs.open(input_file, 'r') as fr:
        user_logs = {}
        POI_category ={}
        index = 0
        for row in fr:
            cols = row.strip().split('\t')
            index += 1
            if index % 10000 == 0:
                print(index)

            POI_category[cols[cat_index]] = cols[cat_index]

            user = cols[user_index]
            if user in user_logs:
                time_obj = dt.datetime.strptime(cols[-1], '%Y-%m-%d %H:%M:%S')
                time = int(time_obj.strftime('%H'))
                weekday = time_obj.weekday()
                user_logs[user].append((time_encode(weekday, time), cols[cat_index]))
            else:
                user_logs[user] = []
                time_obj = dt.datetime.strptime(cols[-1], '%Y-%m-%d %H:%M:%S')
                time = int(time_obj.strftime('%H'))
                weekday = time_obj.weekday() + 1
                user_logs[user].append((time_encode(weekday, time), cols[cat_index]))

    fw = codecs.open(output_file, 'w')
    print('Output User Logs')
    for user in user_logs:
        logs = []
        for t in user_logs[user]:
            encoded_time, cat = t
            logs.append('|' + str(encoded_time) + ',' + cat + '|')

        fw.write(user + '\t' + '\t'.join(logs) + '\n')

    fw.close()

    fw = codecs.open(hash_POI_file, 'w')
    print('Output POI to position')
    for poi in POI_category:
        fw.write(poi + '\t' + POI_category[poi] + '\n')

    fw.close()

    return user_logs


def split_train_test(user_logs, output_train, output_test):
    print('Splitting training data and testing data')
    fw_train = codecs.open(output_train, 'w')
    fw_test = codecs.open(output_test, 'w')

    for user in user_logs:
        fw_train.write(user + '\t')
        fw_test.write(user + '\t')
        training_index, testing_index = train_test_split(range(len(user_logs[user])), test_size=0.3, random_state=7)
        if len(training_index) > 0 and len(testing_index) > 0:
            training_tuples = [user_logs[user][i] for i in training_index]
            testing_tuples = [user_logs[user][i] for i in testing_index]

            for t in training_tuples:
                fw_train.write('|' + str(t[0]) + ',' + t[1] + '|' + '\t')

            for t in testing_tuples:
                fw_test.write('|' + str(t[0]) + ',' + t[1] + '|' + '\t')

        fw_train.write('\n')
        fw_test.write('\n')
    fw_test.close()
    fw_train.close()


def load_user_logs(log_file):
    print('Log loading')
    with codecs.open(log_file, 'r') as fr:
        user_logs = {}
        for row in fr:
            cols = row.strip().split('\t')
            user = cols[0]
            for i in range(1, len(cols)):
                encoded_time, POI = cols[i].strip('|').split(',')
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
            preference.append('|' + cat + ',' + str(user_preference[user][cat]) + '|')

        fw.write(user + '\t' + '\t'.join(preference) + '\n')

    fw.close()

    return user_preference


if __name__ == '__main__':
    convert_time('../data/NYC_foursquare/dataset_TSMC2014_NYC.txt', '../data/NYC_foursquare/NYC_time.dat', 4)
    user_activity_all = load_raw_logs('../data/NYC_foursquare/NYC_time.dat', 'user_log_all.dat', 'poi_to_category.dat', 0, -1, 1, 3)
    split_train_test(user_activity_all, 'NYC_time_train.dat', 'NYC_time_test.dat')
    user_activity_train = load_user_logs('NYC_time_train.dat')
    poi_category = load_hash_file('poi_to_category.dat')
    person_profile(user_activity_train, poi_category, 'user_preference.dat')