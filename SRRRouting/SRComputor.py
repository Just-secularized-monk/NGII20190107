# coding=utf-8
# !/usr/bin/python

import time
import os
import networkx as nx
import InfoGet

def copyFile(f1, f2):
    in_file = open(f1)
    indata = in_file.read()
    out_file = open(f2, 'w')
    out_file.write(indata)

def cmp_file(f1, f2):
    st1 = os.stat(f1)
    st2 = os.stat(f2)
    if st1.st_size != st2.st_size:
        return False
    bufsize = 8 * 1024
    with open(f1, 'rb') as fp1, open(f2, 'rb') as fp2:
        while True:
            b1 = fp1.read(bufsize)
            b2 = fp2.read(bufsize)
            if b1 != b2:
                return False
            if not b1:
                return True

def computeLatencyOfPath(G, path):
    latency = 0
    for node in path:
        latency = latency + G.nodes[node]["latency"]
    return latency

def getCurrentNodes(SRs):
    SRMap = {"3:111:1::": "1", "3:111:2::": "2", "3:111:3::": "3", "3:111:4::": "4",
             "3:111:5::": "5", "3:111:6::": "6", "3:111:7::": "7", "3:111:8::": "8",
             "3:111:9::": "9"}
    nodes = []
    for SR in SRs:
        for i in range(1, len(SR)):
            if SR[i] == "2001:1:5::1":
                continue
            else:
                node = SRMap[SR[i]]
                if node == "1" or node == "9" or str(node) == "2":
                    continue
                elif node not in nodes:
                    nodes.append(node)
    return nodes

def getAllShortestPaths(G, src, dst):
    shortest_paths = []
    paths = list(nx.shortest_simple_paths(G, src, dst))
    # print(paths[0])
    shortes_len = int(len(paths[0]))
    # print(shortes_len)
    for path in paths:
        if len(path) == shortes_len:
            shortest_paths.append(path)
    # print(shortest_paths)
    return shortest_paths

def getODSR(G, SRs):
    SR = []
    SRMap = {"1": "3:111:1::", "2": "3:111:2::", "3": "3:111:3::", "4": "3:111:4::",
             "5": "3:111:5::", "6": "3:111:6::", "7": "3:111:7::", "8": "3:111:8::",
             "9": "3:111:9::"}
    selectPathSet = []
    nodes = getCurrentNodes(SRs)
    print("current nodes: " + str(nodes))
    SR.append("x")
    shortestPathSet = getAllShortestPaths(G, 1, 9)
    # remove the joint path
    for path in shortestPathSet:
        flag = False
        for node in path:
            if str(node) != "1" and str(node) != "2" and str(node) != "9" and str(node) in nodes:
                flag = True
        if flag == True:
            continue
        else:
            selectPathSet.append(path)
    print("selectPathSet: " + str(selectPathSet))
    ODPath = selectHighestPath(G, selectPathSet)
    print("ODPath: " + str(ODPath))
    if ODPath == None:
        return None
    else:
        for node in ODPath:
            SR.append(SRMap[str(node)])
        SR.append("2001:1:5::1")
        return SR

def getTDSR(request, G):
    SR = []
    SRMap = {"1": "3:111:1::", "2": "3:111:2::", "3": "3:111:3::", "4": "3:111:4::",
             "5": "3:111:5::", "6": "3:111:6::", "7": "3:111:7::", "8": "3:111:8::",
             "9": "3:111:9::"}
    SR.append(request.split(" ")[0])
    selectPathSet = getAllShortestPaths(G, 1, 9)
    print("selectPathSet: " + str(selectPathSet))
    TDPath = selectLowestPath(G, request.split(" ")[1], selectPathSet)
    print("TDPath: " + str(TDPath))
    if TDPath == None:
        return None
    else:
        for node in TDPath:
            SR.append(SRMap[str(node)])
        SR.append("2001:1:5::1")
        return SR

def selectHighestPath(G, paths):
    tmp = 0
    lastPath = []
    # filter the paths with high latency, get the lowest path
    for path in paths:
        # print("path: " + str(path))
        path_latency = computeLatencyOfPath(G, path)
        # print("path_latency: " + str(path_latency))
        # print("tmp: " + str(tmp))
        if path_latency > tmp:
            tmp = path_latency
            lastPath = path
        # print("lastPath: " + str(lastPath))
    if len(lastPath) > 0:
        return lastPath
    else:
        return None

def selectLowestPath(G, latency, paths):
    tmp = int(latency)
    lastPath = []
    # filter the paths with high latency, get the lowest path
    for path in paths:
        # print("path: " + str(path))
        path_latency = computeLatencyOfPath(G, path)
        # print("path_latency: " + str(path_latency))
        # print("tmp: " + str(tmp))
        if path_latency < tmp:
            tmp = path_latency
            lastPath = path
        # print("lastPath: " + str(lastPath))
    if len(lastPath) > 0:
        return lastPath
    else:
        return None

def customizeForOneRequest(request, G):
    SRs = []
    print("start to customize 1 request: " + request)
    # get the 2-D SR for the request
    TDSR = getTDSR(request, G)
    if TDSR != None:
        SRs.append(TDSR)
    else:
        return None
    # get the 1-D SR
    ODSR = getODSR(G, SRs)
    if ODSR != None:
        SRs.append(ODSR)
    else:
        return None
    return SRs

def customizeForZeroRequest(G):
    SRs = []
    print("start to customize 0 request!")
    # get the 1-D SR
    ODSR = getODSR(G, SRs)
    if ODSR != None:
        SRs.append(ODSR)
    else:
        return None
    return SRs

def customizeForRequests(requestList, G):
    print("start to customize n request!" + str(requestList))

if __name__ == '__main__':
    while True:
        # get the new latency.txt and request.txt
        InfoGet.getNewRequestTXT()
        InfoGet.getNewLatancyTXT()
        print("new request.txt and latency.txt has been done!")
        # create G and requestList
        G = nx.Graph()
        requestList = []
        SRs = []
        for line in open("/home/sdn/SRRRouting/latency.txt"):
            node = int(line.strip().split(":")[0])
            latency = int(line.strip().split(":")[1])
            G.add_node(node, latency=latency)
        for line in open("/home/sdn/SRRRouting/topo.txt"):
            src = int(line.strip().split(" ")[0])
            dst = int(line.strip().split(" ")[1])
            G.add_edge(src, dst)
        print(list(G.nodes.data()))
        for line in open("/home/sdn/SRRRouting/request.txt"):
            requestList.append(line.strip())
        print(requestList)
        # compute the SRLists
        if len(requestList) == 1:
            SRs = customizeForOneRequest(requestList[0], G)
        elif len(requestList) == 0:
            SRs = customizeForZeroRequest(G)
        else:
            SRs = customizeForRequests(requestList, G)
        # if no SRs, continue
        if SRs == None:
            print("Fail!")
        else:
            print("last SRs:" + str(SRs))
        # write the SRs to sr_new.txt every time
        fo = open("/home/sdn/SRRRouting/sr_new.txt", 'w')
        for SR_Item in SRs:
            for i in range(0, len(SR_Item)):
                if i == 1 or i == 2:
                    continue
                elif i == len(SR_Item) - 1:
                    fo.write(SR_Item[i] + "\n")
                else:
                    fo.write(SR_Item[i] + " ")
        fo.close()
        # cmp sr_new.txt and sr_old.txt
        if cmp_file("/home/sdn/SRRRouting/sr_new.txt", "/home/sdn/SRRRouting/sr_old.txt") == False:
            os.system("./expect.sh ")
            copyFile("/home/sdn/SRRRouting/sr_new.txt", "/home/sdn/SRRRouting/sr_old.txt")
            print("SCP the sr_new.txt!")
        else:
            print("Don't SCP: same SRs!")
        time.sleep(20)