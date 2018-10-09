# Example Visualization of discussion messages #1
# written by Mike Gleicher, October 5, 2018
#
# this was put together to be simple to write, not necessarily
# nice to use or easy to read
#
# this is a lot longer than it needs to be, because I manually
# group things because I didn't realize seaborn with do everything
# for me

import json
from collections import defaultdict
import datetime
import dateutil

# simple pictures via seaborn
import seaborn
# for saving
import matplotlib.pyplot as pyplot


def vis1(fname="test.json", absolute = True, useGroups=True):
    with open(fname) as fi:
        messages = json.load(fi)

        # sort the messages into lists for each discussion - where a discussion
        # is a tuple topic/group
        groupMessages = defaultdict(list)

        # given a message, get the key for the dictionaries
        def key(message):
            if useGroups:
                return (message["topicID"],message["groupID"])
            else:
                return (message["topicID"])

        for m in messages:
            # convert the time to something useful before we even start
            m["time"] = dateutil.parser.parse(m["time"])

            groupMessages[key(m)].append(m)

        # make a dict so we can figure out an integer for each group
        ids = {g:i for i,g in enumerate(groupMessages)}
        print(ids)

        # find the starting time for each group - assume its the first message's time
        starts = {}
        ends = {}
        for g in groupMessages:
            starts[g] = min([m["time"] for m in groupMessages[g]])
            ends[g] = max([m["time"] for m in groupMessages[g]])
            print(ids[g],starts[g],ends[g])

        # the very first message
        first = min([m["time"] for m in messages])

        # for each message, give how long it was after the start of the messages
        # assuming the first message was the beginning of the discussion
        for m in messages:
            if absolute:
                m["afterstart"] = m["time"] - first
            else:
                m["afterstart"] = m["time"] - starts[key(m)]

        # find the maximum of all durations - since we want everything on a common scale
        longest = max([m["afterstart"] for m in messages])

        # simple version of drawing using seaborn
        x = [ m["afterstart"]/datetime.timedelta(days=1) for m in messages]

        if useGroups:
            y = [ str(m["topicID"])+"\n"+str(m["groupID"]) for m in messages]
        else:
            y = [str(m["topicID"]) for m in messages]

        hues = [ "reply" if m["parent"] else "initial" for m in messages]

        # does the actual drawing
        plt = seaborn.swarmplot(y,x,hue=hues)

        # set the drawing parameters
        plt.set(xlabel="Topic Number / Group Number" if useGroups else "Topic Number")
        plt.set(ylabel="Days from start" if absolute else "Days from first in discussion")
        plt.figure.show()
        # save out the plot
        # assume that the file name is .json
        basename = fname[:-5]
        plt.figure.savefig(basename+".png")
        plt.figure.savefig(basename+".svg")
        return plt


