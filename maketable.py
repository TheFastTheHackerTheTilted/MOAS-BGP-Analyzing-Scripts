import os
from collections import defaultdict

def analyze_data(data_folder="data", one_session_file="one_session.txt", output_file="moas_table.txt"):
	# Initialize dictionary to hold yearly data
	yearly_data = {year: {"announcement_count": 0, "moas_count": 0, "short_count": 0} for year in range(2014, 2025)}

	# Step 1: Process files in the data folder
	for filename in sorted(os.listdir(data_folder)):
		if filename.endswith(".txt"):
			filepath = os.path.join(data_folder, filename)

			with open(filepath, "r") as file:
				lines = file.readlines()

				# Extract year from the second line (line 1 in Python)
				year_line = lines[1].split("(")[1].split("-")[0].strip()
				year = int(year_line)

				# Extract announcement count and MOAS count from lines 6 and 7 (lines 5 and 6 in Python)
				announcement_count = int(lines[5].split(":")[1].strip())
				moas_count = int(lines[6].split(":")[1].strip())

				# Update the dictionary
				yearly_data[year]["announcement_count"] += announcement_count
				yearly_data[year]["moas_count"] += moas_count

	# Step 2: Process the one-session file for short-lived MOAS counts
	with open(one_session_file, "r") as file:
		lines = file.readlines()

		# Extract years from lines like "Seen in: summary_route-views2_20140304_0000.txt"
		for i in range(1, len(lines), 4):  # Start from line 2 in text (index 1 in Python), step by 4
			line = lines[i]
			if "Seen in:" in line:
				year = int(line.split("_")[2][:4])  # Extract year from the filename
				yearly_data[year]["short_count"] += 1

	# Step 3: Write results to output file
	with open(output_file, "w") as file:
		file.write(f"{'Year':<10}{'Announcements':<15}{'MOAS Count':<15}{'MOAS Ratio':<15}{'Short-Lived MOAS':<10}\n")
		file.write("=" * 70 + "\n")
		for year in range(2014, 2025):
			announcements = yearly_data[year]["announcement_count"]
			moas = yearly_data[year]["moas_count"]
			ratio = "{:.6f}".format(moas/announcements)
			short = yearly_data[year]["short_count"]
			file.write(f"{year:<10}{announcements:<15}{moas:<15}{ratio:<15}{short:<10}\n")

	print(f"Analysis complete. Results written to {output_file}")

if __name__ == "__main__":
	analyze_data("data", "one_session.txt", "moas_table.txt")
