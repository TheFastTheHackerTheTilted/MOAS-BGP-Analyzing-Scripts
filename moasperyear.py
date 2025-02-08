import os
import re
from collections import defaultdict

#this file checks for all moas events not limited to events which was seen only once

# Path to the data folder
data_folder = "./data/"

# Dictionary to store prefix to ASN lists mapping
prefix_asn_mapping = defaultdict(list)

# Loop through all files in the data folder
for file_name in os.listdir(data_folder):
	# Process only files with '2014' in their name
	if "2014" in file_name:
		file_path = os.path.join(data_folder, file_name)
		
		with open(file_path, 'r') as file:
			# Read all lines of the file
			lines = file.readlines()
			
			# Start from the 10th line (index 9 if 0-based)
			for i in range(9, len(lines), 2):  # Increment by 2 to handle pairs
				# Line 10 (Prefix) and Line 11 (Origin ASNs)
				prefix_line = lines[i].strip()
				if i + 1 < len(lines):  # Ensure there is a next line
					asn_line = lines[i + 1].strip()
					
					# Extract Prefix from the line
					prefix_match = re.match(r"Prefix:\s+([\d\.\/]+)", prefix_line)
					if prefix_match:
						prefix = prefix_match.group(1)
						
						# Extract ASNs from the line
						asn_match = re.match(r"Origin ASNs:\s+([\d,\s]+)", asn_line)
						if asn_match:
							# Parse ASNs into a list of integers
							asns = list(map(str, asn_match.group(1).split(',')))
							
							# Add the ASN list for the prefix
							prefix_asn_mapping[prefix].append(asns)

# Group prefixes by the number of ASN lists, sorted in descending order
grouped_prefixes = defaultdict(list)
for prefix, asn_lists in prefix_asn_mapping.items():
	grouped_prefixes[len(asn_lists)].append((prefix, asn_lists))

# Write the results to a text file
output_file = "grouped_prefixes_desc.txt"
with open(output_file, "w") as file:
	for group_size in sorted(grouped_prefixes, reverse=True):  # Sort descending
		file.write(f"Prefixes with {group_size} ASN list(s):\n")
		for prefix, asn_lists in grouped_prefixes[group_size]:
			file.write(f"  Prefix: {prefix}\n")
			file.write(f"    ASN Lists: {asn_lists}\n")
		file.write("\n")

print(f"Results have been written to {output_file}")
