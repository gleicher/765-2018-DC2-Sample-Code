# create fake data for the Discussion assignment
#
# this is the simplest possible random tree generator - I had hoped to extend it
# to make more interesting random data, but did not get around to it.
#
# the key function is "makeTree" - there are some support routines before it,
# and driver code (to generate the published examples) afterwards
#
# you probably don't want the driver - but the "fakeTree" function may be a starting
# point for more interesting data generators
#

from collections import deque
import datetime
import random

# libraries for writing different file formats
import csv,json
# In Mike's version of this, it calls the example (baseline) visualization
# code in order to make pictures as well as the different data files

# import Canvas.analyzeMessages as AM
# import DiscussionViewer.drawTree as DT
# import svgtoys.elems as ELEMS

# write a tree in various file formats (this is copied from Canvas.analyzeMessages
def writeTableCSV(messtable,filename):
    with open(filename, "w") as of:
        w = csv.writer(of,lineterminator="\n")
        w.writerow(["id","topicID","groupID","time","user","parent","numChildren","chars_total","textchars","images"])
        for m in messtable:
            w.writerow([m["id"],m["topicID"],m["groupID"],
                        m["time"],m["user"],m["parent"],len(m["children"]),
                        m["info"]["chars_total"],m["info"]["textchars"],m["info"]["images"]
                       ])
def writeTableJSON(messtable,filename):
    with open(filename, "w") as of:
        json.dump(messtable,of,indent=4)



def makeLeaf(*,id=9999,user=9999,time=datetime.datetime(year=2001,month=1,day=1),likes=False,parent=None,
             length=1000,images=0,depth=0):
    return  {
        "id": id,
        "time": time,
        "user": user,
        "parent": parent,
        "likes": likes,
        "info": {"chars_total":length,"textchars":int(length*.9),"images":images},
        "children": [],
        # these need to be removed
        "depth":depth,
        "hot":0
    }

def fakeTree(*,maxDepth = 10, childDistribution=[ [2], [1,2,0], [1,2,0,0], [1,2,0,0,0] ], nusers=5,
             topicID=1000, groupID=2000 ):
    """
    generate a message tree (example data) randomly

    the tree is described as a distribution of how many children are possible at
    each level

    for example:
    [ [2], [2], [3] ] - means 2 children for every node at level 1 and 2 and 3 children for
    nodes at level 3

    At any level, a list means "choose randomly from this list for each node" so:
    [ [2], [1,2] ] - means 2 children at level 1 (the root) and for every other level,
    randomly choose between 1 and 2 children per node

    :param maxDepth: depth of the tree
    :param childDistribution: distribution of children as a list of lists
    :param nusers: number of different users to simulate
    :param topicID: topicID for the topic (note: this is just given to the tree)
    :param groupID: groupID for the group (note: this is just given to the tree)
    :return:
    """
    messageCt = 5000
    lasttime = datetime.datetime(year=2019,month=5,day=5,hour=5,minute=5)
    messages = []

    users = [(100 + i) for i in range(nusers)]

    def nextID():
        nonlocal  messageCt
        messageCt += 1
        return messageCt
    def nextTime():
        nonlocal lasttime
        lasttime += datetime.timedelta(hours=1)
        return lasttime

    def pickUser(notlist=[]):
        u = users.copy()
        for n in notlist:
            u.remove(n)
        return random.choice(u)

    # we expand breadth first - this is the queue of nodes to add
    currentLeaves = deque({})

    # create the root message
    currentLeaves.append(makeLeaf(id=nextID(), time=nextTime(), user=pickUser([])))

    # while there are leaves to be processed, process them
    while currentLeaves:
        leaf = currentLeaves.popleft()
        messages.append(leaf)

        # decide how many children
        ld = leaf["depth"]
        if ld < maxDepth:
            # base number of likely children, just based on depth
            nchildren = random.choice(childDistribution[ld if ld< len(childDistribution) else -1])
            nots = [leaf["user"]]
            for i in range(nchildren):
                cuser = pickUser(nots)
                nots.append(cuser)
                child = makeLeaf(id=nextID(),time=nextTime(),parent=leaf["id"],depth=leaf["depth"]+1,user=cuser)
                leaf["children"].append(child["id"])
                currentLeaves.append(child)

    # clean out internal stuff and add in required stuff
    for m in messages:
        del m["hot"]
        del m["depth"]
        m["topicID"] = topicID
        m["groupID"] = groupID
        m["groupTopic"] = topicID
        m["time"] = m["time"].isoformat()
    return messages

# List of trees to make
# each entry has the name (for the files),
# the depth for the tree, the branching parameters (
# the number of trees (since it is random, creating multiple things make sense)
exampleTrees = [
    ("binary-3", 3, [ [2] ],1),
    ("binary-5", 5, [ [2] ],1),
    ("binary-8", 8, [ [2] ],1),
    ("trinary-3", 3, [[3]],1),
    ("trinary-5", 5, [[3]],1),
    ("trinary-8", 8, [[3]],1),
    ("4-way-3", 3, [[4]],1),
    ("4-way-5", 5, [[4]],1),
    ("carved-binary-5",5,[ [2],[1,2],[0,1,2]],3),
    ("carved-binary-8", 8, [[2], [1, 2], [0, 1, 2]], 3),
    ("carved-trinary-5", 5, [[3], [2, 3], [0, 1, 2,3]], 3),
    ("carved-trinary-8", 8, [[3], [2, 3], [0, 1, 2,3]], 3),
    ("medium-8", 8,   [[4,5], [2,3,4,5,6], [1,2,3,4,5,6,1,2,0], [1,2,3,0,1,2], [0,1,2,0,1]], 3),
    ("medium-12", 12, [[4, 5], [2, 3, 4], [1, 2, 3, 0, 1, 2], [1, 2, 0, 1]], 3),
    ("medium-20", 20, [[4, 5], [2, 3, 4], [1, 2, 3, 0, 1, 2], [1, 2, 0, 1]], 3),
    ("carved-trinary-5", 5, [[3], [2, 3], [0, 1, 2, 3]], 3)
]

# this creates a set of tree files - based on the exampleTrees list
def makeExamples():
    text = ""
    for i,ex in enumerate(exampleTrees):
        for iter in range(ex[3]):
            tree = fakeTree(maxDepth=ex[1],childDistribution=ex[2],nusers=max(ex[2][0])*2)
            fname = "EV-Examples/{:02d}-{}-{}".format(i,ex[0],iter)
            text += "+ $dc2e.{} ({} nodes)\n".format(fname,len(tree))
            print(fname,len(tree))
            writeTableCSV(tree,fname+".csv")
            writeTableJSON(tree,fname+".json")
    print(text)

makeExamples()