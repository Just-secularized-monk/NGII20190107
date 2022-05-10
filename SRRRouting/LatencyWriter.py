# coding=utf-8
# !/usr/bin/python

import json
import io
import os
import time

latencyPeriod = 5

def file_name(file_dir, name):
    L = []
    for root, dirs, files in os.walk(file_dir):
        for file in files:
            if os.path.splitext(file)[1] == name:
                L.append(os.path.join(root, file))
    return L

def removeFiles(path, name):
    files = file_name(path, name)
    for file in files:
        os.system("sudo rm " + file)

def writeHopTxt(srcPort, dstPort, hopId):
    jsonFile = "flow_hop_latency," + srcPort + "-" + dstPort + ",sw_id=" + hopId + ".json"
    os.system(
        "curl -G \'http://localhost:8086/query\' --data-urlencode \"db=INTdatabase\" --data-urlencode \"q=select * from \\\"flow_hop_latency," + srcPort + "->" + dstPort + ",proto=17,sw_id=" + hopId + "\\\" " + " ORDER BY time DESC LIMIT " + str(
            latencyPeriod) + "\"" + " > /home/sdn/GrafanaData/influx/json/" + jsonFile)
    os.system("sudo chmod 777 /home/sdn/GrafanaData/influx/json/" + jsonFile)
    # Add the hop.json
    hopTxt = hopId + ".txt"
    fo = open("/home/sdn/GrafanaData/influx/node/" + hopTxt, "w")
    with io.open('/home/sdn/GrafanaData/influx/json/' + jsonFile, 'r', encoding='utf8')as hop_fp:
        hop_data = json.load(hop_fp).get("results")[0].get("series")[0].get("values")
        for one_data in hop_data:
            fo.write(str(one_data[0]) + " " + str(one_data[1]) + '\n')
    fo.close()
    os.system("sudo chmod 777 /home/sdn/GrafanaData/influx/node/" + hopTxt)

def readFromInflux():
    # open the flows.txt with "r"
    with open("/home/sdn/SRRRouting/flowConfig.txt", 'r') as flow_txt:
        flows = flow_txt.readlines()
        for i in range(len(flows)):
            srcPort = flows[i].split(" ")[0] + ":" + flows[i].split(" ")[1]
            dstPort = flows[i].split(" ")[2] + ":" + flows[i].split(" ")[3].strip()
            jsonFile = "flow_stat," + srcPort + "-" + dstPort + ".json"
            # Get the flow.json
            os.system(
                "curl -G \'http://localhost:8086/query\' --data-urlencode \"db=INTdatabase\" --data-urlencode \"q=select * from \\\"flow_stat," + srcPort + "->" + dstPort + ",proto=17\\\" " + " ORDER BY time DESC LIMIT " + str(
                    latencyPeriod) + "\"" + " > /home/sdn/GrafanaData/influx/json/" + jsonFile)
            # sudo chmod 777 flow.json
            os.system("sudo chmod 777 /home/sdn/GrafanaData/influx/json/" + jsonFile)
            # open the flow.json with "r"
            with io.open('/home/sdn/GrafanaData/influx/json/' + jsonFile, 'r', encoding='utf8') as fp:
                try:
                    results = json.load(fp).get("results")[0].get("series")[0].get("values")
                    # convert to flow.txt
                    flowTxt = srcPort + "_" + dstPort + ".txt"
                    with io.open('/home/sdn/GrafanaData/influx/flow/' + flowTxt, 'w', encoding='utf8') as fw:
                        for result in results:
                            fw.write(result[0] + " " + str(result[1]) + " " + result[2] + '\n')
                    os.system("sudo chmod 777 /home/sdn/GrafanaData/influx/flow/" + flowTxt)
                    # Get the hop.json
                    nodes = file_name("/home/sdn/GrafanaData/influx/node", ".txt")
                    for hopId in (results[0][2].split(":")):
                        flag = False
                        if (len(nodes) == 0):
                            writeHopTxt(srcPort, dstPort, hopId)
                        else:
                            for node in nodes:
                                if hopId == node.split("/")[6].split(".txt")[0]:
                                    flag = True;
                                    break
                                if flag == False:
                                    writeHopTxt(srcPort, dstPort, hopId)
                except Exception as e:
                    print(str(e))
                    continue

def getNodeLatency():
    NodeMap = {"1": "0", "2": "0", "3": "0", "4": "0",
               "5": "0", "6": "0", "7": "0", "8": "0",
               "9": "0"}
    nodes = file_name("/home/sdn/GrafanaData/influx/node", ".txt")
    fo = open("/home/sdn/GrafanaData/latency.txt", 'w')
    for node in nodes:
        s = 0
        with io.open(node, 'r', encoding='utf8') as f:
            metrics = f.readlines()
            for i in range(len(metrics)):
                s = s + int(metrics[i].split(" ")[1].strip())
            s = int(s / len(metrics))
            fo.write(node.split(".txt")[0].split("/")[6] + ":" + str(s) + "\n")
    fo.close()
    for line in open("/home/sdn/GrafanaData/latency.txt"):
        node = line.strip().split(":")[0]
        latency = line.strip().split(":")[1]
        NodeMap[node] = latency
    # print(NodeMap)
    for key, value in NodeMap.items():
        if value == "0":
            fo = open("/home/sdn/GrafanaData/latency.txt", 'a')
            fo.write(key + ":" + value + "\n")

def writeLatencyToInfluxDB():
    timeStap = str(int(round(time.time() * 1000000000)))
    SRs = []
    # read the sr_new.txt, get two paths
    for line in open("/home/sdn/SRRRouting/sr_new.txt"):
        SRs.append(line)
    if len(SRs) != 2:
        print("no Grafana data!")
    else:
        sr1 = SRs[0].split(" ")[1 : -1]
        sr2 = SRs[1].split(" ")[1 : -1]
    path1 = convertSRToNum(sr1)
    path2 = convertSRToNum(sr2)
    path1.insert(0, '1')
    path1.insert(1, '2')
    path2.insert(0, '1')
    path2.insert(1, '2')
    # print(path1)
    # print(path2)
    latency1 = computeLatencyOfPath(path1)
    latency2 = computeLatencyOfPath(path2)
    # print(latency1)
    # print(latency2)
    # write latency to InfluxDB
    os.system("curl -i -XPOST \'http://localhost:8086/write?db=INTdatabase\' --data-binary \'latency,path_id=1 value=" + str(latency1) + " " + timeStap + "\'")
    os.system("curl -i -XPOST \'http://localhost:8086/write?db=INTdatabase\' --data-binary \'latency,path_id=2 value=" + str(latency2) + " " + timeStap + "\'")
    print("Grafana Data has been written!")

def convertSRToNum(sr):
    NodeMap = {"3:111:1::": "1", "3:111:2::": "2", "3:111:3::": "3", "3:111:4::": "4",
               "3:111:5::": "5", "3:111:6::": "6", "3:111:7::": "7", "3:111:8::": "8",
               "3:111:9::": "9"}
    for i in range(0, len(sr)):
        sr[i] = NodeMap[sr[i]]
    return sr

def computeLatencyOfPath(path):
    latency = 0
    LatencyMap = {}
    for line in open("/home/sdn/GrafanaData/latency.txt"):
        LatencyMap[line.split(":")[0]] = line.split(":")[1].strip()
    # print(LatencyMap)
    for node in path:
        latency = latency + int(LatencyMap[node])
    return latency

if __name__ == '__main__':
    while True:
        removeFiles("/home/sdn/GrafanaData/influx/node", ".txt")
        removeFiles("/home/sdn/GrafanaData/influx/json", ".json")
        removeFiles("/home/sdn/GrafanaData/influx/flow", ".txt")
        readFromInflux()
        getNodeLatency()
        writeLatencyToInfluxDB()
        time.sleep(latencyPeriod)
