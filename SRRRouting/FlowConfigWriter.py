# coding=utf-8
# !/usr/bin/python

if __name__ == '__main__':
    fo = open("/home/sdn/SRRRouting/flowConfig.txt", 'w')
    num = 0
    for line in open("/home/sdn/Desktop/iperf.txt"):
        flowTxt = []
        if num == 5:
            break
        elif " "  in line:
            strs = line.strip().split(" ")
            for i in range(0, len(strs)):
                if strs[i] == "local":
                    flowTxt.append("10.1.1.1")
                    flowTxt.append(strs[i + 3])
                    flowTxt.append("10.1.5.1")
                    flowTxt.append("5001")
                    print(flowTxt)
                    for item in flowTxt:
                        fo.write(item + " ")
                    fo.write("\n")
                    num = num + 1
        else:
            continue
    fo.close()