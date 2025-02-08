import os
from collections import defaultdict
from datetime import datetime

def parse_logs(data_folder="data"):
	"""
	Parse the logs to extract prefix details and their associated metadata.
	"""
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

def filename_to_year(filename):
	"""
	Extract the year from the filename.
	"""
	try:
		date_str = filename.split("_")[2]  # e.g., "20140101"
		return datetime.strptime(date_str, "%Y%m%d").year  # Parse to extract the year
	except Exception as e:
		print(f"Error parsing year from filename {filename}: {e}")
		return None

def write_logs_by_year(prefix_data, output_folder="output"):
	"""
	Write one-time events grouped by year into separate files.
	"""
	# Ensure the output folder exists
	os.makedirs(output_folder, exist_ok=True)
	
	# Dictionary to group one-time events by year
	yearly_data = defaultdict(list)
	
	for prefix, data in prefix_data.items():
		first_seen = data["first_seen"]
		last_seen = data["last_seen"]
		origins = ", ".join(sorted(data["origins"]))
		
		# Only process one-session events
		if first_seen == last_seen:
			year = filename_to_year(first_seen)
			if year is not None:
				yearly_data[year].append({
					"prefix": prefix,
					"seen_in": first_seen,
					"origins": origins
				})
	
	# Write the data to separate files for each year
	for year, events in yearly_data.items():
		output_file = os.path.join(output_folder, f"one_session_{year}.txt")
		with open(output_file, "w") as file:
			for event in events:
				file.write(f"Prefix: {event['prefix']}\n")
				file.write(f"  Seen in: {event['seen_in']}\n")
				file.write(f"  Origin ASNs: {event['origins']}\n\n")
	
	print(f"Finished writing one-session events grouped by year to {output_folder}.")

if __name__ == "__main__":
	# Parse logs and process one-session events by year
	prefix_data = parse_logs("data")
	write_logs_by_year(prefix_data, "output")
	print("##########\n#Finished#\n##########")
