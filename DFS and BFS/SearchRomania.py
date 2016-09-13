'''
This code uses Deepth First Search and Breadth First Searchin finding all the
possible traversal paths between any two given points in a graph.
Particularly, this code takes in the city map of Romania as the graph. The same
is present in this folder as "RomaniaMap.JPG".
'''


__author__='Nikhil Sharma'

##Syntax to execute: "python SearchRomania.py <search type> <start city> <goal city>"

import sys
import csv
import os


###The following portion reads the roads.csv file and generates the graph
try:
    currentDir = os.path.dirname(os.path.abspath(__file__))
    pathOfRoadsFile = currentDir+'/roads.csv'
    roadsFile = open(pathOfRoadsFile)
except:
    print "\nIt appears that the 'roads.csv' file is missing. Make sure to put it back in the same folder where this source code is.\n"
    sys.exit(0)
reader = csv.reader(roadsFile, delimiter=',')
roadsData = list(reader)
roadsData = sum(roadsData,[])
roadsData = [x.strip(' ') for x in roadsData]
roadsData = filter(None, roadsData)


##Create Graph
roadGraph = {}
for loopPlaces1 in range(0,len(roadsData),2):
    if not roadsData[loopPlaces1] in roadGraph:
        roadGraph[roadsData[loopPlaces1]] = []
    if not roadsData[loopPlaces1+1] in roadGraph:
        roadGraph[roadsData[loopPlaces1+1]] = []

    roadGraph[roadsData[loopPlaces1]].append(roadsData[loopPlaces1+1])
    roadGraph[roadsData[loopPlaces1+1]].append(roadsData[loopPlaces1])


####--------------------------------------------------------------------------------------
####--------------------------------------------------------------------------------------


def depthFirstSearch(inputGraph, startNode, goalNode, path = []):
    if not path: #This handles the intial call to the function, when path is empty
        path.append(startNode)
    if startNode == goalNode:
        yield path
    for node in [x for x in inputGraph[startNode] if x not in path]:  #The "if x not in path" makes sure that we aren't including the nodes already visited
        for eachPathNode in depthFirstSearch(inputGraph, node, goalNode, path + [node]):
            yield eachPathNode

def breadthFirstSearch(inputGraph, startNode, goalNode):
    queue = [(startNode, [startNode])]
    while queue:
        (node, path) = queue.pop(0)
        for nextNode in set(inputGraph[node]) - set(path): #The subtraction operation makes sure that the nodes already visited are not counted
            if nextNode == goalNode:
                yield path + [nextNode]
            else:
                queue.append((nextNode, path + [nextNode]))



####--------------------------------------------------------------------------------------
####--------------------------------------------------------------------------------------

###Taking the input from the user
if len(sys.argv) != 4:
    print '\nPlease enter all the required information. The syntax is python SearchRomania.py <search type> <start city> <goal city>, where the <search type> is one from dfs and bfs\n'
    sys.exit()
searchType = sys.argv[1].lower()
startCity = sys.argv[2].lower()
goalCity = sys.argv[3].lower()

if searchType not in ['dfs','bfs']:
    print "\nIncorrect search type entered. Please execute again\n"
    sys.exit(0)

resultsList = list(breadthFirstSearch(roadGraph, startCity, goalCity)) if searchType == 'bfs' else list(depthFirstSearch(roadGraph, startCity, goalCity))
for localCount in range(len(resultsList)):
    print "\nPath " + str(localCount+1) + ": \n"
    for i in range(len(resultsList[localCount])):
        if i == len(resultsList[localCount])-1:
            #print 'ttttttttttttttttt'
            print resultsList[localCount][i]
        else:
            print resultsList[localCount][i] + ' -->',
    print 'Path Length: ' + str(i+1)
    print '\n'

print 'Note that the Path Length was defined as the number of nodes, not the number of edges.'
