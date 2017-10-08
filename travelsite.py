from pymongo import MongoClient
from sparkpost import SparkPost

client = MongoClient('mongodb://daphne:password@ds036577.mlab.com:36577/traveldata')

db = client.traveldata
collection =db.cities
postId = db.cities.find()

def plan(cities, interests, numDays, budget, busy, ranking):
    data = getCityData(cities)
    filteredData = reduceByInterests(data, interests)
    cityEvents = filteredData[0]
    orderedEvents = filteredData[1]
    itinerary = {}
    start = 0
    for k in cityEvents.keys(): # for each city
        cityPlan = {} # all day plans for this city
        cityData = getCityData([k])
        for day in range(0, numDays): #for num Days
            retVal = makeDayPlan(cityEvents[k], orderedEvents[str(k)], cityData, busy, budget, ranking, interests) #make a plan
            cityPlan["day" + str(day + 1)]  = retVal[0]
            cityEvents[k] = {}
            orderedEvents[k] = retVal[2]
            for i in range(0, len(retVal[1])):
                cityEvents[k][orderedEvents[k][i]] = retVal[1][i]
        itinerary[k] = cityPlan #add city plan to iterinary
        start += len(cityEvents[k])
    sendEmail(itinerary)
    return itinerary



            

def makeDayPlan(cityFilteredEvents, orderedEventNames, cityData, busy, budget, ranking, interests):
    #returns plan for one day based on filtered cityData
    plan = {}
    runningBudget = budget
    cityData = cityData[0]
    sort = sortEventsByPrice(orderedEventNames, cityFilteredEvents)
    sortedCityEvents = sort[0]
    sortedEventNames = sort[1]
    if "nightlife" in interests:
        runningBudget -= float(cityFilteredEvents["nightlife"]["price"])
        runningBudget -= float((2 * cityData["beer"]))
    runningBudget -= float(cityData["cappuccino"])

    if ranking[2] == "accomodations":
        accom = cityData["accomodations"]
        plan["accomodations"] = "hostel"
        runningBudget -= float(accom["hostel"])
    if ranking[2] == "food":
        food = cityData["restaurants"]
        plan["breakfast"] = "budget breakfast"
        plan["lunch"] = "budget lunch"
        plan["dinner"] = "inexpensive dinner"
        runningBudget -= float(food["budgetbreakfast"]) 
        runningBudget -= float(food["budgetlunch"])     
        runningBudget -= float(food["inexpensive"])  
    if ranking[2] == "activities":         
        if busy == 0:
            end = 2
        elif busy == 1:
            end = 3
        else:
            busy = 5
        usedTypes = []
        i = 0

        if end > len(sortedCityEvents):
            return "We don't have that many events sorry!"

        for activity in range(0, end):
            while i < len(sortedEventNames) and sortedCityEvents[i]["type"] in usedTypes:
                i+=1
            if i == len(sortedCityEvents) and sortedCityEvents[i-1]["type"]  in usedTypes:
                i = 0
                usedTypes = []
            while i<len(sortedEventNames) and sortedCityEvents[i]["type"] in usedTypes:
                i+=1
    
            plan["activity " + str(activity + 1)] = sortedEventNames[i]
            runningBudget -=  float(sortedCityEvents[i]["price"])
            usedTypes.append(sortedCityEvents[i]["type"])
            sortedCityEvents.pop(i)
            sortedEventNames.pop(i)
        
        

    if ranking[1] == "accomodations":
        accom = cityData["accomodations"]
        plan["accomodations"] = "hostel"
        runningBudget -= float(accom["hostel"])

    if ranking[1] == "food":
        food = cityData["restaurants"]
        plan["breakfast"] = "budget breakfast"
        plan["lunch"] = "budget lunch"
        plan["dinner"] = "inexpensive dinner"
        runningBudget -= float(food["budgetbreakfast"])   
        runningBudget -= float(food["budgetlunch"])     
        runningBudget -= float(food["inexpensive"])
    if ranking[1] == "activities":         
        if busy == 0:
            end = 2
        elif busy == 1:
            end = 3
        else:
            busy = 5
        usedTypes = []
        i = 0
        if end > len(sortedCityEvents):
            return "We don't have that many events sorry!"
        for activity in range(0, end):
            while i < len(sortedEventNames) and sortedCityEvents[i]["type"] in usedTypes:
                i+=1
            if i == len(sortedCityEvents) and sortedCityEvents[i-1]["type"]  in usedTypes:
                i = 0
                usedTypes = []
            while i<len(sortedEventNames) and sortedCityEvents[i]["type"] in usedTypes:
                i+=1
    
            plan["activity " + str(activity + 1)] = sortedEventNames[i]
            runningBudget -=  float(sortedCityEvents[i]["price"])
            usedTypes.append(sortedCityEvents[i]["type"])
            sortedCityEvents.pop(i)
            sortedEventNames.pop(i)
    if runningBudget < 0:
        return "We cannot make a plan for this price in this city!"


    if ranking[0] == "accomodations":
        accom = cityData["accomodations"]
        if float(accom["four-starhotel"]) < runningBudget:
            plan["accomodations"] = "four-starhotel"
            runningBudget -= float(accom["four-starhotel"])
        elif float(accom["three-starhotel"]) < runningBudget:
            plan["accomodations"] = "three-starhotel"
            runningBudget -= float(accom["three-starhotel"])
        elif float(accom["hostel"]) < runningBudget:
            plan["accomodations"] = "hostel"
            runningBudget -= float(accom["hostel"])
        else:
             return "We cannot make a plan for this price in this city!"


    if ranking[0] == "food":
        food = cityData["restaurants"]
        plan["breakfast"] = "budget breakfast"
        plan["lunch"] = "budget lunch"
        runningBudget -= float(food["budgetbreakfast"])   
        runningBudget -= float(food["budgetlunch"]) 
        if float(food["midrange"]) < runningBudget:
            plan["dinner"] = "nice dinner"
            runningBudget -= float(food["midrange"]) 
        elif float(food["inexpensive"]) < runningBudget:
            plan["dinner"] = "inexpensive dinner"
            runningBudget -= float(food["inexpensive"]) 
        else:
             return "We cannot make a plan for this price in this city!"

    if ranking[0] == "activities":         
        if busy == 0:
            end = 2
        elif busy == 1:
            end = 3
        else:
            busy = 5
        usedTypes = []
        i = 0
        if end > len(sortedCityEvents):
            return "We don't have that many events sorry!"
        for activity in range(0, end):
            while i < len(sortedEventNames) and sortedCityEvents[i]["type"] in usedTypes:
                i+=1
            if i == len(sortedCityEvents) and sortedCityEvents[i-1]["type"]  in usedTypes:
                i = 0
                usedTypes = []
            while i<len(sortedEventNames) and sortedCityEvents[i]["type"] in usedTypes:
                i+=1
    
            plan["activity " + str(activity + 1)] = sortedEventNames[i]
            runningBudget -=  float(sortedCityEvents[i]["price"])
            usedTypes.append(sortedCityEvents[i]["type"])
            sortedCityEvents.pop(i)
            sortedEventNames.pop(i)


    if runningBudget > 0:
        if ranking[1] == "accomodations" and plan["accomodations"] != "four-starhotel":
            accom = cityData["accomodations"]
            if float(accom["four-starhotel"]) < runningBudget:
                if (plan["accomodations"] == "hostel"):
                    plan["accomodations"] = "four-starhotel"
                    runningBudget -= float(accom["four-starhotel"]) - float(accom["hostel"])
                else:
                    plan["accomodations"] = "four-starhotel"
                    runningBudget -= float(accom["three-starhotel"]) - float(accom["hostel"])
            elif float(accom["three-starhotel"]) < runningBudget:
                plan["accomodations"] = "three-starhotel"
                runningBudget -= float(accom["three-starhotel"])

        if ranking[1] == "food" and plan["dinner"] != "nice dinner":
            if cityData["restaurants"]["midrange"] < runningBudget:
                plan["dinner"] = "nice dinner"
                runningBudget -= float(cityData["restaurants"]["midrange"]) - float(cityData["restaurants"]["inexpensive"])

        if ranking[2] == "accomodations" and plan["accomodations"] != "four-starhotel":
            accom = cityData["accomodations"]
            if float(accom["four-starhotel"]) < runningBudget:
                if (plan["accomodations"] == "hostel"):
                    plan["accomodations"] = "four-starhotel"
                    runningBudget -= float(accom["four-starhotel"]) - float(accom["hostel"])
                else:
                    plan["accomodations"] = "four-starhotel"
                    runningBudget -= float(accom["three-starhotel"]) - float(accom["hostel"])
            elif float(accom["three-starhotel"]) < runningBudget:
                plan["accomodations"] = "three-starhotel"
                runningBudget -= float(accom["three-starhotel"])

        if ranking[2] == "food" and plan["dinner"] != "nice dinner":
            if cityData["restaurants"]["midrange"] < runningBudget:
                plan["dinner"] = "nice dinner"
                runningBudget -= float(cityData["restaurants"]["midrange"]) - float(cityData["restaurants"]["inexpensive"])

    plan["cost"] = budget - runningBudget
    return (plan, sortedCityEvents, sortedEventNames)

def sortEventsByPrice(sortedEventNames, cityEvents):
    result = []
    resultNames = []
    temp = [cityEvents[sortedEventNames[0]]]
    tempNames = [sortedEventNames[0]]
    i = 1
    while i < len(cityEvents):
        if sortedEventNames[i] == "nightlife":
            print(cityEvents)
        if cityEvents[sortedEventNames[i]]["type"] == temp[0]["type"]:
            count = 0
            while count < len(temp) and cityEvents[sortedEventNames[i]]["price"] < temp[count]["price"]:
                count+=1
            temp = temp[0:count] + [cityEvents[sortedEventNames[i]]] + temp[count:]  
            tempNames = tempNames[0:count] + [sortedEventNames[i]] + tempNames[count:]   
        else:
            result += temp
            resultNames += tempNames
            temp = [cityEvents[sortedEventNames[i]]]
            tempNames = [sortedEventNames[i]]

        if i == len(sortedEventNames) -1:
            result += temp
            resultNames += tempNames
        i += 1
   
    return result, resultNames

def getCityData(cities):
    data = []
    if (len(cities) == 0):
        data = db.cities.find()
    else:
        for c in cities:
            data += db.cities.find({"name": c})
    return data

temp = getCityData(["Paris"])[0]["accomodations"]



def reduceByInterests(cityData, interests):
    filteredData = {} #final return value
    sortedNames = {}
    for d in cityData: #go through each city
        city = {} #filtered data for one city
        names = []
        for i in interests:
            for m in d["museums"]:
                if m["type"] == "modern" and "modern art" == i:
                    city[m["name"]] =  {"price": m["price"], "type":"modern"}
                    names += [m["name"]]
                if m["type"] == "historic" and "historic art" == i:
                    names += [m["name"]]
                    city[m["name"]] =  {"price": m["price"], "type": "historic"}

            for s in d["sites"]:
                if s["type"] == i:
                    names += [s["name"]]
                    city[s["name"]] = {"price": s["price"], "type": i}
            
            if "nightlife" == i:
                names += ["nightlife"]
                city["nightlife"] = {"price": d["nightlife"], "type": i}

        sortedNames[d["name"]] = names            
        filteredData[d["name"]] = city
    return (filteredData, sortedNames)

def sendEmail(plan):
    emailtext = "Hello daphne \n This is your travel plan: \n" 

    for key in plan.keys():
        citytext = ""
        cityName = key
        cityPlan = plan[key]
        citytext += cityName + ": \n"
        for day in cityPlan.keys():
            citytext += "day " + str(day) + ": \n"
            dayPlan = cityPlan[day]
            for event in dayPlan.keys():
                temp =  event + ": " + str(dayPlan[event]) + " \n"
                citytext += temp

        emailtext += citytext + " \n \n"
    print(emailtext)
    sp = SparkPost('3fde7f3ebdbfee6fb82b7fdef81530735a54e44f')
    response = sp.transmissions.send(
    recipients=[
        "dnhuch@berkeley.edu"
      
       ],
     reply_to='no-reply@sparkpostmail.com',

    text=emailtext,
    from_email='dnhuch@fin-venture.org',
    subject='Your Travel Plans'
   
    )
print(plan(["Paris"], ["historic art", "nightlife"], 1, 300,0, ["food", "accomodations", "activities"]))
