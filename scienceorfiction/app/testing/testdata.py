# Temporary test data to insert
from datetime import date, timedelta
from random import shuffle, choice, random


def getRogues():
    '''Returns list of Rogues'''
    rogueList = ['Steve Novella', 'Bob Novella', 'Jay Novella',
                 'Evan Bernstein', 'Cara Santa Maria']
    return rogueList


def getAdmins():
    '''Returns list of Admin Tuples (username, password)'''
    adminList = [('admin', 'adminpass')]
    return adminList


def getEpisodes():
    episodeList = []
    ep_date = date(2012, 1, 7)
    ep_num = 600
    num_items_choices = [3, 4]
    participant_accuracy_choices = [.9, .7, .5, .4, .2]
    themes_choices = [None, 'Star Wars', 'Star Trek', 'Numbers', 'Vaccines',
                      'Computer Science', 'Biology', 'Chemistry',
                      'Diseases', 'Spacefaring', 'Pseudosciences',
                      'Brains', 'Aquatic Animals', 'Medicine', 'Steel']

    # assign accuracies to rogues
    rogues = []
    for rogue in getRogues():
        shuffle(participant_accuracy_choices)
        rogues.append((rogue, participant_accuracy_choices.pop()))

    while ep_date < date.today():
        episode = {}
        episode['ep_num'] = ep_num
        episode['ep_date'] = ep_date
        episode['theme'] = choice(themes_choices)
        episode['num_items'] = choice(num_items_choices)

        # select presenter
        if random() <= .9:
            presenter = 'Steve Novella'
        else:
            presenter = choice(rogues)[0]

        # select correct or incorrect
        episode['rogues'] = []
        for rogue in rogues:
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

        # append episode and increment values
        episodeList.append(episode)
        ep_num += 1
        ep_date += timedelta(days=7)

    return episodeList
