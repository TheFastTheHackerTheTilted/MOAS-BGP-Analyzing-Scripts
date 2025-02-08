import argparse
import pybgpstream

# Configurations for time intervals and collectors
timeDict = {
	"batch1": ["2017-07-07 00:00:00", "2017-07-07 00:00:01 UTC"],
	"batch2": ["2017-07-08 00:00:00", "2017-07-08 00:00:01 UTC"],
	"batch3": ["2017-07-08 00:00:00", "2017-07-08 00:00:10 UTC"],
	"batch4": ["2017-07-08 00:00:00", "2017-07-08 00:01:00 UTC"],
}

collectorList = ["route-views2", "route-views.sg", "route-views.linx"]

# Dictionaries to store prefix-to-path mapping and MOAS events
prefix_to_as_path = {}
moas_events = {}

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

def main():
	# Set up argument parsing
	parser = argparse.ArgumentParser(description="Process BGPStream data")
	parser.add_argument("batch", choices=timeDict.keys(), help="Choose the batch (e.g., batch1, batch2)")
	parser.add_argument("collector_index", type=int, choices=range(len(collectorList)), help="Choose the collector index (0, 1, ...)")
	args = parser.parse_args()

	# Retrieve batch and collector based on arguments
	from_time, until_time = timeDict[args.batch]
	collector = collectorList[args.collector_index]

	print(f"Using batch: {args.batch} ({from_time} to {until_time})")
	print(f"Using collector: {collector}")

	# Initialize the BGPStream object
	stream = get_stream(from_time, until_time, collector)

	# Process the stream
	for elem in stream:
		print(elem)


if __name__ == "__main__":
	main()
