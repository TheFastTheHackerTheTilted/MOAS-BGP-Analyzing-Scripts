from collections import defaultdict
import ast

def analyze_asn_file(file_path):
	"""
	Analyze a file containing ASN data and count occurrences of various attributes.

	Args:
		file_path (str): Path to the file containing ASN data.

	Returns:
		None
	"""
	print("Analayzing ",file_path)
	print("#############################")
	rpki_status_counts = defaultdict(int)
	rir_counts = defaultdict(int)
	ipv4_visibility_counts = defaultdict(int)
	ipv6_visibility_counts = defaultdict(int)

	try:
		with open(file_path, "r") as file:
			for line in file:
				# Parse each line as a dictionary
				try:
					asn_data = ast.literal_eval(line.strip())  # Safely evaluate the line as a Python dict
				except Exception as e:
					print(f"Error parsing line: {line.strip()} - {e}")
					continue

				# Count RPKI status
				rpki_status = asn_data.get("rpki_status", "unknown")
				rpki_status_counts[rpki_status] += 1

				# Count RIR status
				rir = asn_data.get("rir", "unknown")
				rir_counts[rir] += 1

				# Count IPv4 and IPv6 visibility statuses
				visibility = asn_data.get("visibility", {})
				if isinstance(visibility, dict):  # If visibility is a dictionary
					ipv4_status = visibility.get("ipv4_status", "unknown")
					ipv6_status = visibility.get("ipv6_status", "unknown")
				elif isinstance(visibility, tuple):  # If visibility is a tuple
					ipv4_status = "unknown"
					ipv6_status = "unknown"
				else:
					ipv4_status = "unknown"
					ipv6_status = "unknown"

				ipv4_visibility_counts[ipv4_status] += 1
				ipv6_visibility_counts[ipv6_status] += 1

		# Print results
		print("RPKI Status Counts:")
		for status, count in rpki_status_counts.items():
			print(f"  {status}: {count}")

		print("\nRIR Counts:")
		for rir, count in rir_counts.items():
			print(f"  {rir}: {count}")

		print("\nIPv4 Visibility Counts:")
		for status, count in ipv4_visibility_counts.items():
			print(f"  {status}: {count}")

		print("\nIPv6 Visibility Counts:")
		for status, count in ipv6_visibility_counts.items():
			print(f"  {status}: {count}")

	except FileNotFoundError:
		print(f"File not found: {file_path}")
	except Exception as e:
		print(f"An error occurred: {e}")

# Example usage
if __name__ == "__main__":
	file_path = "./output/asn_analysis_results_2024.txt"  # Replace with the actual file path
	analyze_asn_file(file_path)
