import csv
#03 2206 Light-weight interaction

#column values from boris export
timeStamp = 0
eventName = 5
eventType = 8

#initializing rater 1
rater1 = {}
rater1["events"] = []
rater1["eventProfile"] = []

#initializing rater2
rater2 = {}
rater2["events"] = []
rater2["eventProfile"] = []

finalProfile = []

#collects all the event information from the file provided
def collectEvents(file, rater):
    #set the rater that we are collecting from
    r = rater2
    if rater == 1:
        r = rater1
    #opens the tsv and reads the lines
    with open(file) as tsv:
        for line in csv.reader(tsv, delimiter="\t"):
            event_data = {}
            #convert to float then floor
            event_data["eventName"] = line[eventName]
            event_data["timeStamp"] = int(float(line[timeStamp]))
            event_data["eventType"] = line[eventType]
            #add to events
            r["events"].append(event_data)

#find the events stop
def eventStop(r, e, pos):
    for x in range(pos, len(r["events"])):
        c = r["events"][x] #the event being checked
        if c["eventName"] == e["eventName"] and c["eventType"] == 'STOP':
            return c["timeStamp"]
    return -1

#creates a valid profile of the raters events that can be passed to SPSS
def createProfile(rater):
    #set the rater that we are collecting from
    r = rater2
    if rater == 1:
        r = rater1
    #loop through the raters logged events
    events = r["events"]
    for x in range(0,len(events)):
        e = events[x]
        #handle event start
        if e["eventType"] == 'START':
            startTime = e["timeStamp"]
            endTime = eventStop(r, e, x)
            assert (endTime != -1)
            for i in range(startTime, endTime):
                r["eventProfile"].append((i , e["eventName"]))

#aligns the two rater profiles based on time
def alignProfiles():
    #the positions in the arrays of rater events
    pos1 = 0
    pos2 = 0
    #the time that is being analyzed
    time = 0
    #the two end times for the two raters
    endTime1 = rater1["eventProfile"][len(rater1["eventProfile"]) - 1][0]
    endTime2 = rater2["eventProfile"][len(rater2["eventProfile"]) - 1][0]
    #the later of the two times
    #maxTime = max(endTime1, endTime2)
    maxTime = min(endTime1,endTime2)
    done1 = False
    done2 = False
    while time < maxTime:
        #set rater data
        rater_data = {}
        rater_data['rater 1'] = "None"
        rater_data['rater 2'] = "None"
        rater_data['time'] = "0"
        #Do not extend the bounds of any rater
        if pos1 >= len(rater1["eventProfile"]):
            done1 = True
            event1 = (0, "None")
        else:
            event1 = rater1["eventProfile"][pos1]

        if pos2 >= len(rater2["eventProfile"]):
            done2 = True
            event2 = (0, "None")
        else:
            event2 = rater2["eventProfile"][pos2]

        #if neither raters events are done
        if not done1 and not done2:
            time = min(event1[0],event2[0])
        elif done1:
            time = event2[0]
        elif done2:
            time = event1[0]

        #add the events to the rater data
        if event1[0] == time:
            rater_data['rater 1'] = event1[1]
            pos1 += 1
        if event2[0] == time:
            rater_data['rater 2'] = event2[1]
            pos2 += 1
        rater_data['time'] = time
        finalProfile.append(rater_data)

#compares two disagreements to determine if they are the same
def compare(dis1, dis2):
    if (dis1['rater 1'] == dis2['rater 1']) and (dis1['rater 2'] == dis2['rater 2']):
        return True
    else:
        return False

#resolves any Disagreements in the final profile
def resolveDis(file):
    file_name = "timeline_" + file + ".csv";
    with open(file_name, "w+") as output:
        fieldnames = ['time','decision']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        #the previous disagreement
        save_dis = {}
        #the current Disagreements
        dis = {}
        #accumulates the indeces which have already been logged
        acc = []
        disagreement = False
        #loop through all logs
        for x in range(0,len(finalProfile)):
            log = finalProfile[x]
            #if x has already been logged skip it
            if x in acc or (log['rater 1']=="None" or log['rater 2']=="None"):
                continue
            #the event that will be written to output
            e = {}
            e['time'] = int(log['time'])
            #if the raters agree then we can write the event
            if log['rater 1'] == log['rater 2']:
                e['decision'] = log['rater 1']
                disagreement = False
                writer.writerow(e)
            #the raters disagree
            else:
                disagreement = True
                #make an account of the disagreement
                dis['rater 1'] = log['rater 1']
                dis['rater 2'] = log['rater 2']
                save_dis['rater 1'] = log['rater 1']
                save_dis['rater 2'] = log['rater 2']

                endTime = -1
                duration = 0
                index = x
                while disagreement and (dis['rater 1'] == save_dis['rater 1'] and dis['rater 2'] == save_dis['rater 2']) and index < len(finalProfile):
                    acc.append(index)
                    duration += 1
                    endTime = int(finalProfile[index]['time'])
                    dis['rater 1'] = finalProfile[index]['rater 1']
                    dis['rater 2'] = finalProfile[index]['rater 2']
                    index += 1
                    if dis['rater 1'] == dis['rater 2']:
                            disagreement = False
                startTime = e['time']
                if (endTime - startTime) > 7:
                    #collect input from user
                    print("DISAGREEMENT")
                    print("starts at: " + str(startTime) + "\nlasts: " + str(duration) + " seconds")
                    print(save_dis)
                    dec = raw_input("Would you like to use rater 1 or 2? [1 / 2] \n")
                    if dec == "1":
                        e['decision'] = log['rater 1']
                    elif dec == "2":
                        e['decision'] = log['rater 2']
                else:
                    e['decision'] = log['rater 1']
                #from start index to final index
                for r in range(0,endTime - startTime):
                    #write the chosen
                    writer.writerow(e)
                    #correct time
                    e['time'] += 1

#collects the file name as input
startGroup = 10

endGroup = 21
for x in range(startGroup,endGroup+1):
    file_name = str(x)
    file_name_mod = file_name;
    if x < 10:
        file_name_mod = "0" + file_name;
    print("\n");
    print("STARTING GROUP: " + file_name_mod)
    collectEvents("Rater1/" + file_name_mod + ".tsv", 1)
    collectEvents("Rater2/" + file_name_mod + ".tsv", 2)
    createProfile(1);
    createProfile(2);
    alignProfiles();
    resolveDis(file_name_mod);
    #initializing rater 1
    rater1 = {}
    rater1["events"] = []
    rater1["eventProfile"] = []
    #initializing rater2
    rater2 = {}
    rater2["events"] = []
    rater2["eventProfile"] = []
    finalProfile = []
