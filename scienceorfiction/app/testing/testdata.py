# __init__.py
# Created by: Michael Cole
# Updated by: [Michael Cole]
# --------------------------
# Temporary test data to insert

from datetime import date, timedelta
from random import shuffle, choice, random


def getRogues():
    '''Returns list of Rogues'''
    rogueList = ['Steve Novella', 'Bob Novella', 'Jay Novella',
                 'Evan Bernstein', 'Cara Santa Maria']
    return rogueList


def getGuests():
    '''Returns a list of Guests'''
    guestList = ['George Hrab', 'Bill Nye', 'Britt Hermes',
                 'Neil deGrasse Tyson', 'Jennifer Oulette',
                 'Richard Wiseman']
    return guestList


def getAdmins():
    '''Returns list of Admin Tuples (username, password)'''
    adminList = [('admin', 'adminpass')]
    return adminList


def getRoguesRandomized():
    rogues = getRogues()
    participant_accuracy_choices = [.9, .8, .5, .2, .1]
    start_dates = [date(2005, 5, 4), date(2005, 5, 4), date(2006, 9, 3),
                   date(2012, 7, 19), date(2005, 5, 4)]
    end_dates = [None, None, None, None, None]
    shuffle(participant_accuracy_choices)
    shuffle(start_dates)
    shuffle(end_dates)
    roguesRandomized = []
    for rogue in rogues:
        roguesRandomized.append([rogue, participant_accuracy_choices.pop(),
                                 start_dates.pop(), end_dates.pop()])
    return roguesRandomized


def getEpisodes(rogues):
    episodeList = []
    ep_date = date(2018, 5, 4)
    ep_num = 1
    num_items_choices = [3, 4]
    themes_choices = [None, 'Star Wars', 'Star Trek', 'Numbers', 'Vaccines',
                      'Computer Science', 'Biology', 'Chemistry',
                      'Diseases', 'Spacefaring', 'Pseudosciences',
                      'Brains', 'Aquatic Animals', 'Medicine', 'Steel']

    previousYear = ep_date.year
    while ep_date < date.today():
        if ep_date.year != previousYear:
            previousYear = ep_date.year
            accuracies = [rogue[1] for rogue in rogues]
            shuffle(accuracies)
            for rogue in rogues:
                rogue[1] = accuracies.pop()
        episode = {}
        episode['ep_num'] = ep_num
        episode['ep_date'] = ep_date
        episode['theme'] = choice(themes_choices)
        episode['num_items'] = choice(num_items_choices)
        episode['guests'] = []

        # select presenter
        if random() <= .9:
            presenter = 'Steve Novella'
        else:
            presenter = choice(rogues)[0]

        # select correct or incorrect
        episode['rogues'] = []
        for rogue in rogues:
            if not rogue[-1] or not rogue[-1] < episode['ep_date']:
                # rogue is no longer a participant
                if rogue[0] != presenter:
                    # rogue is participant
                    if random() >= .1:
                        # rogue is present
                        if random() <= rogue[1]:
                            # rogue is correct
                            episode['rogues'].append((rogue[0], 'correct'))
                        else:
                            # rogue is incorrect
                            episode['rogues'].append((rogue[0], 'incorrect'))
                    else:
                        # rogue is absent
                        episode['rogues'].append((rogue[0], 'absent'))
                else:
                    # rogue is presenter
                    episode['rogues'].append((rogue[0], 'presenter'))

        if random() <= .08:
            guest = choice(getGuests())
            if random() >= .5:
                participant = (guest, 'correct')
            else:
                participant = (guest, 'incorrect')
            episode['guests'].append(guest)
            episode['rogues'].append(participant)

        # append episode and increment values
        episodeList.append(episode)
        ep_num += 1
        ep_date += timedelta(days=7)

    return episodeList
