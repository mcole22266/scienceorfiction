from datetime import date
from os import environ

from bokeh.models import HoverTool
from bokeh.plotting import figure, output_file, save

from .extensions import getAllEpisodes, getRogues
from .stats import getRogueAccuracy, getRogueOverallAccuracy, getSweeps


def saveGraph(graph, filename):
    filename += '.html'
    output_filepath = environ['OUTPUT_FILEPATH']
    output_filepath += filename
    output_file(output_filepath)
    save(graph)


def buildAllGraphs(graphTypes, graphYears):
    for graphType in graphTypes:
        for graphYear in graphYears:
            getGraph(graphType, graphYear)


def getGraph(graphType, graphYear=False, graphTheme=False):
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
    if graphTheme:
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
    for rogue in getRogues(onlyNames=True, daterange=daterange):
        accuracy = getRogueOverallAccuracy(rogue, daterange=daterange,
                                           theme=theme)
        accuracy = accuracy*100
        x.append(rogue)
        y.append(accuracy)
        keepcolors.append(colors.pop())

    colors = keepcolors
    tools = 'hover, pan, wheel_zoom, save, reset'
    p = figure(title="Rogue Accuracies",
               x_range=x,
               y_range=(0, 100),
               y_axis_label='Percent Correct',
               sizing_mode='stretch_width',
               toolbar_location='above',
               toolbar_sticky=False,
               tools=tools,
               tooltips="@x: @top%",
               active_drag="pan",
               active_inspect="hover",
               active_scroll="wheel_zoom")

    p.vbar(x=x, top=y, bottom=0, width=0.5, color=colors, alpha=0.3)

    saveGraph(p, saveTo)


def graphRogueAccuracies(saveTo='graph', theme=False, daterange=False):
    colors = ['red', 'blue', 'black', 'green', 'orange', 'purple',
              'navy']
    hovertool = HoverTool(
        mode='vline',
        tooltips=[
            ('Date', '@x{%raw%}{%F}{%endraw%}'),  # raw/endraw added due to
                                                  # Jinja2 Error
            ('Accuracy', '@y%')
        ],
        formatters={
            'x': 'datetime'
        }
    )
    tools = [hovertool, 'pan', 'wheel_zoom', 'save', 'reset']
    p = figure(title="Rogue Accuracies",
               x_axis_label='Date',
               y_axis_label='Accuracy',
               x_axis_type='datetime',
               sizing_mode='stretch_width',
               tools=tools,
               active_drag="pan",
               active_inspect=hovertool,
               active_scroll="wheel_zoom")

    for rogue in getRogues(onlyNames=True, daterange=daterange):
        accuracies = getRogueAccuracy(rogue, theme=theme, daterange=daterange)
        x = []
        y = []
        for episode, accuracy in accuracies:
            accuracy *= 100
            x.append(episode.date)
            y.append(accuracy)
        color = colors.pop()
        p.line(x, y, legend_label=rogue, line_width=4, color=color, alpha=.3)
        # p.circle(x, y, fill_color=color, alpha=.2, size=6)
    saveGraph(p, saveTo)


def graphSweeps(saveTo='graph', daterange=False):
    colors = ['red', 'blue', 'black', 'green', 'orange', 'purple',
              'navy']

    hovertool = HoverTool(
        mode='vline',
        tooltips=[
            ('Date', '@x{%raw%}{%F}{%endraw%}'),  # raw/endraw added due to
                                                  # Jinja2 Error
            ('Accuracy', '@y%')
        ],
        formatters={
            'x': 'datetime'
        }
    )

    tools = [hovertool, 'pan', 'wheel_zoom', 'save', 'reset']

    p = figure(title="Sweeps",
               plot_width=1250,
               x_axis_label='Date',
               y_axis_label='Number of Sweeps',
               x_axis_type='datetime',
               sizing_mode='stretch_width',
               tools=tools,
               active_drag='pan',
               active_inspect=hovertool,
               active_scroll='wheel_zoom')

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
