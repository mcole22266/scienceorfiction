from datetime import date
from os import environ

from bokeh.plotting import figure, output_file, save

from .extensions import getAllEpisodes, getRogues
from .stats import getRogueAccuracy, getRogueOverallAccuracy, getSweeps


def saveGraph(graph, filename):
    filename += '.html'
    output_filepath = environ['OUTPUT_FILEPATH']
    output_filepath += filename
    output_file(output_filepath)
    save(graph)


def getGraph(graphType, graphYear, graphTheme):
    graph = graphType
    if graphYear == '':
        daterange = False
    elif graphYear == 'overall':
        daterange = False
    else:
        startDate = date(int(graphYear), 1, 1)
        endDate = date(int(graphYear), 12, 31)
        daterange = (startDate, endDate)
        graph += graphYear
    if graphTheme == '':
        graphTheme = False
    else:
        graph += graphTheme
    if graphType == 'overallAccuracy':
        graphRogueOverallAccuracies(graph, daterange=daterange,
                                    theme=graphTheme)
    elif graphType == 'accuracyOverTime':
        graphRogueAccuracies(graph, daterange=daterange, theme=graphTheme)
    elif graphType == 'sweeps':
        graphSweeps(graph, daterange=daterange)
    return graph


def graphRogueOverallAccuracies(saveTo='graph', daterange=False,
                                theme=False):
    colors = ['red', 'blue', 'black', 'green', 'orange', 'purple',
              'navy']
    keepcolors = []

    x = []
    y = []
    for rogue in getRogues(onlyNames=True):
        accuracy = getRogueOverallAccuracy(rogue, daterange=daterange,
                                           theme=theme)
        accuracy = accuracy*100
        x.append(rogue)
        y.append(accuracy)
        keepcolors.append(colors.pop())

    colors = keepcolors
    p = figure(title="Rogue Accuracies",
               plot_width=1250,
               x_range=x,
               y_axis_label='Percent Correct')

    p.vbar(x=x, top=y, bottom=0, width=0.5, color=colors, alpha=0.3)

    saveGraph(p, saveTo)


def graphRogueAccuracies(saveTo='graph', theme=False, daterange=False):
    colors = ['red', 'blue', 'black', 'green', 'orange', 'purple',
              'navy']
    p = figure(title="Rogue Accuracies",
               plot_width=1250,
               x_axis_label='Date',
               y_axis_label='Accuracy',
               x_axis_type='datetime')

    for rogue in getRogues(onlyNames=True):
        accuracies = getRogueAccuracy(rogue, theme=theme, daterange=daterange)
        x = []
        y = []
        for episode, accuracy in accuracies:
            x.append(episode.date)
            y.append(accuracy)
        color = colors.pop()
        p.line(x, y, legend_label=rogue, line_width=4, color=color, alpha=.3)
        # p.circle(x, y, fill_color=color, alpha=.2, size=6)
    saveGraph(p, saveTo)


def graphSweeps(saveTo='graph', daterange=False):
    colors = ['red', 'blue', 'black', 'green', 'orange', 'purple',
              'navy']
    p = figure(title="Sweeps",
               plot_width=1250,
               x_axis_label='Date',
               y_axis_label='Number of Sweeps',
               x_axis_type='datetime')

    allPresenterSweeps = getSweeps(presenter=True, daterange=daterange)
    allparticipantSweeps = getSweeps(participant=True, daterange=daterange)
    episodes = getAllEpisodes(daterange=daterange)

    presenterSweeps = []
    numPresenterSweeps = 0
    participantSweeps = []
    numParticipantSweeps = 0
    for episode in episodes:
        if episode in allPresenterSweeps:
            numPresenterSweeps += 1
        elif episode in allparticipantSweeps:
            numParticipantSweeps += 1
        presenterSweeps.append((episode, numPresenterSweeps))
        participantSweeps.append((episode, numParticipantSweeps))

    x = []
    y = []
    for episode, numSweeps in presenterSweeps:
        x.append(episode.date)
        y.append(numSweeps)
    color = colors.pop()
    p.line(x, y, legend_label='Presenter Sweeps',
           line_width=4, color=color, alpha=.3)
    # p.circle(x, y, fill_color=color, alpha=.2, size=6)

    x = []
    y = []
    for episode, numSweeps in participantSweeps:
        x.append(episode.date)
        y.append(numSweeps)
    color = colors.pop()
    p.line(x, y, legend_label='Participant Sweeps',
           line_width=4, color=color, alpha=.3)

    saveGraph(p, saveTo)
