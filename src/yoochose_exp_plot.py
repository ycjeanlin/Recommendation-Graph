import codecs
import matplotlib.pyplot as plt
import numpy as np
from math import log


def pre_recall_cf(x_label, y_label):
    fig, ax = plt.subplots()

    ax.set_xlabel(x_label, fontsize=18)
    ax.set_ylabel(y_label, fontsize=18)
    header = []

    ind = np.arange(3.6, 31, 5)
    with codecs.open('D:\\Exp Result\\Pre_Recall CRRCF.csv', 'r') as fr:
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
    ax.axis([1, 34, 0.20, 0.8])
    plt.xticks(fontsize = '14')
    plt.yticks(fontsize = '14')

    ax.legend(loc='best', fontsize = '14')
    plt.show()


def CRRCF_exec_time():
    fig, ax = plt.subplots()

    ax.set_xlabel('Top', fontsize=16)
    ax.set_ylabel('Time (sec.)', fontsize=16)
    header = []
    mark = ['o', '>', 'x', 'o', 'd']
    with codecs.open('D:\\Exp Result\\exp_time_CRRCF.csv', 'r') as fr:
        data_frame = {}
        x = []
        labels = True
        for row in fr:
            cols = row.strip().split(',')
            if not labels:
                for i in range(len(cols)):
                    if i == 0:
                        x.append(int(cols[i]))
                    else:
                        if i not in data_frame:
                            data_frame[i] = []
                        data_frame[i].append(float(cols[i]))
            else:
                for l in cols:
                    header.append(l)
                labels = False

        for i in sorted(data_frame):
            ax.plot(x, data_frame[i], label = header[i], marker = mark[i], markersize = 10)
    ax.axis([1, 34, 0.002, 0.015])
    ax.legend(loc='best')
    #plt.suptitle('Recall@5 with Item-based 2-Step Random Walk on RG', fontsize = 16)
    #plt.suptitle(title, fontsize = 16)
    plt.xticks(fontsize = '14')
    plt.yticks(fontsize = '14')
    plt.show()


def CRRRW_exec_time():
    fig, ax = plt.subplots()

    ax.set_xlabel('Iteration', fontsize=16)
    ax.set_ylabel('Time (sec.)', fontsize=16)
    header = []
    mark = ['o', '>', 'x', 'o', 'd']
    with codecs.open('D:\\Exp Result\\exp_time_CRRRW.csv', 'r') as fr:
        data_frame = {}
        x = []
        labels = True
        for row in fr:
            cols = row.strip().split(',')
            if not labels:
                for i in range(len(cols)):
                    if i == 0:
                        x.append(int(cols[i]))
                    else:
                        if i not in data_frame:
                            data_frame[i] = []
                        data_frame[i].append(float(cols[i]))
            else:
                for l in cols:
                    header.append(l)
                labels = False

        for i in sorted(data_frame):
            ax.plot(x, data_frame[i], label = header[i], marker = mark[i], markersize = 12)
        ax.plot([15, 195], [0.004544589, 0.004544589], '--', label = 'SRRCF no update')
    ax.axis([20, 190, 0, 0.005])
    ax.legend(loc='best')

    #plt.suptitle('Recall@5 with Item-based 2-Step Random Walk on RG', fontsize = 16)
    #plt.suptitle(title, fontsize = 16)
    plt.xticks(fontsize = '14')
    plt.yticks(fontsize = '14')
    plt.show()


def pre_recall_rw(x_label, y_label):
    fig, ax = plt.subplots()

    ax.set_xlabel(x_label, fontsize=18)
    ax.set_ylabel(y_label, fontsize=18)
    header = []

    ind = np.arange(20,200, 30)
    with codecs.open('D:\\Exp Result\\Pre_Recall CRRRW.csv', 'r') as fr:
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
        width = 5
        colors = ['w', 'w', 'grey', 'w', 'k']
        patterns = ['/', '/', '', ' ', '']
        for i in sorted(data_frame):
            print(i)
            ax.bar(ind+width*(i-1),  data_frame[i], width, label = header[i], color=colors[i], edgecolor='k', hatch = patterns[i])

    ax.set_xticks(ind + width * 2)
    ax.axis([15, 195, 0.10, 0.75])
    plt.xticks(fontsize = '14')
    plt.yticks(fontsize = '14')
    ax.plot([15, 195], [0.385188275, 0.385188275], '--', color = 'k',label = 'SRRcf@5')
    ax.plot([15, 195], [0.384374007, 0.384374007],  color = 'k', label = 'CRRcf@5')
    ax.legend(loc='best', fontsize = '14')
    plt.show()


def all_recall_cf(x_label, y_label):
    fig, ax = plt.subplots()

    ax.set_xlabel(x_label, fontsize=18)
    ax.set_ylabel(y_label, fontsize=18)
    header = []

    ind = np.arange(3.6, 31, 5)
    with codecs.open('D:\\Exp Result\\All_Recall CRRCF.csv', 'r') as fr:
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
    ax.axis([1, 34, 0.20, 0.8])
    plt.xticks(fontsize = '14')
    plt.yticks(fontsize = '14')
    #ax.plot([1, 34], [0.299650461, 0.299650461], '--', label = 'Min Pre_Recall CF@5')
    #ax.plot([1, 34], [0.58728551, 0.58728551], '--', label = 'Max Pre_Recall CF@30')
    ax.legend(loc='best', fontsize = '14')
    plt.show()


def all_recall_rw(x_label, y_label):
    fig, ax = plt.subplots()

    ax.set_xlabel(x_label, fontsize=18)
    ax.set_ylabel(y_label, fontsize=18)
    header = []

    ind = np.arange(20,200, 30)
    with codecs.open('D:\\Exp Result\\All_Recall CRRRW.csv', 'r') as fr:
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
        width = 5
        colors = ['w', 'w', 'grey', 'w', 'k']
        patterns = ['/', '/', '', ' ', '']
        for i in sorted(data_frame):
            print(i)
            ax.bar(ind+width*(i-1),  data_frame[i], width, label = header[i], color=colors[i], edgecolor='k', hatch = patterns[i])

    ax.set_xticks(ind + width * 2)
    ax.axis([15, 195, 0.1, 0.75])
    plt.xticks(fontsize = '14')
    plt.yticks(fontsize = '14')
    ax.plot([15, 195], [0.324653445, 0.324653445], '--', color = 'k', label = 'SRRcf@5')
    ax.plot([15, 195], [0.461970971, 0.461970971],  color = 'k', label = 'CRRcf@5')
    ax.legend(loc='best', fontsize = '14')
    plt.show()


def scalability_exec_time():
    fig, ax = plt.subplots()

    ax.set_xlabel('Number of Session', fontsize=16)
    ax.set_ylabel('Time (sec.)', fontsize=16)
    with codecs.open('D:\\Exp Result\\exp_time_scalability.csv', 'r') as fr:
        data_frame = {}
        x = []
        for row in fr:
            cols = row.strip().split(',')
            for i in range(len(cols)):
                if i == 0:
                    x.append(int(cols[i]))
                else:
                    if i not in data_frame:
                        data_frame[i] = []
                    data_frame[i].append(float(cols[i]))

        for i in sorted(data_frame):
            ax.plot(x, data_frame[i])
    #ax.axis([30, 200, 0.14, 0.35])
    #ax.plot([30, 200], [0.345765808706704, 0.345765808706704], '--', label = 'Ref Pre_Recall')
    #ax.plot([30, 200], [0.022939113, 0.022939113], '--', label = 'itemset-based CF')
    ax.legend(loc='best')
    plt.show()


def plot_scalability_recall():
    fig, ax = plt.subplots()

    ax.set_xlabel('Iteration', fontsize=16)
    ax.set_ylabel('Recall', fontsize=16)
    header = []
    colors = ['w', 'w', 'grey', 'w', 'k']
    patterns = ['/', '/', '', ' ', '']
    width = 5
    ind = np.arange(20,200, 30)

    with codecs.open('D:\\Exp Result\\Pre_Recall CRRRW.csv', 'r') as fr:
        data_frame = {}
        x = []
        labels = True
        for row in fr:
            cols = row.strip().split(',')
            if not labels:
                if 4 not in data_frame:
                    data_frame[4] = []
                data_frame[4].append(float(cols[4]))
            else:
                for l in cols:
                    header.append(l)
                labels = False
        ax.bar(ind+width*0,  data_frame[4], width, label = 'Pre_Recall small', color=colors[1], edgecolor='k', hatch = patterns[1])

    header = []
    with codecs.open('D:\\Exp Result\\All_Recall CRRRW.csv', 'r') as fr:
        data_frame = {}
        x = []
        labels = True
        for row in fr:
            cols = row.strip().split(',')
            if not labels:
                if 4 not in data_frame:
                    data_frame[4] = []
                data_frame[4].append(float(cols[4]))
            else:
                for l in cols:
                    header.append(l)
                labels = False
        ax.bar(ind+width*2,  data_frame[4], width, label = 'All_Recall small', color=colors[3], edgecolor='k', hatch = patterns[3])

    header = []
    with codecs.open('D:\\Exp Result\\itemset-based RWRG_step_2_top_5_m_5_9\\exp_recall.csv', 'r') as fr:
        data_frame = {}
        x = []
        labels = True
        for row in fr:
            cols = row.strip().split(',')
            if not labels:
                for i in range(len(cols)):
                    if i == 0:
                        x.append(int(cols[i]))
                    else:
                        if i not in data_frame:
                            data_frame[i] = []
                        data_frame[i].append(float(cols[i]))
            else:
                for l in cols:
                    header.append(l)
                labels = False
        for i in sorted(data_frame):
            if i != 2:
                #ax.plot(x, data_frame[i], label = header[i]+' large')
                ax.bar(ind+width*i,  data_frame[i], width, label = header[i]+' large', color=colors[i+1], edgecolor='k', hatch = patterns[i+1])

    ax.axis([15, 195, 0.1, 0.7])
    ax.legend(loc='best')
    plt.xticks(range(30, 200, 30), fontsize = '14')
    plt.yticks(fontsize = '14')
    #plt.suptitle('Recall@5 with Item-based 2-Step Random Walk on RG', fontsize = 16)
    #plt.suptitle(title, fontsize = 16)
    plt.show()


def main():
    #pre_recall_cf('Top', 'Pre_Recall')
    pre_recall_rw('Iteration', 'Pre_Recall')
    #all_recall_cf('Top', 'All_Recall')
    #all_recall_rw('Iteration', 'All_Recall')
    #CRRCF_exec_time()
    #CRRRW_exec_time()

    #plot_scalability_recall()
    #scalability_exec_time()


main()
