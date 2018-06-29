## Random data generator for OEE scenario

###########################
# Configuration variables #
###########################

# Traceability
plant_trace = ['Main', 'Springfield']
workcenter_trace = ['A', 'B']
machine_trace = ['250', '350', '251', '351']
shift_trace = ['1', '2']
operator_trace = ['CGM', 'DC', 'TR', 'AD', 'DS', 'KG', 'RR', 'LM', 'JL', 'MM', 'RM', 'JM', 'JG', 'IK', 'KE', 'RH']

# Quality of work. These variables present different scenarios for data variation. Most will be good, a couple bad, and a couple great.
qual_of_work = {'good':[0,0], 'bad':[-.03,-.03], 'great':[.01,.01]}

# Combo for looping over the 16 operators with appropriate trace for each. 
# List is 'Plant', 'Workcenter', 'Machine', 'Shift', 'Operator'
combo_trace = [
    ['Main', 'A', '250', '1', 'CGM'], 
    ['Main', 'A', '250', '1', 'DC'],
    ['Main', 'A', '250', '2', 'TR'],
    ['Main', 'A', '250', '2', 'AD'],
    ['Main', 'B', '350', '1', 'DS'],
    ['Main', 'B', '350', '1', 'KG'],
    ['Main', 'B', '350', '2', 'RR'],
    ['Main', 'B', '350', '2', 'LM'],
    ['Springfield', 'A', '251', '1', 'JL'],
    ['Springfield', 'A', '251', '1', 'MM'],
    ['Springfield', 'A', '251', '2', 'RM'],
    ['Springfield', 'A', '251', '2', 'JM'],
    ['Springfield', 'B', '351', '1', 'JG'],
    ['Springfield', 'B', '351', '1', 'IK'],
    ['Springfield', 'B', '351', '2', 'KE'],
    ['Springfield', 'B', '351', '2', 'RH'],
    ]

# Misc variables
ideal_cycle_time = 0.055
scheduled_time = 720

#######################
# Top Level functions #
#######################

import random

def main():
    '''Loop over the combo_trace list to generate data for each operator for the past 90 days.'''
    for item in combo_trace:
        


main()