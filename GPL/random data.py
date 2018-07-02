""" Random data generator for OEE scenario """

###########################
# Configuration variables #
###########################

# Traceability - (this block is for documentation)
plant_trace = ['Main', 'Springfield']
workcenter_trace = ['A', 'B']
machine_trace = ['250', '350', '251', '351']
shift_trace = ['1', '2']
operator_trace = ['CGM', 'DC', 'TR', 'AD', 'DS', 'KG', 'RR', 'LM', 'JL', 'MM', 'RM', 'JM', 'JG', 'IK', 'KE', 'RH']

# Combo for looping over the 16 operators with appropriate trace for each. 
# List is 'Plant', 'Workcenter', 'Machine', 'Shift', 'Operator', 'Target'
# Target sets the quality of the work for the given operator/trace combo. Simple ranking of Good, Great, Bad.

combo_trace = [
    ['Main', 'A', '250', '1', 'CGM', 'good'], 
    ['Main', 'A', '250', '1', 'DC', 'good'],
    ['Main', 'A', '250', '2', 'TR', 'good'],
    ['Main', 'A', '250', '2', 'AD', 'great'],  # individual operator performing well
    ['Main', 'B', '350', '1', 'DS', 'good'],
    ['Main', 'B', '350', '1', 'KG', 'good'],
    ['Main', 'B', '350', '2', 'RR', 'good'],
    ['Main', 'B', '350', '2', 'LM', 'good'],
    ['Springfield', 'A', '251', '1', 'JL', 'bad'], # machine 251 has issues
    ['Springfield', 'A', '251', '1', 'MM', 'bad'],
    ['Springfield', 'A', '251', '2', 'RM', 'bad'],
    ['Springfield', 'A', '251', '2', 'JM', 'bad'],
    ['Springfield', 'B', '351', '1', 'JG', 'good'],
    ['Springfield', 'B', '351', '1', 'IK', 'good'],
    ['Springfield', 'B', '351', '2', 'KE', 'good'],
    ['Springfield', 'B', '351', '2', 'RH', 'good'],
    ]

# trace to UDL mapping
udl = {'shift':2, 'workcenter':3, 'machine':4, 'plant':5, 'operator':6, 'available':9, 'scheduled':10, 'good_parts':11, 'total_parts':12, 'ideal_cycle_time':13}

# Misc variables 
ideal_cycle_time = 0.055
scheduled_time = 720

# Defect lists - logic starts at the beginning and loops over each. Put them in order from most common to least common. 
downtime_defects = ['Startup', 'Changeover', 'Lack of raw material', 'Machine issue', 'Other']
quality_defects = ['Heavy', 'Broken', 'Crack', 'Damaged', 'Loose', 'Bad part']

#######################
# Top Level functions #
#######################

import random, datetime

def main():
    """ Loop over the combo_trace list to generate data for each operator for the past 90 days. """ 
    for item in combo_trace:
        store_OEE(item, udl)

###############################
# Store OEE for each operator #
###############################

def store_OEE(trace, udl):
    """ Store OEE data with downtime defects. Set the traceability, part number, process, generate data, and then store """
    
    # reset oee_values to blank
    oee_values = [] 
    oee_trace_values = []
    
    # set the traceability for this loop
    datadms.settrace(udl['shift'], trace[3])
    datadms.settrace(udl['workcenter'], trace[1])
    datadms.settrace(udl['machine'], trace[2])
    datadms.settrace(udl['plant'], trace[0])
    datadms.settrace(udl['operator'], trace[4]) 
    
    # set date time for today, generate and store data, then loop for 90 days prior.
    start_date = datetime.datetime.now()
    for cnt in range(91):
    	# clear the OEE traceabilty fields
    	datadms.settrace(udl['scheduled'], '')
    	datadms.settrace(udl['available'], '')
    	datadms.settrace(udl['good_parts'], '')
    	datadms.settrace(udl['total_parts'], '')
    	datadms.settrace(udl['ideal_cycle_time'], '')
    	
    	date = start_date - datetime.timedelta(days=cnt)
    	# set the time stamp depending on shift 1 or 2.
    	if trace[3] == 1:
    		time = ' 8:00:00.0'
    	else:
    		time = ' 20:00:00.0'
    	datadms.datetime = date.strftime('%Y-%m-%d') + time
    	
    	# assign random OEE values for this row, passing in good, great, bad value
    	oee_values = generate_oee_values(trace[5]) 
    	# calculate the OEE values that need to be used for these percentages
    	oee_trace_values = generate_oee_trace_values(oee_values)
    	
    	datadms.process = 'Molding'
    	# set the part number based on the workcenter
    	if trace[1] == 'A': 
    		datadms.partno = '20 OZ' # workcenter A does 20oz bottles
    	elif trace[1] == 'B':
    		datadms.partno = '2 L' # workcenter B does 2L bottles
    	
    	# store quality defects with a random defect
    	bad_parts = oee_trace_values[3] - oee_trace_values[2]
    	set_defects(quality_defects, bad_parts) 	
    	datadms.setdefectcnt(1, bad_parts)
    	datadms.samplesize = oee_trace_values[3]
    	datadms.ncu = bad_parts
    	datadms.store()
    
    	# store OEE record with downtime reasons as defects.
    	# set the OEE traceabilty fields
    	datadms.settrace(udl['scheduled'], str(oee_trace_values[0]))
    	datadms.settrace(udl['available'], str(oee_trace_values[1]))
    	datadms.settrace(udl['good_parts'], str(oee_trace_values[2]))
    	datadms.settrace(udl['total_parts'], str(oee_trace_values[3]))
    	datadms.settrace(udl['ideal_cycle_time'], str(oee_trace_values[4]))
    	
    	downtime = oee_trace_values[0] - oee_trace_values[1]
    	set_defects(downtime_defects, downtime)
    	datadms.setdefectcnt(1, downtime)
    	datadms.process = 'OEE'
    	datadms.samplesize = oee_trace_values[0]
    	datadms.ncu = downtime
    	datadms.store()
    
    datadms.clear()

##########################
# Random data generation #
##########################

def generate_oee_values(rating):
	""" This function contains the definition of good, great, bad OEE values. Then it randomly generates OEE values from those parameters
		and returns a list of three OEE values """
		
	# Defining good, great, bad, respectively. List contents are mean, standard deviation percentages.
	good_great_bad = {
		'availability':([.85, .03], [.90, .01], [.80, .05]),
		'performance':([.92, .02], [.95, .01], [.90, .03]),
		'quality':([.98, .005], [.99, .0005], [.96, .01])
		}
	
	if rating == 'good':
		v = 0
		oee_values = [
			random.normalvariate(good_great_bad['availability'][v][0], good_great_bad['availability'][v][1]), 
			random.normalvariate(good_great_bad['performance'][v][0], good_great_bad['performance'][v][1]), 
			random.normalvariate(good_great_bad['quality'][v][0], good_great_bad['quality'][v][1])
			]
	elif rating == 'great':
		v = 1
		oee_values = [
			random.normalvariate(good_great_bad['availability'][v][0], good_great_bad['availability'][v][1]), 
			random.normalvariate(good_great_bad['performance'][v][0], good_great_bad['performance'][v][1]), 
			random.normalvariate(good_great_bad['quality'][v][0], good_great_bad['quality'][v][1])
			]
	elif rating == 'bad':
		v = 2
		oee_values = [
			random.normalvariate(good_great_bad['availability'][v][0], good_great_bad['availability'][v][1]), 
			random.normalvariate(good_great_bad['performance'][v][0], good_great_bad['performance'][v][1]), 
			random.normalvariate(good_great_bad['quality'][v][0], good_great_bad['quality'][v][1])
			]
	return oee_values

def generate_oee_trace_values(oee_values):
	""" use the oee values to calculate the five traceability values for the record. 
	scheduled time, available time, good parts, total parts, ideal cycle time"""
	available_time = scheduled_time * oee_values[0] 
	total_parts = available_time * oee_values[1] / ideal_cycle_time
	good_parts = total_parts * oee_values[2]
	return [scheduled_time, available_time, good_parts, total_parts, ideal_cycle_time]
	

def set_defects(defect, defect_count):
    """ Pick a defect from the list to assign for this record """

    for idx in defect:
    	if random.random >= .2:
    		datadms.setdefect(1, idx)
    		break
    	else: 
    		# defect defaults to first item
    		datadms.setdefect(1, defect[0])
    

############################################
main()