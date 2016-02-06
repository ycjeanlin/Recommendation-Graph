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
    with codecs.open('D:\\Exp Result\\Pre_Recall CFRG.csv', 'r') as fr:
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

    ax.legend(loc='best', fontsize = '14')
    plt.show()


def pre_recall_rw(x_label, y_label):
    fig, ax = plt.subplots()

    ax.set_xlabel(x_label, fontsize=18)
    ax.set_ylabel(y_label, fontsize=18)
    header = []

    ind = np.arange(20,200, 30)
    with codecs.open('D:\\Exp Result\\Pre_Recall RWRG.csv', 'r') as fr:
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
    ax.axis([15, 195, 0.10, 0.55])
    plt.xticks(fontsize = '14')
    plt.yticks(fontsize = '14')
    ax.plot([15, 195], [0.299650461, 0.299650461], '--', label = 'Min Pre_Recall CF@5')
    ax.plot([15, 195], [0.345765809, 0.345765809], '--', label = 'Max Pre_Recall CF@5')
    ax.legend(loc='best', fontsize = '14')
    plt.show()


def all_recall_cf(x_label, y_label):
    fig, ax = plt.subplots()

    ax.set_xlabel(x_label, fontsize=18)
    ax.set_ylabel(y_label, fontsize=18)
    header = []

    ind = np.arange(3.6, 31, 5)
    with codecs.open('D:\\Exp Result\\All_Recall CFRG.csv', 'r') as fr:
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
    ax.axis([1, 34, 0.10, 0.75])
    plt.xticks(fontsize = '14')
    plt.yticks(fontsize = '14')

    ax.legend(loc='best', fontsize = '14')
    plt.show()


def all_recall_rw(x_label, y_label):
    fig, ax = plt.subplots()

    ax.set_xlabel(x_label, fontsize=18)
    ax.set_ylabel(y_label, fontsize=18)
    header = []

    ind = np.arange(20,200, 30)
    with codecs.open('D:\\Exp Result\\All_Recall RWRG.csv', 'r') as fr:
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
    ax.axis([15, 195, 0.10, 0.65])
    plt.xticks(fontsize = '14')
    plt.yticks(fontsize = '14')
    ax.plot([15, 195], [0.227484407, 0.227484407], '--', label = 'Min All_Recall CF@5')
    ax.plot([15, 195], [0.392007926, 0.392007926], '--', label = 'Max All_Recall CF@5')
    ax.legend(loc='best', fontsize = '14')
    plt.show()


def main():
    #pre_recall_cf('Iteration', 'Pre_Recall')
    #pre_recall_rw('Iteration', 'Pre_Recall')
    #all_recall_cf('Iteration', 'All_Recall')
    all_recall_rw('Iteration', 'All_Recall')


main()
