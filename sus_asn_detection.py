import os
import requests
from collections import defaultdict
import time
from statistics import median

# Configuration
URL_PREFIX_FROM_AS 	= "https://stat.ripe.net/data/announced-prefixes/data.json?resource=AS{asn}"
URL_RPKI 			= "https://stat.ripe.net/data/rpki-validation/data.json?resource=AS{asn}&prefixes={prefix}"
URL_WHOIS 			= 'https://stat.ripe.net/data/whois/data.json?data_overload_limit=ignore&resource={asn}'
URL_RIR 			= 'https://stat.ripe.net/data/rir/data.json?data_overload_limit=ignore&resource={asn}&lod=2'
URL_VISIBILITY 		= 'https://stat.ripe.net/data/visibility/data.json?data_overload_limit=ignore&include=peers_seeing&resource={asn}'
URL_AS_PATH_LENGTH 	= 'https://stat.ripe.net/data/as-path-length/data.json?resource={asn}'

def fetch_prefixes_from_asn(asn):
	url = URL_PREFIX_FROM_AS.format(asn=asn)
	try:
		response = requests.get(url)
		response.raise_for_status()
		return [item.get("prefix") for item in response.json().get("data", {}).get("prefixes", [])]
	except Exception as e:
		print(f"Error fetching prefixes for ASN {asn}:")
		return []


def fetch_rpki_status(asn, prefixes):
	"""
	Fetch RPKI status for a given ASN and prefixes.
	Args:
		asn (str): ASN to fetch RPKI status for.
		prefixes (list): List of prefixes.
	
	Returns:
		dict: RPKI data containing statuses and related details.
	"""
	prefix_param = ",".join(prefixes)
	url = URL_RPKI.format(asn=asn, prefix=prefix_param)
	try:
		response = requests.get(url)
		response.raise_for_status()
		rpki_data = response.json().get("data", {})
		
		# Ensure we handle cases with single item or list
		if isinstance(rpki_data, dict):  # If it's a single dictionary, wrap it in a list
			rpki_data = [rpki_data]
		
		return rpki_data
	except Exception as e:
		print(f"Error fetching RPKI status for ASN {asn}:")
		return []


def analyze_rpki_status(validating_roas, prefix):
	for roa in validating_roas:
		if roa.get("prefix") == prefix:
			return roa.get("status", "unknown")
	return "unknown"

def analyze_rpki_data(validating_roas):
	"""
	Analyze RPKI data for prefixes and categorize overall RPKI status.
	
	Args:
		validating_roas (list): A list of ROAs, each containing a `status` attribute.
	
	Returns:
		str: The categorized RPKI status: completely_valid, mostly_valid, less_valid, invalid, no_prefixes, or unknown.
	"""
	# Count statuses
	status_counts = {"valid": 0, "invalid": 0, "unknown": 0}
	for roa in validating_roas:
		status = roa.get("status", "unknown").lower()
		if status in status_counts:
			status_counts[status] += 1
		else:
			status_counts["invalid"] += 1
	
	total_prefixes = len(validating_roas)
	valid_count = status_counts["valid"]
	invalid_count = status_counts["invalid"]
	unknown_count = status_counts["unknown"]
	
	# Determine RPKI status
	if total_prefixes == 0:
		return "no_prefixes"
	elif invalid_count == total_prefixes:
		return "invalid"
	elif valid_count == total_prefixes:
		return "completely_valid"
	elif valid_count > (total_prefixes / 2):
		return "mostly_valid"
	elif valid_count > 0:
		return "less_valid"
	else:
		return "unknown"

def fetch_visibility(asn):
	"""
	Fetch visibility information for an ASN.
	"""
	url = URL_VISIBILITY.format(asn=asn)
	try:
		response = requests.get(url)
		response.raise_for_status()
		return response.json().get('data', {}).get('visibilities', [])
	except Exception as e:
		print(f"Error fetching visibility data for ASN {asn}:")
		return []
def analyze_visibility(visibility_data):
	"""
	Analyze visibility based on the first visibility data entry.
	"""
	if not visibility_data:
		return "unknown", 0, 0  # No visibility data

	visibility_entry = visibility_data[0]  # Use the first visibility entry
	ipv4_not_seeing = len(visibility_entry.get('ipv4_full_table_peers_not_seeing', []))
	ipv6_not_seeing = len(visibility_entry.get('ipv6_full_table_peers_not_seeing', []))
	ipv4_seeing = len(visibility_entry.get('ipv4_full_table_peers_seeing', []))
	ipv6_seeing = len(visibility_entry.get('ipv6_full_table_peers_seeing', []))

	# Determine visibility status
	def calculate_visibility(seeing, not_seeing):
		if seeing == 0:
			return "invisible"
		elif not_seeing == 0:
			return "visible"
		elif seeing / (seeing + not_seeing) > 0.5:
			return "mostly_visible"
		else:
			return "low_visible"

	ipv4_status = calculate_visibility(ipv4_seeing, ipv4_not_seeing)
	ipv6_status = calculate_visibility(ipv6_seeing, ipv6_not_seeing)

	return {
		"ipv4_status": ipv4_status,
		"ipv6_status": ipv6_status,
	}


def fetch_rir_data(asn):
	"""
	Fetch RIR registration data for an ASN.
	Extracts and simplifies the registration status.
	"""
	url = URL_RIR.format(asn=asn)  # Use the RIR API URL with the ASN
	try:
		# Make the API request
		response = requests.get(url)
		response.raise_for_status()
		rir_data = response.json().get('data', {}).get('rirs', [])
		
		# Process the RIR data
		if not rir_data:
			return "no_rir_data"  # No RIR data available

		# Extract RIR statuses
		status_counts = defaultdict(int)
		for rir_entry in rir_data:
			status = rir_entry.get('status', 'unknown')  # Default to 'unknown' if status is missing
			status_counts[status] += 1

		# Simplify the output
		if len(status_counts) == 1:
			# If there is only one status, return it directly
			return next(iter(status_counts))
		else:
			# If multiple statuses exist, summarize them
			return "multiple_statuses"
	except Exception as e:
		print(f"Error fetching RIR data for ASN {asn}:")
		return "error"

def fetch_as_path_length(asn):
	"""
	Fetch AS path length data for an ASN.
	"""
	url = URL_AS_PATH_LENGTH.format(asn=asn)
	try:
		response = requests.get(url)
		response.raise_for_status()
		return response.json().get('data', {}).get('stats', [])
	except Exception as e:
		print(f"Error fetching AS path length for ASN {asn}:")
		return []



def calculate_median_as_path_length(stats):
	"""
	Calculate the median AS path length based on the stripped average path lengths.

	Args:
		stats (list): A list of stats containing stripped path data.

	Returns:
		float: The median AS path length, or None if no valid data is available.
	"""
	# Extract the stripped "avg" values
	path_lengths = [
		stat["stripped"]["avg"] for stat in stats if "stripped" in stat and "avg" in stat["stripped"]
	]
	
	# Ensure there are values to calculate the median
	if not path_lengths:
		return None  # No data available
	
	# Calculate the median
	return round(median(path_lengths),3)




def analyze_asn(asn):
	"""
	Analyze a single ASN by fetching various data and determining its properties.
	"""
	analysis = {
		"asn": asn,
		"rpki_status": "unknown",  # Validity status: completely_valid, mostly_valid, less_valid, invalid
		# "whois": {},  # Placeholder for WHOIS data
		"rir": {},  # Placeholder for RIR registration data
		"visibility": {},  # Placeholder for visibility data
		"path_length": None  # Placeholder for AS path length
	}

	as_path_stats = fetch_as_path_length(asn)
	analysis["as_path"] = calculate_median_as_path_length(as_path_stats)
	
	# Fetch prefixes for the ASN
	prefixes = fetch_prefixes_from_asn(asn)
	if prefixes:
		# Fetch RPKI validation data for all prefixes
		rpki_data = fetch_rpki_status(asn, prefixes)
		analysis["rpki_status"] = analyze_rpki_data(rpki_data)
	else:
		analysis["rpki_status"] = "no_prefixes"

	# Analyze visibility (using existing function)
	visibility_data = fetch_visibility(asn)
	analysis["visibility"] = analyze_visibility(visibility_data)

	rir_data = fetch_rir_data(asn)
	analysis["rir"] = rir_data

	return analysis





def fetch_asn_data(asn, retries=5, delay=3):
	"""
	Fetch ASN data from the RIPEstat API with retries and delay between attempts.
	"""
	for attempt in range(retries):
		try:
			# Make the request to the RIPEstat API
			response = requests.get(RIPESTAT_API_URL, params={"resource": f"AS{asn}"})
			response.raise_for_status()  # Raise an error for bad responses
			return response.json()  # Return the JSON data if the request is successful
		except (requests.exceptions.ConnectionError, requests.exceptions.RequestException) as e:
			print(f"Attempt {attempt + 1}/{retries} failed for ASN {asn}:")
			if attempt < retries - 1:
				time.sleep(delay)  # Wait before retrying
			else:
				raise e  # If retries are exhausted, raise the exception

def check_asn_properties(asn):
	"""
	Check ASN properties using RIPEstat API or other methods and assign suspicion scores.
	"""
	try:
		data = fetch_asn_data(asn)
		if not data or "data" not in data:
			return {"asn": asn, "valid": False, "status": "Unknown", "score": 3}  # Assign default suspicious score

		overview = data["data"]
		status = overview.get("status", "Unknown")
		rpki_status = overview.get("rpki_status", "unknown")

		# Assign suspicion score based on RPKI status and ASN status
		score = 0
		if rpki_status == "invalid":
			score += 3  # High suspicion for invalid RPKI
		if status == "inactive":
			score += 2  # Moderate suspicion for inactivity

		return {"asn": asn, "valid": True, "status": status, "rpki_status": rpki_status, "score": score}
	except Exception as e:
		print(f"Error fetching data for ASN {asn}:")
		# Return a placeholder result if ASN data is unavailable
		return {"asn": asn, "status": "unavailable", "country": "unknown", "type": "unknown"}

def parse_one_session(file_path):
	"""
	Parse the `one_session.txt` file to extract prefix, seen data, and origin ASNs.
	"""
	moas_data = []  # List to hold parsed MOAS event data
	with open(file_path, 'r') as file:
		lines = file.readlines()
		total_lines = len(lines)

		for i in range(0, total_lines, 4):  # Process each MOAS event (4-line groups)
			if i % 1000 == 0:  # Print progress every 1000 lines
				print(f"Parsing progress: {i}/{total_lines} lines processed...")

			prefix = lines[i].strip().split(": ")[1]
			seen_in = lines[i + 1].strip().split(": ")[1]
			origin_asns = list(map(int, lines[i + 2].strip().split(": ")[1].split(",")))  # Split by comma only
			moas_data.append({"prefix": prefix, "seen_in": seen_in, "origin_asns": origin_asns})

	print("Parsing complete.")
	return moas_data

def analyze_moas_events(moas_data):
	"""
	Analyze MOAS events and assign suspicion scores to each ASN.
	"""
	asn_scores = defaultdict(list)  # {ASN: [scores]}
	prefix_results = []  # Detailed results for each prefix
	total_events = len(moas_data)
	
	for index, event in enumerate(moas_data):
		if index % 100 == 0:  # Print progress every 100 events
			print(f"Analyzing progress: {index}/{total_events} events processed...")
		
		prefix = event["prefix"]
		origin_asns = event["origin_asns"]
		prefix_suspicion = 0  # Total suspicion score for this prefix
		
		# Analyze each ASN
		asn_analysis = []
		for asn in origin_asns:
			asn_details = check_asn_properties(asn)
			asn_scores[asn].append(asn_details["score"])
			asn_analysis.append(asn_details)
			prefix_suspicion += asn_details["score"]
		
		# Store results
		prefix_results.append({
			"prefix": prefix,
			"total_suspicion": prefix_suspicion,
			"asn_analysis": asn_analysis,
		})
	
	print("Analysis complete.")
	return asn_scores, prefix_results


def categorize_asn_scores(asn_scores):
	"""
	Categorize ASNs based on their suspicion scores and available information.
	"""
	categories = {
		"Likely Legitimate": [],
		"Potentially Suspicious": [],
		"Likely Malicious": [],
		"Lacking Information": []
	}
	
	for asn, scores in asn_scores.items():
		# Check if the ASN lacks information
		if all(score == 3 for score in scores):  # Assuming score of 3 means 'unknown'
			categories["Lacking Information"].append(asn)
		else:
			# Calculate the average score for categorization
			avg_score = sum(scores) / len(scores)
			if avg_score < 2:
				categories["Likely Legitimate"].append(asn)
			elif 2 <= avg_score < 4:
				categories["Potentially Suspicious"].append(asn)
			else:
				categories["Likely Malicious"].append(asn)
	
	return categories


def write_results_to_file(prefix_results, categories, output_path):
	"""
	Write the analysis results to a text file.
	"""
	with open(output_path, 'w') as file:
		file.write("MOAS Event Analysis\n")
		file.write("=" * 50 + "\n\n")

		# Write Prefix Analysis
		file.write("Prefix-Level Analysis:\n")
		for result in prefix_results:
			file.write(f"Prefix: {result['prefix']}\n")
			file.write(f"  Total Suspicion Score: {result['total_suspicion']}\n")
			file.write("  ASN Analysis:\n")
			for asn_data in result["asn_analysis"]:
				file.write(f"    ASN {asn_data['asn']}: Score {asn_data['score']}, Status: {asn_data['status']}, RPKI: {asn_data['rpki_status']}\n")
			file.write("\n")

		# Write ASN Categories
		file.write("\nASN Categorization:\n")
		for category, asns in categories.items():
			file.write(f"{category} ({len(asns)} ASNs):\n")
			file.write(", ".join(map(str, asns)) + "\n\n")


def main():
	one_session_file = "./output/one_session_2024.txt"
	output_file = "./output/asn_analysis_results_2024.txt"

	event_list = parse_one_session(one_session_file)
	asns_to_analyze = {asn for event in event_list for asn in event["origin_asns"]}
	processed_asns = set()  # Track ASNs already processed

	start_time = time.time()
	with open(output_file, "a") as file:  # Use 'a' mode to append to the file
		for asn in asns_to_analyze:
			if asn in processed_asns:
				print(f"Skipping already analyzed ASN {asn}")
				continue
			
			print(f"Analyzing ASN {asn}...")
			result = analyze_asn(asn)
			file.write(f"{result}\n")  # Write the result immediately after analysis
			processed_asns.add(asn)  # Mark ASN as processed
			
	total_time = time.time() - start_time
	print(f"Processed {len(asns_to_analyze)} ASNs in {total_time:.2f} seconds.")
	print(f"Results written to {output_file}.")

if __name__ == "__main__":
	main()
