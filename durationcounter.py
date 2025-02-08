import os
from collections import defaultdict
from datetime import datetime


###############
# this script will generate 2 files, 
# multi_session and one_session which shows if prefix is seen in multiple or single session
##############

def parse_logs(data_folder="data"):
	# Dictionary to store prefix details
	prefix_data = defaultdict(lambda: {"first_seen": None, "last_seen": None, "origins": set(), "last_seen_changes": 0})
	
	# Iterate through all files in the data folder
	for filename in sorted(os.listdir(data_folder)):
		if filename.endswith(".txt"):
			filepath = os.path.join(data_folder, filename)
			with open(filepath, "r") as file:
				lines = file.readlines()
			
			# Extract relevant data starting from line 10
			for i in range(9, len(lines), 2):  # Step by 2 to process prefix-origin pairs
				if i + 1 < len(lines):  # Ensure there is a matching Origin ASNs line
					prefix_line = lines[i].strip()
					origin_line = lines[i + 1].strip()
					
					# Parse prefix and origins
					if prefix_line.startswith("Prefix:") and origin_line.startswith("Origin ASNs:"):
						prefix = prefix_line.split(":")[1].strip()
						origins = set(origin_line.split(":")[1].strip().split(", "))
						
						# Update dictionary
						if prefix not in prefix_data:
							prefix_data[prefix]["first_seen"] = filename
						# Check if last_seen is changing
						if prefix_data[prefix]["last_seen"] != filename:
							prefix_data[prefix]["last_seen_changes"] += 1
						prefix_data[prefix]["last_seen"] = filename
						prefix_data[prefix]["origins"].update(origins)
	
	return prefix_data

def filename_to_date(filename):
	"""Converts a filename to a datetime object."""
	try:
		# Extract the compact date and time string from the filename
		date_str = filename.split("_")[2]  # e.g., "20140101"
		time_str = filename.split("_")[3].replace(".txt", "")  # e.g., "0000"
		datetime_str = f"{date_str}{time_str}"  # Combine to "201401010000"
		return datetime.strptime(datetime_str, "%Y%m%d%H%M")  # Parse to datetime
	except Exception as e:
		print(f"Error parsing filename {filename}: {e}")
		return datetime.min  # Default fallback for invalid filenames

def write_logs(prefix_data, single_session_file="one_session.txt", multi_session_file="multi_session.txt"):
	with open(single_session_file, "w") as single_file, open(multi_session_file, "w") as multi_file:
		for prefix, data in prefix_data.items():
			first_seen = data["first_seen"]
			last_seen = data["last_seen"]
			last_seen_changes = data["last_seen_changes"]
			origins = ", ".join(sorted(data["origins"]))
			
			# Write to respective file based on session count
			if first_seen == last_seen:  # One-session events
				single_file.write(f"Prefix: {prefix}\n")
				single_file.write(f"  Seen in: {first_seen}\n")
				single_file.write(f"  Origin ASNs: {origins}\n\n")
			else:  # Multiple-session events
				multi_file.write(f"Prefix: {prefix}\n")
				multi_file.write(f"  First Seen: {first_seen}\n")
				multi_file.write(f"  Last Seen: {last_seen}\n")
				multi_file.write(f"  Last Seen Changes: {last_seen_changes}\n")
				multi_file.write(f"  Origin ASNs: {origins}\n\n")

if __name__ == "__main__":
	# Parse logs and separate data
	prefix_data = parse_logs("data")
	write_logs(prefix_data, "one_session.txt", "multi_session.txt")
	print("##########\n#Finished#\n##########")
