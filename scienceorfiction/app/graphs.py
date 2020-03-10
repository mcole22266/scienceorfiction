from datetime import date
from os import environ

import bokeh.palettes as palettes
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure, output_file, save

from .extensions import getAllEpisodes, getGuests, getRogues
from .stats import getRogueAccuracy, getRogueOverallAccuracy, getSweeps


def saveGraph(graph, filename):
    '''
    Writes a given graph to a file in a given location. Location is dictated by
    the OUTPUT_FILEPATH env variable.

    Args:
        graph (Bokeh Figure): The desired graph to be written to a file.
        filename (str): The desired name of the saved file.
    Returns:
        None
    '''
    filename += '.html'
    output_filepath = environ['OUTPUT_FILEPATH']
    output_filepath += filename
    output_file(output_filepath)
    save(graph)


def buildAllGraphs(graphTypes, graphYears):
    '''
    Used primarily to "update" graphs by recreating them with current data.
    Also is used upon app initialization to create graphs needed for display.

    Args:
        graphTypes (List[str]): A list of graphtypes to build.
        graphYears (List[date]): A list of dates for graphs to build.
    Returns:
        None
    '''
    for graphType in graphTypes:
        for graphYear in graphYears:
            getGraph(graphType, graphYear)


def getGraph(graphType, graphYear=False, graphTheme=False):
    '''
    "Controller" for graph-building. Given a graphType ensures that a graph
    is built.

    Args:
        graphType (str): The type of graph to build.
        graphYear(date) - optional: The year to build a graph for.
        graphTheme(str) - optional: The theme to filter all data in
            graph building.
    Returns:
        (str): Name of graph based on parameters.
    '''
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
    '''
    Used specifically to create an Overall Accuracy bar graph.

    Args:
        saveTo (str): Filename for graph.
        daterange (List or Tuple) - optional: Filter data for graphs down to
            a date range.
        theme (str) - optional: Filter data for graphs down to a particular
            theme.
    Returns:
        None
    '''
    hovertool = HoverTool(
        tooltips='''
<div class="container-fluid">
    <div>
        <span style="font-size: 17px; font-weight: bold;">@x:</span>
        <span style="font-size: 17px;">@y%</span>
    </div>
    <div class="container">
        <span style="font-size: 15px;">@correct Correct</span><br>
        <span style="font-size: 15px;">@incorrect Incorrect</span>
    </div>
</div>
''')

    x = []
    y = []
    correct = []
    incorrect = []
    for rogue in getRogues(onlyNames=True, daterange=daterange):
        rogueOverallAccuracy = getRogueOverallAccuracy(
            rogue,
            daterange=daterange,
            theme=theme)
        accuracy, num_correct, num_incorrect = rogueOverallAccuracy
        accuracy = accuracy*100
        x.append(rogue)
        y.append(accuracy)
        correct.append(num_correct)
        incorrect.append(num_incorrect)

    tools = [hovertool, 'pan', 'wheel_zoom', 'save', 'reset']
    source = ColumnDataSource(data=dict(
        x=x, y=y, correct=correct, incorrect=incorrect,
        color=palettes.Set3[len(x)]
    ))
    p = figure(title="Rogue Accuracies",
               x_range=x,
               y_range=(0, 100),
               y_axis_label='Percent Correct',
               sizing_mode='stretch_both',
               toolbar_location='above',
               toolbar_sticky=False,
               tools=tools,
               active_drag="pan",
               active_inspect=hovertool,
               active_scroll="wheel_zoom")

    p.vbar(x='x', top='y', width=0.5, color='color',
           alpha=0.75, source=source)

    saveGraph(p, saveTo)


def graphRogueAccuracies(saveTo='graph', theme=False, daterange=False):
    '''
    Used specifically to create an accumulated rogue accuracy over time
    line graph.

    Args:
        saveTo (str): Filename for graph.
        daterange (List or Tuple) - optional: Filter data for graphs down to
            a date range.
        theme (str) - optional: Filter data for graphs down to a particular
            theme.
    Returns:
        None
    '''
    hovertool = HoverTool(
        mode='vline',
        line_policy='nearest',
        tooltips='''
<div class="container-fluid">
    <div>
        <span style="font-size: 17px; font-weight: bold;">@name:</span>
        <span style="font-size: 17px;">@y%</span>
    </div>
    <div>
        <span style="font-size: 15px; font-weight: bold;">Date:</span>
        <span style="font-size: 15px;">@x{%raw%}{%F}{%endraw%}</span>
    </div>
</div>
''',
        formatters={
            'x': 'datetime'
        }
    )
    colors = palettes.Set3[12]
    tools = [hovertool, 'pan', 'wheel_zoom', 'save', 'reset']
    p = figure(title="Accuracies",
               x_axis_label='Date',
               y_axis_label='Accuracy',
               x_axis_type='datetime',
               sizing_mode='stretch_width',
               tools=tools,
               toolbar_location='above',
               active_drag="pan",
               active_inspect=hovertool,
               active_scroll="wheel_zoom")

    rogues = getRogues(daterange=daterange)
    guests = getGuests(daterange=daterange)
    participants = rogues + guests
    for i, participant in enumerate(participants):
        accuracies = getRogueAccuracy(
            participant.name, theme=theme, daterange=daterange)
        x = []
        y = []
        color = colors[i]
        for episode, accuracy in accuracies:
            accuracy *= 100
            x.append(episode.date)
            y.append(accuracy)
        source = ColumnDataSource(data=dict(
            x=x, y=y,
            name=[participant.name for r in range(len(x))],
        ))
        p.line(x='x', y='y', legend_label=participant.name, line_color=color,
               line_width=4, alpha=0.75, source=source,
               visible=participant.is_rogue)

    p.legend.click_policy = "hide"
    saveGraph(p, saveTo)


def graphSweeps(saveTo='graph', daterange=False):
    '''
    Used specifically to create an accumulated number of sweeps over time
    line graph.

    Args:
        saveTo (str): Filename for graph.
        daterange (List or Tuple) - optional: Filter data for graphs down to
            a date range.
    Returns:
        None
    '''
    colors = palettes.Set3[12]

    hovertool = HoverTool(
        mode='vline',
        tooltips='''
<div class="container-fluid">
    <div>
        <span style="font-size: 17px; font-weight: bold;">
            @label:
        </span>
        <span style="font-size: 17px;">@y</span>
    </div>
    <div>
        <span style="font-size: 15px; font-weight: bold;">Date:</span>
        <span style="font-size: 15px;">@x{%raw%}{%F}{%endraw%}</span>
    </div>
</div>
''',
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
    color = colors[0]
    source = ColumnDataSource(data=dict(
        x=x, y=y,
        label=['Presenter Sweeps' for r in range(len(x))],
    ))
    p.line(x='x', y='y', legend_label='Presenter Sweeps',
           line_width=4, color=color, alpha=0.75, source=source)

    x = []
    y = []
    for episode, numSweeps in participantSweeps:
        x.append(episode.date)
        y.append(numSweeps)
    color = colors[1]
    source = ColumnDataSource(data=dict(
        x=x, y=y,
        label=['Participant Sweeps' for r in range(len(x))],
    ))
    p.line(x='x', y='y', legend_label='Participant Sweeps',
           line_width=4, color=color, alpha=0.75, source=source)

    saveGraph(p, saveTo)
