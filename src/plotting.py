import codecs
import matplotlib.pyplot as plt


def plot_scatter(in_file):
    x = []
    y = []
    with codecs.open(in_file, 'r') as fr:
        for row in fr:
            cols = row.strip().split('\t')
            x.append(float(cols[0]))
            y.append(float(cols[1]))
    fig, ax = plt.subplots()

    ax.set_xlabel('Number of Users (%)', fontsize=20)
    ax.set_ylabel('Number of Items (%)', fontsize=20)

    ax.scatter(x, y)
    plt.show()


def plot_hist(in_file):

    fig, (ax1,ax2) = plt.subplots(2, 1, sharex=True)
    ax1.hist(relevant)
    ax2.hist(irrelevant)
    #ax1.axis([0, 55, 0.16, 0.22])

    #ax1.set_ylabel('')
    ax1.set_xlabel('Relevant')
    ax2.set_xlabel('Irrelevant')

    plt.show()


if __name__ == '__main__':
    plot_scatter('exp7_result.txt')