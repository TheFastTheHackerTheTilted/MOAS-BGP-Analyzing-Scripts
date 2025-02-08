import os
import re
import matplotlib.pyplot as plt
import pandas as pd  # Optional, but helpful for managing data

########
# creates 2 seperate graphs
########

# Path to the directory containing the log files
log_dir = "data/"

def parse_logs(log_dir):
	"""
	Parses log files to extract total updates, MOAS count, and timestamps.
	"""
	data = []
	
	for filename in os.listdir(log_dir):
		if filename.endswith(".txt"):  # Ensure we process only text files
			filepath = os.path.join(log_dir, filename)
			
			with open(filepath, "r") as file:
				lines = file.readlines()
				
				# Extract details using known line structure
				timestamp_match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", lines[1])
				updates_match = re.search(r"Total Updates: (\d+)", lines[5])
				moas_match = re.search(r"MOAS Count: (\d+)", lines[6])
				
				if timestamp_match and updates_match and moas_match:
					timestamp = timestamp_match.group(1)
					total_updates = int(updates_match.group(1))
					moas_count = int(moas_match.group(1))
					
					data.append({
						"timestamp": timestamp,
						"total_updates": total_updates,
						"moas_count": moas_count,
						"moas_ratio": moas_count / total_updates if total_updates > 0 else 0
					})
	
	return pd.DataFrame(data)

def plot_data(df):
	"""
	Plots MOAS count and ratio over time using Matplotlib, removing gaps and point markers.
	"""
	# Convert timestamp to datetime for better visualization
	df["timestamp"] = pd.to_datetime(df["timestamp"])
	df.sort_values("timestamp", inplace=True)
	
	# Plotting MOAS Count
	plt.figure(figsize=(10, 6))
	plt.plot(df["timestamp"], df["moas_count"], label="MOAS Count", color="blue", linestyle="-")  # Removed marker
	plt.title("MOAS Events Over Time")
	plt.xlabel("Time")
	plt.ylabel("MOAS Count")
	plt.legend()
	plt.grid()
	plt.tight_layout()  # Ensure proper spacing
	plt.show()
	
	# Plotting MOAS Ratio
	plt.figure(figsize=(10, 6))
	plt.plot(df["timestamp"], df["moas_ratio"], label="MOAS Ratio", color="green", linestyle="-")  # Removed marker
	plt.title("MOAS Ratio Over Time")
	plt.xlabel("Time")
	plt.ylabel("MOAS Ratio")
	plt.legend()
	plt.grid()
	plt.tight_layout()  # Ensure proper spacing
	plt.show()


def main():
	# Step 1: Parse log files
	log_data = parse_logs(log_dir)
	#print(log_data)  # Preview parsed data
	
	# Step 2: Visualize the data
	plot_data(log_data)

if __name__ == "__main__":
	main()
