import math
import csv
import statistics
import os.path
import time
import gurobipy
import numpy as np
from argparse import ArgumentParser
import uuid

EPSILON = 0.00001
    

#%%
def getValuePerEngagement(advertiser):
    return advertiser.value_per_engagement


def getValue(advertiser):
    return advertiser.value()


def getSpread(element):
    return element[0]


def maximizeGroupRevenue(advertisers_list, weighted, extended, approximation_tolerance):
    if extended:
        return maximizeGroupRevenueExtended(advertisers_list, weighted, approximation_tolerance)
    elif weighted:
        return maximizeGroupRevenueWeighted(advertisers_list)
    else:
        return maximizeGroupRevenueUnweighted(advertisers_list)


def maximizeGroupRevenueWeighted(advertisers_list):

    advertisers_list.sort(key=getValue, reverse=True)

    index = 0
    total_budget = 0

    while index < len(advertisers_list) and total_budget < advertisers_list[index].value() / 2.0:
        index += 1
        total_budget += advertisers_list[index-1].budget

    return_index = max(index - 1, 0)

    return advertisers_list[return_index].value_per_engagement, advertisers_list[return_index].value()


def maximizeGroupRevenueExtended(advertisers_list, weighted, approximation_tolerance):

    double_advertisers_list = list(advertisers_list)
    # duplicate
    for advertiser in advertisers_list:
        double_advertisers_list.append(Advertiser(advertiser.value_per_engagement, advertiser.budget, dict(advertiser.spread_dict)))

    if weighted:
        double_advertisers_list.sort(key=getValue, reverse=True)
    else:
        double_advertisers_list.sort(key=getValuePerEngagement, reverse=True)

    max_index = 0
    max_revenue = 0
    
    for index in range(1, len(double_advertisers_list), 2):

        revenue = 0
        
        revenue, _ = allocateExtended(double_advertisers_list[:(index+1)], [], 0, double_advertisers_list[index].value_per_engagement, 0, double_advertisers_list[index].value(), weighted, False, approximation_tolerance)

        if revenue > max_revenue:
            max_revenue = revenue
            max_index = index

    return double_advertisers_list[max_index].value_per_engagement, double_advertisers_list[max_index].value()


def maximizeGroupRevenueUnweighted(advertisers_list):

    advertisers_list.sort(key=getValuePerEngagement, reverse=True)

    index = 0
    total_budget = 0
    half_spread = sum([sum(advertisers_list[i].spread_dict.values()) for i in range(0, index + 1)]) / (2.0*(index + 1))
    
    while index < len(advertisers_list) - 1 and total_budget < advertisers_list[index].value_per_engagement * half_spread:
        index += 1
        total_budget += advertisers_list[index-1].budget
        half_spread = sum([sum(advertisers_list[i].spread_dict.values()) for i in range(0, index + 1)]) / (2.0*(index + 1))

    return_index = max(index - 1, 0)

    return advertisers_list[return_index].value_per_engagement, advertisers_list[return_index].value()


def getPrice(advertiser, value_a, value_b, value_per_engagement_a, value_per_engagement_b, advertisers_a, advertisers_b, weighted, non_truthful):
    total_spread = sum(advertiser.spread_dict.values())
    
    price = 0
    
    if total_spread > 0:
        if advertiser in advertisers_a:
            if weighted:
                if non_truthful:  # non-truthful auction is deriving the price from the same group
                    price =  value_a / total_spread
                else:  # truthful auction is deriving the price from the other group
                    price =  value_b / total_spread
            else:
                if non_truthful:
                    price = value_per_engagement_a
                else:
                    price = value_per_engagement_b
        else:
            if weighted:
                if non_truthful:
                    price =  value_b / total_spread
                else:
                    price = value_a / total_spread
            else:
                if non_truthful:
                    price = value_per_engagement_b
                else:
                    price = value_per_engagement_a

    return price


def allocate(advertisers_a, advertisers_b, value_per_engagement_a, value_per_engagement_b, value_a, value_b, weighted, extended, non_truthful, approximation_tolerance, allocation_random_state):
    if extended:
        return allocateExtended(advertisers_a, advertisers_b, value_per_engagement_a, value_per_engagement_b, value_a, value_b, weighted, non_truthful, approximation_tolerance)
    else:
        return allocateRandom(advertisers_a, advertisers_b, value_per_engagement_a, value_per_engagement_b, value_a, value_b, weighted, non_truthful, allocation_random_state)


def allocateExtended(advertisers_a, advertisers_b, value_per_engagement_a, value_per_engagement_b, value_a, value_b, weighted, non_truthful, approximation_tolerance):
    advertisers = advertisers_a + advertisers_b
    for advertiser in advertisers:
        advertiser.resetRemainingBudget()

    revenue = 0
    social_welfare = 0

    if len(advertisers) > 0:

        try:
            model = gurobipy.Model("auction")
            model.Params.MIPGap = approximation_tolerance

            vars = {}

            # determine eligible advertisers
            eligible_advertisers = []
            for advertiser in advertisers:
                price = getPrice(advertiser, value_a, value_b, value_per_engagement_a, value_per_engagement_b, advertisers_a, advertisers_b, weighted, non_truthful)
                if price <= advertiser.value_per_engagement + EPSILON:
                    eligible_advertisers.append(advertiser)

            # create variables
            for seeder in advertisers[0].spread_dict.keys():
                if seeder not in vars:
                    vars[seeder] = {}
                for advertiser in eligible_advertisers:
                    vars[seeder][advertiser.id] = model.addVar(vtype=gurobipy.GRB.BINARY, name=advertiser.id)

            # constraints: seeders can only be allocated to one advertiser
            for seeder in vars.keys():
                lefthandside = None
                for advertiser in eligible_advertisers:
                    if lefthandside:
                        lefthandside += vars[seeder][advertiser.id]
                    else:
                        lefthandside = vars[seeder][advertiser.id]

                model.addConstr(lefthandside <= 1)

            # constraints: advertisers can not spend more than their budget
            # objective: maximize revenue
            objective = None
            for advertiser in eligible_advertisers:
                price = getPrice(advertiser, value_a, value_b, value_per_engagement_a, value_per_engagement_b, advertisers_a, advertisers_b, weighted, non_truthful)
                lefthandside = None
                for seeder in advertiser.spread_dict.keys():
                    value = price * advertiser.spread_dict[seeder] * vars[seeder][advertiser.id]
                    lefthandside += value
                    objective += value

                    model.update()
                    
                model.addConstr(lefthandside <= advertiser.budget)

            model.setObjective(objective, gurobipy.GRB.MAXIMIZE)
            
            model.optimize()
            
            # revenue and social welfare
            for seeder in advertisers[0].spread_dict.keys():
                for advertiser in eligible_advertisers:
                    if math.isclose(vars[seeder][advertiser.id].X, 1, abs_tol=EPSILON):
                        price = getPrice(advertiser, value_a, value_b, value_per_engagement_a, value_per_engagement_b, advertisers_a, advertisers_b, weighted, non_truthful)
                        revenue += price * advertiser.spread_dict[seeder]
                        social_welfare += advertiser.value_per_engagement * advertiser.spread_dict[seeder]

        except gurobipy.GurobiError as error:
            print('Gurobi reported an error:')
            print(error)

    return revenue, social_welfare


def allocateRandom(advertisers_a, advertisers_b, value_per_engagement_a, value_per_engagement_b, value_a, value_b, weighted, non_truthful, allocation_random_state):
    advertisers = advertisers_a + advertisers_b
    for advertiser in advertisers:
        advertiser.resetRemainingBudget()

    seeders = list(advertisers[0].spread_dict.keys())
    allocation_random_state.shuffle(seeders)

    revenue = 0
    social_welfare = 0

    for seeder in seeders:
        
        # find an advertiser who can afford the seeder

        allocated = False
        
        # create a new random sequence for allocation
        allocation_random_state.shuffle(advertisers)

        for advertiser in advertisers:
            if not allocated:
                price = getPrice(advertiser, value_a, value_b, value_per_engagement_a, value_per_engagement_b, advertisers_a, advertisers_b, weighted, non_truthful)
                if price > 0:            
                    # check if advertiser can afford the price
                    payment = price * advertiser.spread_dict[seeder]
                    if price <= advertiser.value_per_engagement + EPSILON and payment <= advertiser.remaining_budget:
                        advertiser.remaining_budget -= payment
                        revenue += payment
                        social_welfare += advertiser.value_per_engagement * advertiser.spread_dict[seeder]
                        allocated = True
                        break

    return revenue, social_welfare


class Advertiser(object):
    def __init__(self, value_per_engagement, budget, spread_dict):
        self.value_per_engagement = value_per_engagement
        self.budget = budget
        self.spread_dict = dict(spread_dict)
        self.resetRemainingBudget()
        self.id = str(uuid.uuid4())

    def resetRemainingBudget(self):
        self.remaining_budget = self.budget

    def value(self):
        return self.value_per_engagement * sum(self.spread_dict.values())


def loadData(path, spread_filename, advertisers_filename, count_seeder):
    spread_list = []
    with open(path + spread_filename) as input_file:
        input_reader = csv.reader(input_file, delimiter=',')

        for row in input_reader: 
            advertiser = int(row[0])
            seeder = int(row[1])
            spread = float(row[2])

            while len(spread_list) <= advertiser:
                spread_list.append({})

            if count_seeder:
                spread += 1
            spread_list[advertiser][seeder] = spread

    advertisers_list = []
    with open(path + advertisers_filename) as input_file:
        input_reader = csv.reader(input_file, delimiter=',')

        index = 0
        for row in input_reader:
            value_per_engagement = float(row[0])
            budget = float(row[1])
            advertisers_list.append(Advertiser(value_per_engagement, budget, spread_list[index]))
            index += 1

    return advertisers_list


def runAuction(advertisers_list, output, approximation_tolerance, group_seed, random_allocation_seed, weighted, extended, count_seeder, non_truthful, iterations):
    
    # Two random state for group-split and random allocation
    group_random_state = np.random.RandomState(group_seed)
    allocation_random_state = np.random.RandomState(random_allocation_seed)
    
    write_header = False
    if not os.path.exists(output):
        write_header = True

    with open(output, 'a', newline='') as output_file:

        output_writer = csv.writer(output_file, delimiter=',')

        revenue_list = []
        social_welfare_list = []
        runtime_list = []

        start = time.time()

        for i in range(iterations):
            number_of_advertisers = len(advertisers_list)
            group_random_state.shuffle(advertisers_list)

            # randomly break tie if number_of_advertisers is odd
            if group_random_state.uniform(0, 1) < 0.5:
                advertisers_a = advertisers_list[:int(number_of_advertisers/2)]
                advertisers_b = advertisers_list[int(number_of_advertisers/2):]
            else:
                advertisers_b = advertisers_list[:int(number_of_advertisers/2)]
                advertisers_a = advertisers_list[int(number_of_advertisers/2):]

            value_per_engagement_a, value_a = maximizeGroupRevenue(advertisers_a, weighted, extended, approximation_tolerance)
            value_per_engagement_b, value_b = maximizeGroupRevenue(advertisers_b, weighted, extended, approximation_tolerance)
            revenue, social_welfare = allocate(advertisers_a, advertisers_b, value_per_engagement_a, value_per_engagement_b, value_a, value_b, weighted, extended, non_truthful, approximation_tolerance, allocation_random_state)

            revenue_list.append(revenue)
            social_welfare_list.append(social_welfare)

            runtime_list.append(time.time() - start)

        runtime_mean = (time.time() - start) / iterations

        if write_header:
            output_writer.writerow(("advertisers", "iterations", "spread", "weighted", "mode", "revenue", "sw", "runtime_accumulated", "runtime_mean", "group_seed", "random_allocation_seed"))
        mode = "random"
        if extended:
            mode = "extended"
        if non_truthful:
            mode = "bound"
        for i in range(len(revenue_list)):
            output_writer.writerow((advertisers_filename, iterations, spread_filename, weighted, mode, revenue_list[i], social_welfare_list[i], runtime_list[i], runtime_mean, group_seed, random_allocation_seed))


if __name__ == '__main__':

    # Set defaults
    path = "Data/Synthetic/"
    spread_filename = "influence=random(0,2000)_n=100.csv"
    advertisers_filename = "value=random(0,1)_b=5000_n=100.csv"
    iterations = 1
    output = "Data/Results/results.csv"
    approximation_tolerance = 0.05
    group_seed = None
    random_allocation_seed = None

    # Parse command line arguments
    parser = ArgumentParser()
    parser.add_argument("-p", "--path", default=path)
    parser.add_argument("-w", "--weighted", action="store_true")
    parser.add_argument("-s", "--spread",  default=spread_filename)
    parser.add_argument("-e", "--extended",  action="store_true")
    parser.add_argument("-i", "--iterations",  default=iterations, type=int)
    parser.add_argument("-o", "--output",  default=output)
    parser.add_argument("-a", "--advertisers",  default=advertisers_filename)
    parser.add_argument("-t", "--tolerance",  default=approximation_tolerance)
    parser.add_argument("-n", "--nontruthful",  action="store_true")
    parser.add_argument("-g", "--groupseed", default=group_seed)
    parser.add_argument("-r", "--randomallocationseed", default=random_allocation_seed)
    parser.add_argument("-c", "--countseeder", action="store_true")

    args = parser.parse_args()
    path = args.path
    spread_filename = args.spread
    output = args.output
    advertisers_filename = args.advertisers
    iterations = args.iterations
    approximation_tolerance = float(args.tolerance)
    group_seed = int(args.groupseed)
    random_allocation_seed = int(args.randomallocationseed)
    weighted = False
    if args.weighted:
        weighted = True
    extended = False
    if args.extended:
        extended = True
    non_truthful = False
    if args.nontruthful:
        non_truthful = True
    count_seeder = False
    if args.countseeder:
        count_seeder = True

    # Create advertisers from file
    advertisers_list = loadData(path, spread_filename, advertisers_filename, count_seeder)

    # Run auction
    runAuction(advertisers_list, output, approximation_tolerance, group_seed, random_allocation_seed, weighted, extended, count_seeder, non_truthful, iterations)
