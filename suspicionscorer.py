import ast
from collections import defaultdict

# Define the suspicion scoring rules
SUSPICION_RULES = {
	"rpki_status": {
		"valid": 0,
		"mostly_valid": 1,
		"unknown": 3,
		"invalid": 5,
		"no_prefixes": 4,
	},
	"rir": {
		"ALLOCATED": 0,
		"ASSIGNED": 2,
		"RESERVED": 3,
		"UNALLOCATED": 5,
		"no_rir_data": 4,
	},
	"visibility": {
		"visible": 0,
		"invisible": 3,
		"unknown": 5,  # Assuming unknown is highly suspicious
	}
}

def calculate_suspicion_score(asn_data):
	"""Calculate the suspicion score for a given ASN entry."""
	score = 0

	# RPKI status
	score += SUSPICION_RULES["rpki_status"].get(asn_data.get("rpki_status"), 0)
	
	# RIR status
	score += SUSPICION_RULES["rir"].get(asn_data.get("rir"), 0)
	
	# Visibility (process IPv4 and IPv6 visibility separately if provided as dict)
	visibility = asn_data.get("visibility")
	if isinstance(visibility, dict):
		for key in ["ipv4_status", "ipv6_status"]:
			score += SUSPICION_RULES["visibility"].get(visibility.get(key, "unknown"), 0)
	elif isinstance(visibility, tuple) and visibility[0] == "unknown":
		score += SUSPICION_RULES["visibility"]["unknown"]
	
	return score

def analyze_asn_scores(file_path):
	print(file_path)
	"""Read ASN data from file, calculate scores, and tally the results."""
	score_counts = defaultdict(int)

	# Read the file and process each ASN
	with open(file_path, "r") as file:
		for line in file:
			try:
				asn_data = ast.literal_eval(line.strip())
				if isinstance(asn_data, dict):  # Ensure the parsed line is a dictionary
					score = calculate_suspicion_score(asn_data)
					score_counts[score] += 1
				else:
					print(f"Skipping invalid line (not a dictionary): {line.strip()}")
			except Exception as e:
				print(f"Skipping invalid line (error: {e}): {line.strip()}")

	# Print results
	print("Suspicion Score Distribution:")
	for score, count in sorted(score_counts.items()):
		print(f"Score {score}: {count} ASNs")

# Usage
file_path = "./output/asn_analysis_results_2024.txt"  # Replace with the path to your file
analyze_asn_scores(file_path)
