from datetime import datetime

def calculate_event_durations(input_file="multi_session.txt"):
	# Variables to store total durations and counts
	total_duration = 0
	total_count = 0

	short_duration = 0
	short_count = 0

	# Function to parse date from filenames
	def parse_date(filename):
		# Extract the date and time portion from the filename
		try:
			date_str = filename.split("_")[2] + filename.split("_")[3].replace(".txt", "")
			return datetime.strptime(date_str, "%Y%m%d%H%M")
		except Exception as e:
			print(f"Error parsing date from {filename}: {e}")
			return None

	# Open and process the file
	with open(input_file, "r") as file:
		lines = file.readlines()

		# Process every pair of "First Seen" and "Last Seen" lines
		for i in range(1, len(lines), 6):  # Line 2, 3, 8, 9... in text file (indices 1, 2, 7, 8 in Python)
			if i + 1 < len(lines):
				first_seen_line = lines[i].strip()
				last_seen_line = lines[i + 1].strip()

				# Extract filenames
				if first_seen_line.startswith("First Seen:") and last_seen_line.startswith("Last Seen:"):
					first_seen_file = first_seen_line.split(":")[1].strip()
					last_seen_file = last_seen_line.split(":")[1].strip()

					# Parse dates
					first_seen_date = parse_date(first_seen_file)
					last_seen_date = parse_date(last_seen_file)

					if first_seen_date and last_seen_date:
						# Calculate duration in days
						duration = (last_seen_date - first_seen_date).total_seconds() / (60 * 60 * 24)  # Convert seconds to days

						# Update total stats
						total_duration += duration
						total_count += 1

						# Update short-duration stats if duration < 30 days
						if duration < 30:
							short_duration += duration
							short_count += 1

	# Calculate averages
	overall_avg = total_duration / total_count if total_count > 0 else 0
	short_avg = short_duration / short_count if short_count > 0 else 0

	# Print results
	print("########## Results ##########")
	print(f"Total Events: {total_count}")
	print(f"Overall Average Duration: {overall_avg:.2f} days")
	print(f"Short-Lived Events (Duration < 30 days): {short_count}")
	print(f"Short-Lived Average Duration: {short_avg:.2f} days")
	print("#############################")

if __name__ == "__main__":
	calculate_event_durations("./output/multi_session.txt")
