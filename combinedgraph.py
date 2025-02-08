import os
import matplotlib.pyplot as plt

def parse_log_file(filepath):
	"""Parses a log file to extract the total updates and MOAS count."""
	with open(filepath, "r") as file:
		lines = file.readlines()
		total_updates = 0
		moas_count = 0
		
		for line in lines:
			if line.startswith("Total Updates:"):
				total_updates = int(line.split(":")[1].strip())
			elif line.startswith("MOAS Count:"):
				moas_count = int(line.split(":")[1].strip())
		
		return total_updates, moas_count

def process_logs(data_folder="data"):
	"""Processes all log files in the data folder and returns parsed results."""
	data = []
	
	for filename in sorted(os.listdir(data_folder)):
		if filename.endswith(".txt"):
			filepath = os.path.join(data_folder, filename)
			total_updates, moas_count = parse_log_file(filepath)
			
			if total_updates > 0:  # Avoid division by zero
				moas_ratio = moas_count / total_updates
				data.append((filename, moas_ratio, moas_count))
	
	return data

def plot_combined_graph(data, output_file="combined_graph.png"):
	"""Plots a combined graph of MOAS ratio and MOAS count."""
	# Extract data
	x_labels = [entry[0] for entry in data]
	moas_ratios = [entry[1] for entry in data]
	moas_counts = [entry[2] for entry in data]
	
	# Create the figure and the two axes
	fig, ax1 = plt.subplots(figsize=(12, 6))
	
	# Plot MOAS ratio on the first y-axis
	ax1.set_xlabel("Log Files (Time)")
	ax1.set_ylabel("MOAS Ratio", color="blue")
	ax1.plot(moas_ratios, color="blue", marker="o", linestyle="None", alpha=0.3, label="MOAS Ratio")
	ax1.tick_params(axis="y", labelcolor="blue")
	ax1.set_xticks(range(0, len(x_labels), max(len(x_labels) // 10, 1)))  # Fewer ticks for readability
	
	# Create a second y-axis for MOAS count
	ax2 = ax1.twinx()
	ax2.set_ylabel("MOAS Count", color="green")
	ax1.plot(moas_counts, color="green", marker="o", linestyle="None", alpha=0.3, label="MOAS Count")
	ax2.tick_params(axis="y", labelcolor="green")
	
	# Title and layout adjustments
	fig.tight_layout()
	plt.title("MOAS Ratio and Count Over Time")
	
	# Save the figure
	plt.savefig(output_file)
	plt.close()

if __name__ == "__main__":
	# Process logs and generate the graph
	data = process_logs("data")
	plot_combined_graph(data, "combined_graph.png")
	print("##########\n# Graph Saved: combined_graph.png #\n##########")
