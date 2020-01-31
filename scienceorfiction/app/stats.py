from .extensions import getParticipant, getResults, getAllEpisodes, getEpisode


def getRogueOverallAccuracy(roguename, daterange=False, theme=False):
    rogue = getParticipant(roguename)
    results = getResults(participant_id=rogue.id, daterange=daterange,
                         theme=theme)
    presentResults = [result for result in results
                      if not result.is_absent and not result.is_presenter]
    correctResults = [result for result in presentResults
                      if result.is_correct]
    totalCorrect = len(correctResults)
    total = len(presentResults)
    accuracy = totalCorrect/total
    return accuracy


def getRogueAccuracy(roguename, daterange=False, theme=False):
    rogue = getParticipant(roguename)
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
        accuracy = totalCorrect/total
        accuracies.append((episode, accuracy))
    return accuracies


def getRogueAttendance(roguename, daterange=False):
    rogue = getParticipant(roguename)
    results = getResults(participant_id=rogue.id, daterange=daterange)
    present = [result for result in results if not result.is_absent]
    totalPresent = len(present)
    total = len(results)
    attendance = totalPresent/total
    return attendance


def getSweeps(allSweeps=False, presenter=False,
              participant=False, daterange=False):
    if allSweeps:
        presenter = True
        participant = True
    episodes = getAllEpisodes(daterange=daterange)
    sweeps = []
    for episode in episodes:
        results = getResults(episode_id=episode.id)
        for result in results:
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
