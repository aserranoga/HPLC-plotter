from pandas import read_csv, merge
import matplotlib.pyplot as plt
import os
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
import configparser
import sys

def get_executable_path():
    """
    This function returns the path where the script or executable is located.
    If frozen (i.e., bundled with PyInstaller), it uses the location of the executable.
    Otherwise, it uses the script's location.
    """
    if getattr(sys, 'frozen', False):  # If the script is run as a bundled executable
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))  # If running as a script

# Get the path to the executable or script
base_path = get_executable_path()

# Locate the configuration file in the same directory and read it
config_file_path = os.path.join(base_path, 'config.ini')
config = configparser.ConfigParser()
config.read(config_file_path)

# General configuration
destination_folder = config.get('General', 'destination_folder')
filename = config.get('General', 'filename')
file_paths = config.get('General', 'file_paths').split(', ')  # Convert CSV paths to a list
time_range = tuple(map(float, config.get('General', 'time_range').split(',')))
x_limits = tuple(map(float, config.get('General', 'x_limits').split(',')))
major_tick_interval = config.getfloat('General', 'major_tick_interval')
num_minor_ticks = config.getint('General', 'num_minor_ticks')

# Style configuration
# Convert the figure size from cm to inches
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

# Combine output folder and filename
output_file = os.path.join(destination_folder, filename)

def read_csv_file(file_path):
    """Read a CSV file and return a DataFrame."""
    return read_csv(file_path)

def find_peak_and_baseline(df, time_col, intensity_col, time_range):
    """Find the peak and baseline intensity within a specified time range."""
    filtered_df = df[(df[time_col] >= time_range[0]) & (df[time_col] <= time_range[1])]
    return filtered_df[intensity_col].max(), filtered_df[intensity_col].min()

def normalize_chromatogram(df, time_col, intensity_col, peak_intensity, baseline_intensity):
    """Normalize the chromatogram intensity."""
    df['normalized_intensity'] = (df[intensity_col] - baseline_intensity) / (peak_intensity - baseline_intensity) * 100
    return df

def export_data_csv(data_frames, labels, filename):
    """Save normalized chromatogram data to a CSV file."""
    base_df = data_frames[0][['min']].rename(columns={'min': 'Time (min)'})  # Start with just time points

    for i, df in enumerate(data_frames):
        sample_df = df[['min', 'Intensity', 'normalized_intensity']].copy()
        sample_df.columns = ['Time (min)', f'Original Intensity ({labels[i]})', f'Normalized Intensity ({labels[i]})']
        base_df = merge(base_df, sample_df, on='Time (min)', how='outer')
        base_df[f'Normalized Intensity (Offset) ({labels[i]})'] = df['normalized_intensity'] + i * 110

    base_df.to_csv(filename, index=False)
    print(f'Data saved to {filename}')

def plot_chromatograms(data_frames, labels, time_col='min', intensity_col='normalized_intensity', offset=110):
    """Plot chromatograms with offsets."""
    plt.figure(figsize=figure_size)
    plt.rc('font', family=font, size=font_size, weight=font_weight)

    for i, df in enumerate(data_frames):
        plt.plot(df[time_col], df[intensity_col] + i * offset, color='black', label=labels[i], linewidth=line_width)

    plt.xlabel('Time (min)')
    plt.xlim(x_limits)  
    plt.ylabel('Normalized Intensity (Offset)')
    plt.ylim(-10, offset * len(data_frames))

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

# Main workflow
data_frames = []
labels = []

for file_path in file_paths:
    df = read_csv_file(file_path)
    peak_intensity, baseline_intensity = find_peak_and_baseline(df, time_col='min', intensity_col='Intensity', time_range=time_range)
    normalized_df = normalize_chromatogram(df, time_col='min', intensity_col='Intensity', 
                                           peak_intensity=peak_intensity, baseline_intensity=baseline_intensity)
    data_frames.append(normalized_df)
    labels.append(os.path.basename(file_path))

# Reverse the order of data frames and labels
data_frames.reverse()
labels.reverse()

# Plot the chromatograms
plot_chromatograms(data_frames, labels)

# Save the plot as a PDF file
plt.savefig(f'{output_file}.pdf')

# Export all the data as csv file
export_data_csv(data_frames, labels, filename=f'{output_file}.csv')
