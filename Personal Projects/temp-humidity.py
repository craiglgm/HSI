""" 
A simple program for my Relay Pi
Controls four outlets, and reads temperature and humidity in Shedquarters.
Runs every 15 minutes to update the chart
"""

# Configuration Settings
html_file_path = 'c:\\users\\Craig\\Downloads\\'
html_file_name = 'shedquarters.html'

def main():
	print( html_file_path + html_file_name )

main()