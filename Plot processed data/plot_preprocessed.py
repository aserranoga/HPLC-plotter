import pandas as pd
import matplotlib.pyplot as plt
import os
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
import configparser

def confirm_overwrite(file_path):
    """Ask the user for confirmation to overwrite an existing file."""
    while True:
        choice = input(f"The file '{os.path.basename(file_path)}' already exists. Do you want to overwrite it? (y/n): ").lower()
        if choice in ['y', 'n']:
            return choice == 'y'
        print("Please respond with 'y' or 'n'.")

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')

# General configuration
processed_csv_file = config.get('General', 'processed_csv_file')  # Path to the processed CSV
pdf_destination_folder = config.get('General', 'pdf_destination_folder')
filename = config.get('General', 'filename')
x_limits = tuple(map(float, config.get('General', 'x_limits').split(',')))
major_tick_interval = config.getfloat('General', 'major_tick_interval')
num_minor_ticks = config.getint('General', 'num_minor_ticks')

# Style configuration
figure_size = tuple(map(lambda x: float(x) / 2.54, config.get('Style', 'figure_size').split(',')))
font = config.get('Style', 'font')
axis_width = config.getfloat('Style', 'axis_width')
font_size = config.getfloat('Style', 'font_size')
font_weight = config.get('Style', 'font_weight')
line_width = config.getfloat('Style', 'line_width')
major_tick_length = config.getfloat('Style', 'major_tick_length')
major_tick_width = config.getfloat('Style', 'major_tick_width')
minor_tick_length = config.getfloat('Style', 'minor_tick_length')
minor_tick_width = config.getfloat('Style', 'minor_tick_width')
tick_font = config.get('Style', 'tick_font')
tick_font_size = config.getfloat('Style', 'tick_font_size')
tick_font_weight = config.get('Style', 'tick_font_weight')

# Padding adjustments
adjust_left = config.getfloat('Style', 'adjust_left')
adjust_right = config.getfloat('Style', 'adjust_right')
adjust_top = config.getfloat('Style', 'adjust_top')
adjust_bottom = config.getfloat('Style', 'adjust_bottom')

# Ensure the PDF destination folder exists
os.makedirs(pdf_destination_folder, exist_ok=True)

# Combine destination folder and filename for the PDF output
output_pdf = os.path.join(pdf_destination_folder, f"{filename}.pdf")

# Check if the PDF file already exists and confirm overwrite
if os.path.exists(output_pdf):
    if not confirm_overwrite(output_pdf):
        print("Operation canceled.")
        exit()

# Read the processed CSV file
df = pd.read_csv(processed_csv_file)

# Extract time column and dynamically get the "Normalized Intensity (Offset)" columns
time_col = 'Time (min)'
offset_columns = [col for col in df.columns if 'Normalized Intensity (Offset)' in col]

# Plotting
plt.figure(figsize=figure_size)
plt.rc('font', family=font, size=font_size, weight=font_weight)

# Plot each offset column directly without additional offset
for col in offset_columns:
    plt.plot(df[time_col], df[col], color='black', label=col.split('(')[-1][:-1], linewidth=line_width)

plt.xlabel('Time (min)')
plt.xlim(x_limits)  
plt.ylabel('Normalized Intensity (Offset)')

# Filter the data to the x-axis range specified in x_limits
filtered_df = df[(df[time_col] >= x_limits[0]) & (df[time_col] <= x_limits[1])]
# Find the maximum intensity within the x-axis range across all offset columns
y_max_within_x_limits = filtered_df[offset_columns].max().max()
# Set y-axis limits with an absolute lower limit of -10 and dynamic upper limit based on filtered data
plt.ylim(-10, y_max_within_x_limits + 10)  # Fixed lower limit of -10, dynamic upper limit within x-axis range


plt.gca().xaxis.set_major_locator(MultipleLocator(major_tick_interval))
plt.gca().xaxis.set_minor_locator(AutoMinorLocator(n=num_minor_ticks))

plt.gca().tick_params(which='major', length=major_tick_length, width=major_tick_width, color='black')
plt.gca().tick_params(which='minor', length=minor_tick_length, width=minor_tick_width, color='black')
plt.xticks(fontname=tick_font, fontsize=tick_font_size, fontweight=tick_font_weight)

plt.subplots_adjust(left=adjust_left, bottom=adjust_bottom, right=adjust_right, top=adjust_top)
plt.gca().get_yaxis().set_visible(False)
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)
plt.gca().spines['bottom'].set_visible(True)
plt.gca().spines['left'].set_visible(False)

# Set thickness of the axes
plt.gca().spines['bottom'].set_linewidth(axis_width)

# Save the plot as a PDF file
plt.savefig(output_pdf)
print(f"Plot from processed data saved to {output_pdf}")