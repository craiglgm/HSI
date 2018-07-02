###########################
# Configuration Variables #
###########################

# Set these variables to True or False based on whether or not you want
# to collect data for that specific part of OEE.
DO_AVAILABILITY = True
DO_PERFORMANCE = True
DO_QUALITY = True

# Set ideal cycle time here: minutes per 1 part
# Can do quality but not performance if you don't have ideal cycle time
IDEAL_CYCLE_TIME = 0.055

# Traceability indices
TRACE_LOT = 1
TRACE_SHIFT = 2
TRACE_WORK_CENTER = 3
TRACE_MACHINE = 4
TRACE_PLANT = 5
TRACE_OPERATOR = 6
TRACE_INSPECTION_PAGE = 7
TRACE_INSPECTION_TEST_NAME = 8
TRACE_AVAILABLE_TIME = 9
TRACE_SCHEDULED_TIME = 10
TRACE_GOOD_PARTS = 11
TRACE_TOTAL_PARTS = 12
TRACE_IDEAL_CYCLE_TIME = 13
TRACE_GUID = 14



# Globals shared from one inspection to the next should be invalidated when they
# are no longer needed to avoid residual data:
# available_time (sent from Availability to Performance)
# guid (sent from Availability to Performance - actually, to store_performance() function)
# total_parts (send from Performance to Quality)


#######################
# Top-Level Functions #
#######################
import System


def main():
	"""Entry point for the program."""
	subinspect_name = inspect.cursubi.name
	if subinspect_name == 'Traceability':
		traceability_scripts()
	elif subinspect_name == 'Availability':
		availability_scripts()
	elif subinspect_name == 'Performance':
		performance_scripts()
	elif subinspect_name == 'Quality':
		quality_scripts()



###############################
# Traceability Sub-Inspection #
###############################

def traceability_scripts():
	"""Scripts for the Traceability subinspection."""
	if testid == '[PRE]':
		traceability_pre()
	elif testid == 'click':
		traceability_click()
	elif testid == '[POST]':
		traceability_post()



def traceability_pre():
	# pre script runs when the sub-inspection loads
	# hard code the plant based on Inspection name
	if inspect.name == 'OEE - Manual Data Entry Springfield Plant':
		inspect.settracevalue(TRACE_PLANT, 'Springfield')
	else:
		inspect.settracevalue(TRACE_PLANT, 'Main')

	# disable the date/time test
	inspect.cursubi.datetime('timestamp').enabled = False

	# Create drop down for traceability options
	inspect.cursubi.trace('shift').list = ['1', '2']
	inspect.cursubi.trace('workcenter').list = ['A', 'B']
	
	# set the ideal cycle time across the Inspection for this scenario
	inspect.settracevalue(TRACE_IDEAL_CYCLE_TIME, str(IDEAL_CYCLE_TIME))


def traceability_click():
	# click script for enabling the d/t
	# Enable the date/time test so that it can be manually set
	inspect.cursubi.datetime('timestamp').enabled = True  # TODO datetime isn't used?


def traceability_post():
	# post script runs when submit is clicked.
	if inspect.cursubi.trace('workcenter').value == 'A':
		inspect.settracevalue(TRACE_MACHINE, '250')
		inspect.dmspartnumber = "20 OZ"
	else:
		inspect.settracevalue(TRACE_MACHINE, '350')
		inspect.dmspartnumber = "2 L"

	# Determine what the next sub-inspection should be based on
	# which Boolean flags are set in the configuration above.
	if DO_AVAILABILITY:
		inspect.setnextsubi('Availability')
	elif DO_PERFORMANCE:
		inspect.setnextsubi('Performance')
	elif DO_QUALITY:
		inspect.setnextsubi('Quality')
	else:
		inspect.setnextsubi(None)


###############################
# Availability Sub-Inspection #
###############################

def availability_scripts():
	"""Scripts for the Availability subinspection."""
	if testid == "scheduled_time":
		availability_scheduled_time()
	elif testid == "downtime_reason":
		availability_downtime_reason()
	elif testid == '[POST]':
		availability_post()


def availability_scheduled_time():
	# "on change" from scheduled time field. 
	# set sample size to scheduled time
	try:
		inspect.cursubi.defectlist("downtime_reason").samplesize = int(
			inspect.cursubi.trace("scheduled_time").value)
	except ValueError:  # they didn't enter an int
		pass


def availability_downtime_reason():
	global available_time

	# "on change" from downtime reason field
	# calculate available time and estimate parts produced
	try:
		# Global set here
		available_time = (
			int(inspect.cursubi.trace("scheduled_time").value) -
			int(inspect.cursubi.defectlist("downtime_reason").ncu)
		)
		inspect.cursubi.trace("available_time").value = str(available_time)
	except ValueError:
		pass


def availability_post():
	global guid

	# Just before this record is stored, tag it with a GUID so it can be
	# updated in the Performance section.
	guid = str(System.Guid.NewGuid())[:30];  # Default max trace length is 30
	inspect.settracevalue(TRACE_GUID, guid)

	if DO_PERFORMANCE:
		inspect.setnextsubi('Performance')
	elif DO_QUALITY:
		inspect.setnextsubi('Quality')
	else:
		inspect.setnextsubi(None)



##############################
# Performance Sub-Inspection #
##############################

def performance_scripts():
	"""Scripts for the Performance subinspection."""
	if testid == '[PRE]':
		performance_pre()
	if testid == '[POST]':
		performance_post()


def performance_pre():
	global available_time

	try:
		local_available_time = int(available_time)

		# Don't delete available_time yet - need it when storing
		# performance record in raw fashion.
	except Exception:
		# Either the global available_time was not set or it was set to None
		available_entry = disp.newnumeric(minvalue=0, maxvalue=100000000000)
		available_entry.text = 'Enter the total time (in minutes) during which parts were produced:'
		available_entry.row = 0
		available_entry.column = 0
		disp.addcntrl(available_entry)
		disp.addbtn(0, "OK")
		disp.popup(True, 'Available Time', 50, 50, 300, 200)

		# TODO Wrap with validation
		available_time = int(available_entry.value)
		local_available_time = available_time

	# Truncate the ideal total parts to an int
	inspect.cursubi.trace("total_parts").value = str(
			int(local_available_time * 1.0 / IDEAL_CYCLE_TIME))


	

def performance_post():
	global total_parts

	# post script runs when submit is clicked
	# Grab the entered value of total parts produced
	try:
		total_parts = int(inspect.cursubi.trace('total_parts').value)
		store_performance()
	except ValueError:
		pass  # value entered for total parts wasn't an integer


	if DO_QUALITY:
		inspect.setnextsubi('Quality')
	else:
		inspect.setnextsubi(None)


def store_performance():
	global guid, available_time  # Need available_time if storing raw record

	# If we have a valid total_parts and guid, update AVAILABILITY record
	try:
		availability_guid = guid
		actual_total_parts = inspect.cursubi.trace("total_parts").value
		update_record_by_guid(availability_guid, TRACE_TOTAL_PARTS, actual_total_parts)
	except Exception:
		# need to store performance if there was no availability step
		# force-create record using datadms (which is separate from inspect)
		for trace_idx in [TRACE_SHIFT, TRACE_WORK_CENTER, TRACE_MACHINE,
		                  TRACE_PLANT, TRACE_OPERATOR]:
			datadms.settrace(trace_idx, inspect.gettracevalue(trace_idx))

		datadms.settrace(TRACE_INSPECTION_PAGE, inspect.cursubi.name)
		datadms.settrace(TRACE_AVAILABLE_TIME, str(available_time))
		datadms.settrace(TRACE_TOTAL_PARTS, inspect.cursubi.trace('total_parts').value)
		datadms.settrace(TRACE_IDEAL_CYCLE_TIME, str(IDEAL_CYCLE_TIME))

		datadms.process = inspect.process
		datadms.partno = inspect.dmspartnumber
		datadms.samplesize = 1
		datadms.store()


def update_record_by_guid(record_guid, trace_index, trace_value):
	"""Find the record stored with a given GUID and update one of its traceability values."""
	query = "UPDATE {} SET UDL{}= '{}' WHERE UDL{} = '{}';".format(
		sql.tables.ddataaux,
		trace_index,
		trace_value,
		TRACE_GUID,
		record_guid
	)
	sql.execute(query)



##########################
# Quality Sub-Inspection #
##########################

def quality_scripts():
	"""Scripts for the Quality subinspection."""
	if testid == "[PRE]":
		quality_pre()
	# Explain we are asking for which defects because we want to Pareto them
	elif testid == "part_defects":
		quality_part_defects()



def quality_pre():
	global total_parts

	# pre script runs when the sub-inspection loads

	# Disable the good parts field (it is automatically set by a formula)
	# good_parts should just be a "Text Entry" traceability test rather than being a real
	# traceability test - this stops it from being stored automatically.
	inspect.cursubi.trace('good_parts').enabled = False

	# Try to set total parts by checking to see if a global for it was already saved
	try:
		inspect.cursubi.defectlist('part_defects').samplesize = total_parts
		del total_parts
	except Exception:
		pass  # Don't pre-fill anything



def quality_part_defects():
	# "on change" from the part defects field
	# set the good parts field to total parts - defects.
	try:
		actual_total_parts = inspect.cursubi.defectlist('part_defects').samplesize
		defect_count = int(inspect.cursubi.defectlist('part_defects').ncu)

		good_part_count = actual_total_parts - defect_count
		inspect.cursubi.trace('good_parts').value = str(good_part_count)

		# Store good parts in the availability record (the one which has the GUID)
		# If there is no availability record, this attempt will fail and nothing will happen.
		availability_guid = guid
		update_record_by_guid(availability_guid, TRACE_GOOD_PARTS, good_part_count)

		del guid  # I don't want to store the GUID again

	except Exception:
		pass


main()