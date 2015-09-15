import codecs
import datetime as dt
from sklearn.cross_validation import train_test_split

def convert_time(input_file, output_file, time_offset):
    with codecs.open(input_file, 'r') as fr:
        index = 0
        fw = codecs.open(output_file, 'w')
        for row in fr:
            index += 1
            if (index % 1000) == 0:
                print index

            cols = row.strip().split('\t')
            parse_time =  cols[7].split()
            time_obj = dt.datetime.strptime(parse_time[0] + ' ' + parse_time[1] + ' ' + parse_time[2] + ' ' + parse_time[3] + ' ' + parse_time[5], '%a %b %d %H:%M:%S %Y') - dt.timedelta(hours=time_offset)

            for i in range(6):
                fw.write(cols[i] + '\t')

            fw.write(str(time_obj) + '\n')

        fw.close()

def load_log(input_file, output_file,  user_index, time_index, POI_index, cat_index):
    with codecs.open(input_file, 'r') as fr:
        user_logs = {}
        index = 0
        for row in fr:
            cols = row.strip().split('\t')
            index += 1
            if index % 10000 == 0:
                print index
            user = cols[user_index]

            if user in user_logs:
                time_obj = dt.datetime.strptime(cols[-1], '%Y-%m-%d %H:%M:%S')
                time = int(time_obj.strftime('%H'))
                weekday = time_obj.weekday() + 1
                user_logs[user].append((weekday, time, cols[POI_index], cols[cat_index]))
            else:
                user_logs[user] = []
                time_obj = dt.datetime.strptime(cols[-1], '%Y-%m-%d %H:%M:%S')
                time = int(time_obj.strftime('%H'))
                weekday = time_obj.weekday() + 1
                user_logs[user].append((weekday, time, cols[POI_index], cols[cat_index]))

    fw = codecs.open(output_file, 'w')
    print 'Output User Logs'
    index = 0
    for user in user_logs:
        print index
        logs = []
        for t in user_logs[user]:
            weekday, time, POI, category = t
            logs.append('(' + str(weekday) + ',' + str(time) + ',' + POI + ',' + category + ')')

        fw.write(user + '\t' + '\t'.join(logs) + '\n')

        index += 1

    fw.close()

    return user_logs

def split_train_test(user_logs, output_train, output_test, min_occur):
    print 'Splitting training data and testing data'
    fw_train = codecs.open(output_train, 'w')
    fw_test = codecs.open(output_test, 'w')

    for user in user_logs:
        training_index, testing_index = train_test_split(range(len(user_logs[user])), test_size=0.3, random_state=7)
        if len(training_index) > 0 and len(testing_index) > 0:
            training_cols = [user_logs[user][i] for i in training_index]
            testing_cols = [user_logs[user][i] for i in testing_index]

            fw_train.write(user + '\t'.join(training_cols) + '\n')

            fw_test.write(user + '\t'.join(testing_cols) + '\n')

    fw_test.close()
    fw_train.close()

def person_profile(user_logs, output_file):
    user_preference = {}

    index = 0
    for user in user_logs:
        for t in user_logs[user]:
            weekday, time, POI, category = t
            index += 1
            if index % 10000 == 0:
                print index

            if user in user_preference:
                if category in user_preference[user]:
                    user_preference[user][category] += 1
                else:
                    user_preference[user][category] = 1
            else:
                user_preference[user] = {}
                user_preference[user][category] = 1

    fw = codecs.open(output_file, 'w')

    print 'Output Users Preference'
    index = 0
    for user in user_preference:
        print index
        preference = []
        for cat in user_preference[user]:
            preference.append('(' + cat + ',' + str(user_preference[user][cat]) + ')')

        fw.write(user + '\t' + '\t'.join(preference) + '\n')

        index += 1

    fw.close()

    return user_preference

if __name__ == '__main__':
    #convert_time('../foursquare_data/dataset_TSMC2014_NYC.txt', '../foursquare_data/NYC_time.dat', 4)
    user_activity = load_log('test_log', 'test_user_log.dat', 0, -1, 1, 2)
    person_profile(user_activity, 'test_user_preference.dat')