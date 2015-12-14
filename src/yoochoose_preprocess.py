import codecs

def extract_purchase_features(buy_logs_file, click_logs_file, output_file):
    '''
    Check did the user in a session buy something, how many times did the user click on the item
    and the index of the last view
    :param buy_logs_file:
    :param click_logs_file:
    :return output_file:
    '''
    print('load buy logs from file')
    session_index = 0
    item_index = 2
    buy_logs = {}
    index = 2
    with codecs.open(buy_logs_file, 'r') as fr:
        for row in fr:
            index += 1
            if (index % 10000) == 0:
                print(index)
            cols = row.strip().split(',')
            session_id = cols[session_index]
            item_id = cols[item_index]
            if session_id not in buy_logs:
                buy_logs[session_id] = []
            buy_logs[session_id].append(item_id)

    print('extract purchasing feature from click logs line by line')
    session_index = 0
    item_index = 2
    index = 0
    with codecs.open(click_logs_file, 'r') as fr:
        fw = codecs.open(output_file, 'w')
        session = 'NA'
        clickstream = []
        for row in fr:
            index += 1
            if (index % 10000) == 0:
                print(index)
            cols = row.strip().split(',')
            session_id = cols[session_index]
            item_id = cols[item_index]
            if session_id == session:
                clickstream.append(item_id)
            else:
                stream_size = len(clickstream)
                if session in buy_logs:
                    has_buy = 1
                    for item in buy_logs[session]:
                        view_times = 0
                        index_last_view = 0
                        for i in range(stream_size):
                            if clickstream[i] == item:
                                view_times += 1
                                index_last_view = i
                        fw.write(session + '\t' + str(has_buy) + '\t' + str(view_times) + '\t' + str(index_last_view) + '\t' + str(stream_size) + '\n')
                else:
                    has_buy = 0
                    view_times = 0
                    index_last_view = 0
                    fw.write(session + '\t' + str(has_buy) + '\t' + str(view_times) + '\t' + str(index_last_view) + '\t' + str(stream_size) + '\n')

                session = session_id
                del clickstream[:]
                clickstream.append(item_id)
        fw.close()


def split_logs_by_month(click_logs_file):
    '''
    split the yoochoose-clicks.dat by month
    :param click_logs_file:
    :return: the data logs of each month
    '''
    month_logs = {}
    time_index = 1
    index = 0
    with codecs.open(click_logs_file, 'r') as fw:
        for row in fw:
            index += 1
            if (index % 100000) == 0:
                print(index)

            cols = row.strip().split(',')
            split_time = cols[time_index].split('-')
            month = int(split_time[1])

            if month not in month_logs:
                month_logs[month] = []

            month_logs[month].append(row)

    for m, logs in month_logs.items():
        fw = codecs.open('../data/yoochoose/click_logs_' + str(m) + '.dat', 'w')
        for l in logs:
            fw.write(l)
        fw.close()


if __name__ == '__main__':
    buy_logs_file_path = '../data/yoochoose/yoochoose-buys.dat'
    click_logs_file_path = '../data/yoochoose/yoochoose-clicks.dat'
    #extract_purchase_features(buy_logs_file_path, click_logs_file_path, 'purchase_feature.txt')
    split_logs_by_month(click_logs_file_path)

