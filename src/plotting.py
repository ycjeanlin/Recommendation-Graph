import codecs
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from math import log
from scipy.stats import gaussian_kde


def plot_scatter(in_file):
    x = []
    y = []
    with codecs.open(in_file, 'r') as fr:
        for row in fr:
            cols = row.strip().split('\t')
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
    #ax.axis([30, 200, 0.14, 0.35])
    #ax.plot([30, 200], [0.345765808706704, 0.345765808706704], '--', label = 'Ref Pre_Recall')
    #ax.plot([30, 200], [0.404336545589325, 0.404336545589325], '--', label = 'Ref Post_Recall')
    #ax.plot([30, 200], [0.392007926023778, 0.392007926023778], '--', label = 'Ref All_Recall')
    #ax.plot([30, 200], [0.3428995022768188, 0.3428995022768188], '--', label = 'Max Itemset-Based RWRG')
    #ax.plot([30, 200], [0.004544589, 0.004544589], '--', label = 'item-based CF')
    #ax.plot([30, 200], [0.022939113, 0.022939113], '--', label = 'itemset-based CF')
    ax.legend(loc='best')
    #plt.suptitle('Recall@5 with Item-based 2-Step Random Walk on RG', fontsize = 16)
    #plt.suptitle(title, fontsize = 16)
    plt.show()


def plot_hist(infile1):
    '''
    data1 = []
    data2 = []
    data3 = []
    data4 = []
    data5 = []
    data6 = []

    with codecs.open(in_file + '_5.csv', 'r') as fr:
        for row in fr:
            cols = row.strip().split(',')
            data1.append(float(cols[1]))
            #data1.append(float(cols[3]) / float(cols[4]))

    with codecs.open(in_file + '_10.csv', 'r') as fr:
        for row in fr:
            cols = row.strip().split(',')
            data2.append(float(cols[1]))

    with codecs.open(in_file + '_15.csv', 'r') as fr:
        for row in fr:
            cols = row.strip().split(',')
            data3.append(float(cols[1]))

    with codecs.open(in_file + '_20.csv', 'r') as fr:
        for row in fr:
            cols = row.strip().split(',')
            data4.append(float(cols[1]))

    with codecs.open(in_file + '_25.csv', 'r') as fr:
        for row in fr:
            cols = row.strip().split(',')
            data5.append(float(cols[1]))

    with codecs.open(in_file + '_30.csv', 'r') as fr:
        for row in fr:
            cols = row.strip().split(',')
            data6.append(float(cols[1]))

    fig, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, sharex='col', sharey='row')
    ax1.hist(data1)
    ax2.hist(data2)
    ax3.hist(data3)
    ax4.hist(data4)
    ax5.hist(data5)
    ax6.hist(data6)

    ax5.set_xlabel('log(popularity) of Recommended Items', fontsize = 14)
    ax1.set_title('Top 5')
    ax2.set_title('Top 10')
    ax3.set_title('Top 15')
    ax4.set_title('Top 20')
    ax5.set_title('Top 25')
    ax6.set_title('Top 30')
    '''
    data1 = []
    with codecs.open(infile1, 'r') as fr:
        for row in fr:
            cols = row.strip().split(',')
            data1.append(float(cols[0]))



    fig, ax = plt.subplots()
    bins = range(0, 200, 3)
    ax.hist(data1, bins, label = 'non', color='white')

    ax.set_xlabel('Days', fontsize = 16)

    plt.suptitle('Activeness of Items', fontsize = 16)
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
    a = np.array(data1)
    q1 = np.percentile(a, 25)
    q2 = np.percentile(a, 50)
    q3 = np.percentile(a, 75)
    print('1Q: ',q1)
    print('Med: ',q2)
    print('IQR: ', (q3 - q1))

    print('With')
    a = np.array(data2)
    q1 = np.percentile(a, 25)
    q2 = np.percentile(a, 50)
    q3 = np.percentile(a, 75)
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
    sorted_data1 = np.sort(data1)

    yvals1=np.arange(len(sorted_data1))/float(len(sorted_data1))

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

    index = np.arange(n_groups)
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

    ind = np.arange(3.6, 31, 5)
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
    #plot_scatter('exp7_result.txt')
    plot_line('tmp_exp.csv', 'Exp(position)', 'Probability', 'Average Execution Time RWRG')
    #plot_line('exp_recall.csv', 'Number of Iterations', 'Recall', 'update itemset-based RWRG Recall@5')
    #plot_boxplot('tmp_exp.csv')
    #plot_hist('tmp_exp.csv')
    #plot_cdf('tmp_time.csv')
    #plot_barplot('tmp_exp.csv', 'Iteration', 'Pre_Recall')
    #plot_barplot_simple()