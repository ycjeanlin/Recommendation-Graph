import codecs
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d
import matplotlib.cm as cm
from numpy import arange, array, percentile, zeros, meshgrid, sort
from math import log
from scipy.stats import gaussian_kde

def plot_surface(in_file):
    count = zeros(shape=(29,29))
    with codecs.open(in_file, 'r') as fr:
        for row in fr:
            cols = row.strip().split(',')
            x = int(cols[0])
            y = int(cols[1])
            if x < 20 and y < 20:
                count[x-1][y-1] += 1
    x = y = arange(0,29,1)
    X, Y = meshgrid(x, y)
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_wireframe(X, Y, count)
    ax.set_xlabel('Stop Time Rank')
    ax.set_ylabel('Similarity Rank')
    ax.set_zlabel('Count')
    plt.show()


def plot_scatter(in_file):
    x = []
    y = []
    with codecs.open(in_file, 'r') as fr:
        for row in fr:
            cols = row.strip().split(',')
            if float(cols[0]) < 30 and float(cols[1]) < 30:
                x.append(float(cols[0]))
                y.append(float(cols[1]))
    fig, ax = plt.subplots()

    ax.set_xlabel('Number of Triggered Users', fontsize=16)
    ax.set_ylabel('Number of Triggered Items', fontsize=16)

    ax.scatter(x, y)
    plt.show()


def plot_line(in_file, x_label, y_label, title):
    x = []
    y = []
    fig, ax = plt.subplots()

    ax.set_xlabel(x_label, fontsize=16)
    ax.set_ylabel(y_label, fontsize=16)
    header = []
    with codecs.open(in_file, 'r') as fr:
        data_frame = {}
        x = []
        labels = True
        for row in fr:
            cols = row.strip().split(',')
            if not labels:
                for i in range(len(cols)):
                    if i == 0:
                        x.append(float(cols[i]))
                    else:
                        if i not in data_frame:
                            data_frame[i] = []
                        data_frame[i].append(float(cols[i]))
            else:
                for l in cols:
                    header.append(l)
                labels = False

        for i in sorted(data_frame):
            #if i != 2 and i != 4:
            ax.plot(x, data_frame[i], label = header[i])
    #ax.axis([0, 400, 0.09, 0.20])
    #ax.plot([30, 200], [0.345765808706704, 0.345765808706704], '--', label = 'Ref Pre_Recall')
    #ax.plot([30, 200], [0.404336545589325, 0.404336545589325], '--', label = 'Ref Post_Recall')
    #ax.plot([0, 400], [0.15161722808781633, 0.15161722808781633], '--', label = 'CRRCF@5')
    #ax.plot([30, 200], [0.3428995022768188, 0.3428995022768188], '--', label = 'Max Itemset-Based RWRG')
    #ax.plot([30, 200], [0.004544589, 0.004544589], '--', label = 'item-based CF')
    #ax.plot([30, 200], [0.022939113, 0.022939113], '--', label = 'itemset-based CF')
    ax.legend(loc='best')
    #plt.suptitle('Recall@5 with Item-based 2-Step Random Walk on RG', fontsize = 16)
    plt.suptitle(title, fontsize = 16)
    plt.show()


def plot_hist(infile1, is_pdf):
    data1 = []
    with codecs.open(infile1, 'r') as fr:
        for row in fr:
            cols = row.strip().split(',')
            data1.append(int(cols[0]))


    fig, ax1 = plt.subplots()
    #bins = range(0, 100, 3)
    #ax.hist(data1, bins, color='white')
    if is_pdf:
        ax1.hist(data1, bins=arange(min(data1), 50, 1), normed = 1, color='white')
    else:
        ax1.hist(data1, bins=arange(min(data1), 50, 1), color='white')


    ax1.set_xlabel('Number of Items', fontsize = 16)
    ax1.set_ylabel('PDF', fontsize = 16)

    plt.suptitle('Stop Time v.s. Similarity (p-value<0.05)', fontsize = 16)
    plt.show()


def plot_boxplot(infile):
    data1 = []
    with codecs.open(infile, 'r') as fr:
        for row in fr:
            cols = row.strip().split(',')
            data1.append(float(cols[0]))
    data2 = []
    with codecs.open('tmp_exp.csv', 'r') as fr:
        for row in fr:
            cols = row.strip().split(',')
            data2.append(int(cols[0]))
    print('Without')
    a = array(data1)
    q1 = percentile(a, 25)
    q2 = percentile(a, 50)
    q3 = percentile(a, 75)
    print('1Q: ',q1)
    print('Med: ',q2)
    print('IQR: ', (q3 - q1))

    print('With')
    a = array(data2)
    q1 = percentile(a, 25)
    q2 = percentile(a, 50)
    q3 = percentile(a, 75)
    print('1Q: ',q1)
    print('Med: ',q2)
    print('IQR: ', (q3 - q1))

    #fig, ax1 = plt.subplots()

    fig, ((ax1, ax2)) = plt.subplots(1, 2, sharex='col', sharey='row')
    ax1.boxplot(data1, vert=True)
    ax2.boxplot(data2, vert=True)
    ax1.set_ylabel('Number of Items', fontsize='16')
    ax1.set_xticklabels(['Without Purchasing'], fontsize = '16')
    ax2.set_xticklabels(['With Purchasing'], fontsize = '16')
    #plt.suptitle('Number of Items in A Session', fontsize = '16')
    plt.show()


def plot_cdf(in_file1):
    data1 = []
    with codecs.open(in_file1, 'r') as fr:
        for row in fr:
            cols = row.strip().split(',')
            data1.append(float(cols[1]))
            #data.append(float(cols[3]) / float(cols[4]))

    # prepare cumulative value
    sorted_data1 = sort(data1)

    yvals1= arange(len(sorted_data1))/float(len(sorted_data1))

    fig, ax = plt.subplots()
    plt.suptitle('CDF of Similarity of Effective User', fontsize = 16)

    ax.plot(sorted_data1,yvals1, label = 'all')
    ax.set_xlabel('Similarity')
    ax.legend(loc='best')
    plt.show()


def plot_barplot_simple():
    data = []
    header = []
    with codecs.open('tmp_preference.csv', 'r') as fr:
        is_header = True
        for row in fr:
            cols = row.strip().split(',')
            if cols[0] == '605':
                for i in range(1, len(cols)):
                    data.append(int(cols[i]))
                break
            elif is_header:
                header = [cols[i] for i in range(1, len(cols))]
                is_header = False


    n_groups = len(data)

    fig, ax = plt.subplots()

    index = arange(n_groups)
    bar_width = 0.35

    opacity = 0.4

    ax.bar(index, data, bar_width, alpha=opacity, color='b')


    plt.xlabel('Category', fontsize = 20)
    plt.ylabel('Scores', fontsize = 20)
    plt.xticks(index + bar_width/2, header)
    plt.legend()

    plt.tight_layout()
    plt.show()


def plot_barplot(in_file, x_label, y_label):
    fig, ax = plt.subplots()

    ax.set_xlabel(x_label, fontsize=18)
    ax.set_ylabel(y_label, fontsize=18)
    header = []

    ind = arange(3.6, 31, 5)
    with codecs.open(in_file, 'r') as fr:
        data_frame = {}
        x = []
        labels = True
        for row in fr:
            cols = row.strip().split(',')
            if not labels:
                for i in range(len(cols)):
                    if i == 0:
                        x.append(float(cols[i]))
                    else:
                        if i not in data_frame:
                            data_frame[i] = []
                        data_frame[i].append(float(cols[i]))
            else:
                for l in cols:
                    header.append(l)
                labels = False
        width = 0.7
        colors = ['w', 'w', 'grey', 'w', 'k']
        patterns = ['/', '/', '', ' ', '']
        for i in sorted(data_frame):
            print(i)
            ax.bar(ind+width*(i-1),  data_frame[i], width, label = header[i], color=colors[i], edgecolor='k', hatch = patterns[i])

    ax.set_xticks(ind + width * 2)
    ax.axis([1, 34, 0.10, 0.60])
    plt.xticks(fontsize = '14')
    plt.yticks(fontsize = '14')
    #ax.plot([15, 200], [0.227484407136765, 0.227484407136765], '--', label = 'Min CF All_Recall@5')
    #ax.plot([15, 200], [0.392007926023778, 0.392007926023778], '--', label = 'Max CF All_Recall@5')

    ax.legend(loc='best')
    #plt.suptitle(title, fontsize = 20)
    plt.show()


if __name__ == '__main__':
    input_path = 'D:\\Exp Result\\US_gowalla\\CRRRW\\'
    #plot_scatter('tmp_exp.csv')
    #plot_surface('tmp_exp.csv')
    #plot_line('exp_recall.csv', 'Iteration', 'Pre_Recall', '')
    plot_line('exp_recall.csv', 'Iteration', 'Recall', '4-step CRRRW')
    #plot_boxplot('tmp_exp.csv')
    #plot_hist('exp_recall.csv', True)
    #plot_cdf('tmp_time.csv')
    #plot_barplot('tmp_exp.csv', 'Iteration', 'Pre_Recall')
    #plot_barplot_simple()