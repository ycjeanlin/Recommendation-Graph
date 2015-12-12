import codecs
import pickle


def exp_popularity(input_file, user_index, item_index):
    with codecs.open(input_file, 'r') as fr:
        index = 0
        popularity = {}
        for row in fr:
            index += 1
            if (index % 10000) == 0:
                print(index)
            cols = row.strip().split('\t')

            item = cols[item_index]

            if item not in popularity:
                popularity[item] = 0

            popularity[item] += 1

    fw = codecs.open('exp_popularity.txt', 'w')
    for i in popularity:
        fw.write(i + '\t' + str(popularity[i]) + '\n')

    fw.close()


def main():
    train_file = 'yoochoose-clicks-no-missing.dat'
    exp_popularity(train_file, 0, 1)



main()
