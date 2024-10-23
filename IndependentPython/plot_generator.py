import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from matplotlib.ticker import MultipleLocator, AutoMinorLocator

# File paths to your CSV files
file_paths = [
    '/Users/arnau/Desktop/data/2024-10-09 ASERRANO-DIM-035-t0 (05).csv',
    '/Users/arnau/Desktop/data/2024-10-11 ASERRANO-DIM-035-2day (06).csv',
    '/Users/arnau/Desktop/data/2024-10-11_2 ASERRANO-DIM-035-repurified (06).csv',
    '/Users/arnau/Desktop/data/2024-10-16_2 ASERRANO-DIM-035-rerepurified-SemiprepC4-product-repeat (06).csv',
    '/Users/arnau/Desktop/data/2024-10-21 ASERRANO-DIM-035-rererepurified_C18prep_good-repeat (05).csv'
]

def read_csv(file_path):
    """Read a CSV file and return a DataFrame."""
    return pd.read_csv(file_path)

def find_peak_and_baseline(df, time_col, intensity_col, time_range=(10, 14)):
    """Find the peak and baseline intensity within a specified time range."""
    filtered_df = df[(df[time_col] >= time_range[0]) & (df[time_col] <= time_range[1])]
    return filtered_df[intensity_col].max(), filtered_df[intensity_col].min()

def normalize_chromatogram(df, time_col, intensity_col, peak_intensity, baseline_intensity):
    """Normalize the chromatogram intensity."""
    df['normalized_intensity'] = (df[intensity_col] - baseline_intensity) / (peak_intensity - baseline_intensity) * 100
    return df

def save_data_for_prism(data_frames, labels, filename='chromatogram_data.csv'):
    """Save normalized chromatogram data to a CSV file for Prism."""
    base_df = data_frames[0][['min']].rename(columns={'min': 'Time (min)'})  # Start with just time points

    for i, df in enumerate(data_frames):
        sample_df = df[['min', 'Intensity', 'normalized_intensity']].copy()
        sample_df.columns = ['Time (min)', f'Original Intensity ({labels[i]})', f'Normalized Intensity ({labels[i]})']
        base_df = pd.merge(base_df, sample_df, on='Time (min)', how='outer')
        base_df[f'Normalized Intensity (Offset) ({labels[i]})'] = df['normalized_intensity'] + i * 110

    base_df.to_csv(filename, index=False)
    print(f'Data saved to {filename}')

def plot_chromatograms(data_frames, labels, time_col='min', intensity_col='normalized_intensity', 
                       offset=110, font='Arial', font_size=9, major_tick_interval=5, num_minor_ticks=4):
    """Plot chromatograms with offsets."""
    plt.figure(figsize=(3, 3))
    plt.rc('font', family=font, size=font_size)

    for i, df in enumerate(data_frames):
        plt.plot(df[time_col], df[intensity_col] + i * offset, color='black', label=labels[i])

    plt.xlabel('Time (min)')
    plt.xlim(9, 16)  
    plt.ylabel('Normalized Intensity (Offset)')
    plt.ylim(-10, offset * len(data_frames))

    plt.gca().xaxis.set_major_locator(MultipleLocator(major_tick_interval))
    plt.gca().xaxis.set_minor_locator(AutoMinorLocator(n=num_minor_ticks))
    plt.gca().tick_params(which='major', length=4, width=1, color='black')
    plt.gca().tick_params(which='minor', length=2, width=1, color='black')
    plt.xticks(fontname=font, fontsize=font_size)

    plt.subplots_adjust(left=0.12, bottom=0.14, right=0.88, top=0.9)
    plt.gca().get_yaxis().set_visible(False)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(True)
    plt.gca().spines['left'].set_visible(False)
    
    # Set thickness of the axes
    spine_thickness = 1.5
    plt.gca().spines['bottom'].set_linewidth(spine_thickness)

# Main workflow
data_frames = []
labels = []

for file_path in file_paths:
    df = read_csv(file_path)
    peak_intensity, baseline_intensity = find_peak_and_baseline(df, time_col='min', intensity_col='Intensity')
    normalized_df = normalize_chromatogram(df, time_col='min', intensity_col='Intensity', 
                                           peak_intensity=peak_intensity, baseline_intensity=baseline_intensity)
    data_frames.append(normalized_df)
    labels.append(os.path.basename(file_path))

# Save data for Prism
save_data_for_prism(data_frames, labels)

# Reverse the order of data frames and labels
data_frames.reverse()
labels.reverse()

# Plot the chromatograms
plot_chromatograms(data_frames, labels)

# Save the plot as a PNG file
plt.savefig('/Users/arnau/Desktop/data/hplc_plot.png', dpi=600)

# Show the plot
plt.show()
