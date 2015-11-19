import codecs
import matplotlib.pyplot as plt


def plot_scatter(in_file):
    x = []
    y = []
    with codecs.open(in_file, 'r') as fr:
        for row in fr:
            cols = row.strip().split('\t')
            x.append(int(cols[0]))
            y.append(float(cols[1]))
    fig, ax = plt.subplots()

    ax.set_xlabel('Top-k User Similarity', fontsize=20)
    ax.set_ylabel('Precision @ Top-5', fontsize=20)

    ax.plot(x, y)
    plt.show()


def plot_line(in_file, x_label, y_label):
    x1 = []
    x2 = []
    y1 = []
    y2 = []
    with codecs.open(in_file, 'r') as fr:
        for row in fr:
            cols = row.strip().split('\t')
            x1.append(int(cols[0]))
            y1.append(float(cols[1]))

    with codecs.open('exp_diversity_hit.txt', 'r') as fr:
        for row in fr:
            cols = row.strip().split('\t')
            x2.append(int(cols[0]))
            y2.append(float(cols[1]))

    fig, ax = plt.subplots()

    ax.set_xlabel(x_label, fontsize=16)
    ax.set_ylabel(y_label, fontsize=16)


    ax.plot(x1, y1, label = 'Recommended')
    ax.plot(x2, y2, label = 'Hit')

    ax.legend(loc='upper right')
    plt.show()


def plot_hist(in_file):
    data1 = []
    '''
    data2 = []
    data3 = []
    data4 = []
    data5 = []
    data6 = []
    '''
    with codecs.open(in_file, 'r') as fr:
        for row in fr:
            cols = row.strip().split('\t')
            data1.append(int(cols[1]))
    '''
    with codecs.open(in_file + '_10.txt', 'r') as fr:
        for row in fr:
            cols = row.strip().split('\t')
            data2.append(int(cols[1]))

    with codecs.open(in_file + '_15.txt', 'r') as fr:
        for row in fr:
            cols = row.strip().split('\t')
            data3.append(int(cols[1]))

    with codecs.open(in_file + '_20.txt', 'r') as fr:
        for row in fr:
            cols = row.strip().split('\t')
            data4.append(int(cols[1]))

    with codecs.open(in_file + '_25.txt', 'r') as fr:
        for row in fr:
            cols = row.strip().split('\t')
            data5.append(int(cols[1]))

    with codecs.open(in_file + '_30.txt', 'r') as fr:
        for row in fr:
            cols = row.strip().split('\t')
            data6.append(int(cols[1]))
    '''
    #fig, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, sharex='col', sharey='row')
    fig, ax = plt.subplots()
    ax.hist(data1)
    ax.set_xlabel('Degree')
    '''
    ax1.hist(data1)
    ax2.hist(data2)
    ax3.hist(data3)
    ax4.hist(data4)
    ax5.hist(data5)
    ax6.hist(data6)

    ax5.set_xlabel('Popularity', fontsize = 14)
    ax1.set_title('Top 5')
    ax2.set_title('Top 10')
    ax3.set_title('Top 15')
    ax4.set_title('Top 20')
    ax5.set_title('Top 25')
    ax6.set_title('Top 30')
    '''
    plt.suptitle('Intermediate User Degree Distribution', fontsize = 16)
    plt.show()


if __name__ == '__main__':
    #plot_scatter('exp_precision.txt')
    #plot_line('exp_diversity.txt', 'Top k of User Similarity', 'Recommended Items Diversity')
    plot_hist('user_degree.txt')