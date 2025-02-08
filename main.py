import argparse
import pybgpstream
from datetime import datetime, timedelta
import os

# Configurations for automation
years = [2017,2018,2020,2021,2022,2023]
session_times = ["00:00:00", "12:00:00"]  # Times per day
session_duration = timedelta(hours=2)  # Each session lasts 2 hours
collectors = ["route-views2", "route-views.sg", "route-views.linx"]

def get_stream(from_time, until_time, collector, bgp_filter="type updates"):
	"""
	Initializes and returns a pybgpstream object with given parameters.
	"""
	return pybgpstream.BGPStream(
		from_time=from_time,
		until_time=until_time,
		collectors=[collector],
		record_type="updates",
		filter=bgp_filter
	)

def generate_intervals():
	"""
	Generate start and end times for the automated sessions based on the rules.
	"""
	intervals = []
	for year in years:
		for month in range(1, 13):  # Iterate through months
			first_day_of_month = datetime(year, month, 1)
			first_week = [
				first_day_of_month + timedelta(days=i)
				for i in range(7) if (first_day_of_month + timedelta(days=i)).month == month
			]
			for day in first_week:
				for session_time in session_times:
					start_time = datetime.combine(day, datetime.strptime(session_time, "%H:%M:%S").time())
					end_time = start_time + session_duration
					intervals.append((start_time, end_time))
	return intervals

def setup():
	os.makedirs("data", exist_ok=True)

def main():
	setup()
	parser = argparse.ArgumentParser(description="Automate BGPStream sessions")
	parser.add_argument("collector_index", type=int, choices=range(len(collectors)), help="Choose the collector index (0, 1, ...)")
	args = parser.parse_args()

	collector = collectors[args.collector_index]
	print(f"Using collector: {collector}")

	# Generate intervals (for testing, limit to the first 3 intervals with [:3] )
	intervals = generate_intervals()
	#print(intervals)

	for start_time, end_time in intervals:
		start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
		end_time_str = end_time.strftime("%Y-%m-%d %H:%M:%S")
		print(f"\nProcessing interval: {start_time_str} to {end_time_str}")

		# Initialize the BGPStream object
		stream = get_stream(start_time_str, end_time_str, collector)

		prefix_to_origins = {}  # Tracks unique origins (last AS) for each prefix
		moas_events = {}        # Stores detected MOAS events
		total_updates = 0
		moas_count = 0

		for elem in stream:
			if elem.type == "A":  # Only process announcements
				total_updates += 1
				prefix = elem.fields.get("prefix", None)
				as_path = elem.fields.get("as-path", None)

				if prefix and as_path:
					origin_asn = as_path.split()[-1]

					if prefix not in prefix_to_origins:
						prefix_to_origins[prefix] = set()

					if origin_asn not in prefix_to_origins[prefix]:
						if len(prefix_to_origins[prefix]) > 0:
							######################3
							# UNCOMMENT THIS TO ANALYZE EACH EVENT INDV.
							# print(f"MOAS Event Detected: Prefix {prefix}")
							# print(f"Existing Origins: {prefix_to_origins[prefix]}")
							# print(f"New Origin ASN: {origin_asn}")
							moas_count += 1

							if prefix not in moas_events:
								moas_events[prefix] = list(prefix_to_origins[prefix])
							moas_events[prefix].append(origin_asn)

					prefix_to_origins[prefix].add(origin_asn)

		# Write the summary to a file
		sanitized_time = start_time.strftime("%Y%m%d_%H%M")
		filename = f"data/summary_{collector}_{sanitized_time}.txt"
		with open(filename, "w") as file:
			file.write(f"\nBGPStream Summary for {collector} ({start_time_str} to {end_time_str})\n\n")
			file.write("MOAS Events Summary:\n")
			file.write(f"\nTotal Updates: {total_updates}\n")
			file.write(f"MOAS Count: {moas_count}\n")
			file.write(f"MOAS Ratio: {moas_count}/{total_updates}\n\n")
			for prefix, origins in moas_events.items():
				file.write(f"Prefix: {prefix}\n")
				file.write(f"  Origin ASNs: {', '.join(origins)}\n")

		print(f"Summary written to {filename}")

if __name__ == "__main__":
	main()
