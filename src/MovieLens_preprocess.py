import codecs
from sklearn.cross_validation import train_test_split


def load_raw_logs(input_file, user_index, movie_index):
    with codecs.open(input_file, 'r') as fr:
        index = 0
        user_logs = {}
        for row in fr:
            cols = row.strip().split('::')
            index += 1
            if index % 10000 == 0:
                print(index)

            user = cols[user_index]
            movie = cols[movie_index]
            if user not in user_logs:
                user_logs[user] = set()
            user_logs[user].add(movie)

    return user_logs


def split_train_test(user_logs, output_train, output_test):
    fw_train = codecs.open(output_train, 'w')
    fw_test = codecs.open(output_test, 'w')

    for user in user_logs:
        movie_list = list(user_logs[user])
        training_index, testing_index = train_test_split(range(len(user_logs[user])), test_size=0.3, random_state=7)

        for t in training_index:
            fw_train.write('u_' + user + '\t' + 'i_' + movie_list[t] + '\n')

        for t in testing_index:
            fw_test.write('u_' + user + '\t' + 'i_' + movie_list[t] + '\n')

    fw_test.close()
    fw_train.close()


if __name__ == '__main__':
    user_activity_all = load_raw_logs('../data/MovieLens/ratings.dat', 0, 1)
    split_train_test(user_activity_all, '../data/MovieLens/train.dat', '../data/MovieLens/test.dat')

