# Used to collect useful stats to be displayed by Bokeh graphs

from .extensions import getAllEpisodes, getEpisode, getParticipant, getResults


def getRogueOverallAccuracy(roguename, daterange=False, theme=False):
    '''
    Used to get a single overall accuracy for a given range. Given a
    date range or theme, more specific accuracies can be found.

    Args:
        roguename (str): Name of the rogue stats should be gathered for.
        daterange (list or tuple) - optional: Start and end dates for more
            specific accuracy information
        theme (str) - optional: Theme for more specific accuracy information.
    Returns:
        (tuple): (Accuracy, Total Correct, Total Incorrect)
    '''
    rogue = getParticipant(roguename)
    # get all results
    results = getResults(participant_id=rogue.id, daterange=daterange,
                         theme=theme)
    # get only results where rogue was present
    presentResults = [result for result in results
                      if not result.is_absent and not result.is_presenter]
    # get only results where rogue was correct
    correctResults = [result for result in presentResults
                      if result.is_correct]
    totalCorrect = len(correctResults)
    totalIncorrect = len(presentResults) - len(correctResults)
    total = len(presentResults)
    try:
        accuracy = totalCorrect/total
    except ZeroDivisionError:
        accuracy = 0
    return accuracy, totalCorrect, totalIncorrect


def getRogueAccuracy(roguename, daterange=False, theme=False):
    '''
    Used to get a list of accumulated accuracy over time for a
    given rogue.

    Args:
        roguename (str): Name of the rogue stats should be gathered for.
        daterange (list or tuple) - optional: Start and end dates for more
            specific accuracy information
        theme (str) - optional: Theme for more specific accuracy information.
    Returns:
        (list): list of accumulated accuracies over time.

    '''
    rogue = getParticipant(roguename)
    # get all results
    results = getResults(participant_id=rogue.id, daterange=daterange,
                         theme=theme)
    accuracies = []
    total = 0
    totalCorrect = 0
    for result in results:
        episode = getEpisode(ep_id=result.episode_id)
        total += 1
        if result.is_correct and not result.is_absent:
            totalCorrect += 1
        try:
            accuracy = totalCorrect/total
        except ZeroDivisionError:
            accuracy = 0
        accuracies.append((episode, accuracy))
    return accuracies


def getRogueAttendance(roguename, daterange=False):
    '''
    Used to get overall attendance of rogues.

    Args:
        roguename (str): Name of the rogue stats should be gathered for.
        daterange (list or tuple) - optional: Start and end dates for more
            specific attendence information
    Returns:
        (float): Overall attendence percentage.
    '''
    rogue = getParticipant(roguename)
    results = getResults(participant_id=rogue.id, daterange=daterange)
    present = [result for result in results if not result.is_absent]
    totalPresent = len(present)
    total = len(results)
    attendance = totalPresent/total
    return attendance


def getSweeps(allSweeps=False, presenter=False,
              participant=False, daterange=False):
    '''
    Used to get a list of episodes that were sweeps of
    some sort.

    Args:
        allSweeps (bool) - optional: If True, both
            presenter and participant sweeps will
            be gathered.
        presenter (bool) - optional: If True, only
            presenter sweeps will be gathered.
        participants (bool) - optional: If True, only
            participant sweeps will be gathered.
        daterange (list or tuple) - optional: Start and end dates for more
            specific attendence information
    Returns:
        (list): A list of all episodes that fit the optional criteria
    '''
    if allSweeps:
        presenter = True
        participant = True
    episodes = getAllEpisodes(daterange=daterange)
    sweeps = []
    for episode in episodes:
        results = getResults(episode_id=episode.id)
        for result in results:
            # remove results where participant is absent
            # or presenter
            if result.is_correct is None:
                results.remove(result)
        totalCorrect = 0
        for result in results:
            if result.is_correct:
                totalCorrect += 1
        if presenter:
            if totalCorrect == 0:
                sweeps.append(episode)
        if participant:
            if totalCorrect == len(results):
                sweeps.append(episode)
    return sweeps
