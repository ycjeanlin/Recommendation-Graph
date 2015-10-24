import codecs
from sklearn.cross_validation import train_test_split


def load_raw_logs(input_file, user_index, movie_index):
    with codecs.open(input_file, 'r') as fr:
        index = 0
        item_logs = {}
        for row in fr:
            cols = row.strip().split('::')
            index += 1
            if index % 10000 == 0:
                print(index)

            user = cols[user_index]
            item = cols[movie_index]
            if item not in item_logs:
                item_logs[item] = set()
            item_logs[item].add(user)

    return item_logs


def split_train_test(item_logs, output_train, output_test):
    fw_train = codecs.open(output_train, 'w')
    fw_test = codecs.open(output_test, 'w')

    for item in item_logs:
        user_list = list(item_logs[item])
        training_index, testing_index = train_test_split(range(len(item_logs[item])), test_size=0.3, random_state=7)

        for t in training_index:
            fw_train.write('u_' + user_list[t] + '\t' + 'i_' + item + '\n')

        for t in testing_index:
            fw_test.write('u_' + user_list[t] + '\t' + 'i_' + item + '\n')

    fw_test.close()
    fw_train.close()


if __name__ == '__main__':
    user_activity_all = load_raw_logs('../data/MovieLens/ratings.dat', 0, 1)
    split_train_test(user_activity_all, '../data/MovieLens/train.dat', '../data/MovieLens/test.dat')

