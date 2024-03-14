# this is created slightly different using different variables
# todo: check if priority queue is properly working (in this case, taking the miniumum value at INDEX 1)
# todo: play around with heurisitc numbers (add a heuristic for movie)

import queue

class Butler:
    def __init__(self):

        # Constants for energy consumption (adjust as needed)
        self.ENERGY_CONSUMPTION = {
            'L1': 0.5,  # Energy consumption rate for light fixture L1
            'L2': 0.7,  # Energy consumption rate for light fixture L2
            'L3': 0.6,  # Energy consumption rate for light fixture L3
            'L4': 0.8   # Energy consumption rate for light fixture L4
        }

        # Constants, we can change later -- best way for now is increase or decrease certain light by 1
        # RESTINC = 2
        # BRIGHTINC = 3
        # DIMC = 5
        self.MAXBRIGHTNESS = 10
        self.MINBRIGHTNESS = 0
        self.EFFICIENCY = 0.05 # use later

        self.lights = ['L1', 'L2', 'L3', 'L4']

#IDEA: MAKE TWO HEURISTIC INTENSITY BRIGHTNESSES -- ONE WHERE OUTSIDE BRIGHTNESS PLAYS EFFECT AND
        #-- ONE WHERE OUTSIDE BRIGHTNESS PLAYS NO EFFECT

        #based off checking the location of light relative to action
        #we are also basing off light based off outside 
        self.heuristics_sleep = {
            'L1' : 0.26,
            'L2' : 0.04,
            'L3' : 0.35,
            'L4' : 0.35,
            'W1' : 0.7, 
            'W2' : 0.4
        }

        #all values should add up to 1
        self.heuristics_study = {
            'L1' : 0.26,
            'L2' : 0.7,
            'L3' : 0.03,
            'L4' : 0.01,
            'W1' : 0.7,
            'W2' : 0.3
        }

        #this is slightly ambiguous -- we can assume the user is listening to music in couch
        self.heuristics_music = {
            'L1' : 0.1,
            'L2' : 0.4,
            'L3' : 0.4,
            'L4' : 0.1,
            'W1' : 0.5,
            'W2' : 1

        }

        #another ambigous one, the user is cleaning the ENTIRE room, hence it may want the brightness to be uniform
        self.heuristics_clean = {
            'L1' : 0.4,
            'L2' : 0.2,
            'L3' : 0.2,
            'L4' : 0.2,
            'W1' : 0.7,
            'W2' : 0.7
        }

    def getCost(self, lights):
        #the cost is based on individual light intensities, and energy consumption rate (closer to 1 -- higher consumption rate, closer to 0 -- lower consumption rate)
        cost = self.ENERGY_CONSUMPTION['L1']*lights['L1'] + self.ENERGY_CONSUMPTION['L2']*lights['L2'] + self.ENERGY_CONSUMPTION['L3']*lights['L3'] + self.ENERGY_CONSUMPTION['L4']*lights['L4']
        return cost

    def getTotalBrightness(self, lightLevels, shutter_status, outside, intensity):
        if (shutter_status) == True:
            status = 0
        else:
            status = 1

        # figure out intensity scaling such that maxTotal brightness is no greater than 10 because no less that 0
        totalBrightness = intensity['L1']*lightLevels['L1'] + intensity['L2']*lightLevels['L2'] + intensity['L3']*lightLevels['L3'] + intensity['L4']*lightLevels['L4'] + intensity['W1']*outside*status + intensity['W2']*outside*status   
        print(f"total brightness: {totalBrightness}")
        print(f"brightness: {round(totalBrightness)}")
        #avoids values from going out of range
        return [round(min(self.MAXBRIGHTNESS, max(self.MINBRIGHTNESS, totalBrightness))), totalBrightness]
    
    def heuristic_function(self, state, target_brightness, outside_brightness):
        # Calculate heuristic value based on factors like distance from target brightness,
        # outside brightness, and current light levels in the room
        distance_to_target = abs(target_brightness - state)
        
        print(f"distance to target: {distance_to_target}")
        return distance_to_target

    # idea: add each device by 1 until we get to goal -- this might not be as efficient but is pretty accurate (we can change this later based on other heuristics)

    #this is just a modified version of UFS with the heuristics
    def AStarLight(self, initialLights, targetBrightness, outsideBrightness, option, shutter_status):
        #gets the intensity per light heuristic
        if (option == 'sleep'):
            intensity = self.heuristics_sleep
        elif (option == 'study'):
            intensity = self.heuristics_study
        elif (option == 'music'):
            intensity = self.heuristics_music
        elif (option == 'clean'):
            intensity = self.heuristics_clean


        #implementation of priority queue
        q = queue.PriorityQueue()

        # keeps track of min cost at that brightness -- our goal is to make sure that cost is min at that brightness level
        minCosts = {brightness: float('inf') for brightness in range(self.MAXBRIGHTNESS)}

        brightnessStats = self.getTotalBrightness(initialLights, shutter_status, outsideBrightness, intensity)
        print(f"current brightness: {brightnessStats[0]}")
        nextCost = self.getCost(initialLights)
        nextH = self.heuristic_function(brightnessStats[1], targetBrightness, outsideBrightness)
        totCost = nextCost+nextH 
        print(f"total cost: {totCost}")
        minCosts[brightnessStats[0]] = totCost
        q.put((totCost,brightnessStats[0],"", initialLights))

        counter  = 1


        #terminates before getting to curr[1] == targetBrightness
        while not q.empty():
            flag = -1
            #get the min element using the priorty queue -> use the heapq library
            curr = q.get()
            
            print(f"currenr state: {curr}")
            #case 1: reached total brightness
            if curr[1] == targetBrightness:
                print(f"final queue: {curr}")
                return [curr[3], False] #gets the light fixture brightnesses and False shutter status
            
            # case 2: lights are minimized, but target brightness cannot be reached
            if curr[1] > targetBrightness and curr[3]['L1'] == 0 and curr[3]['L2'] == 0 and curr[3]['L3'] == 0 and curr[3]['L4'] == 0:
                return [curr[3], True] #gets the light fixture brightnesses and True shutter status
            

            #edge case -> queue before reaching target brightness (we will prioritize user preference of efficiency)
            if (q.empty() and counter == 2):
                flag = 0

            counter = 2

            #traverse through all the lights in the smart home
            for light, brightness in curr[3].items():
                print(light)

                

                next_state = dict(curr[3])

                # we are going to assume next brightness will get -- for now curr[3] = listOfLights -- we are going to increase one of the lights by 1 or -1 depending on current status
                if curr[1] < targetBrightness:
                    next_state[light] += 1
                elif curr[1] > targetBrightness:
                    next_state[light] -= 1

                print(next_state)
                brightnessStats = self.getTotalBrightness(next_state, shutter_status, outsideBrightness, intensity)
                
                
                nextCost = self.getCost(next_state)  
                nextH = self.heuristic_function(brightnessStats[1], targetBrightness, outsideBrightness)
                totCost = nextCost+nextH                 #calculate f=g+h -> cost to reach node + additional heuristic cost. also, energy efficiency but it shouldnt have as much of an impact on the next choice as reaching the goal quickly should
                print(f"total cost: {totCost}")
                # where totCost = f(n), nextH = remaining brightness, (lets not use efficiency yet)
                
                print(f"minCost: {minCosts[brightnessStats[0]]}")
                if totCost < minCosts[brightnessStats[0]]:                    #if we previously had a less effective way to reach this temperature, replace it with this way. if there is already a more effective way to reach this point, don't bother continuing this path
                    minCosts[brightnessStats[0]] = totCost
                    if brightnessStats[0] >= self.MINBRIGHTNESS and brightnessStats[0] <= self.MAXBRIGHTNESS:
                        #to do - make a list of values to add and subtract in order to get total cost
                        # priority queue:
                        # value 1: total cost -- this should get min every time
                        # value 2: current brightness
                        # value 3: path for queue
                        # value 4: light values
                        print(f"1 nextBrightness: {brightnessStats[0]}")
                        print(f"1 total cost: {totCost}")
                        print(f"1 next state: {next_state}")
                        q.put((totCost, brightnessStats[0],curr[2]+ " --> " +str(light), next_state))
                #edge case --> queue is going to run out of options, start considering all children
                elif flag == 0:
                    print("here")
                    if brightnessStats[0] >= self.MINBRIGHTNESS and brightnessStats[0] <= self.MAXBRIGHTNESS:
                        q.put((totCost, brightnessStats[0],curr[2]+ " --> " +str(light), next_state))

#note - these variable will change since they will be based by gui
targetBrightness = 5 #this is will change later
outsideBrightness = 1
initialLights = {'L1': 0, 'L2': 0, 'L3': 0, 'L4': 0}
option = 'study'
shutter_status = False #assume shutters are open -- 
butler = Butler()
result = butler.AStarLight(initialLights, targetBrightness, outsideBrightness, option, shutter_status)
print(result)

