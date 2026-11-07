import matplotlib.pyplot as plt
from IPython import display

plt.ion()

def plot(scores, mean_scores, score_times = None, mean_score_times = None, times = None, mean_times = None):
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.title("training...")
    plt.xlabel("Number of games")
    plt.ylabel("Score")
    plt.plot(scores)
    plt.plot(mean_scores)
    #plt.plot(score_times)
    #plt.plot(mean_score_times)
    #plt.plot(times)
    #plt.plot(mean_times)
    plt.ylim(ymin=0)
    plt.text(len(scores)-1, scores[-1], "score: " + str(scores[-1]))
    plt.text(len(mean_scores)-1, mean_scores[-1], "mean score: " + str(mean_scores[-1]))
    #plt.text(len(score_times)-1, score_times[-1], "score/time: " + str(score_times[-1]))
    #plt.text(len(mean_score_times)-1, mean_score_times[-1], "mean score/time: " + str(mean_score_times[-1]))
    #plt.text(len(times)-1, times[-1], "time: " + str(times[-1]))
    #plt.text(len(mean_times)-1, mean_times[-1], "mean time: " + str(mean_times[-1]))
    
