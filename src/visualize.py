import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import numpy as np

def visualize_solution(solution, colors, output_file=None):
    """
    Visualize a nonogram solution as an image.
    
    Parameters:
    - solution: 2D list of characters ('-', 'a', 'b', etc.)
    - colors: List of color hex codes (#ffffff, #333333, etc.)
    - output_file: Path to save the image (if None, just display it)
    """
    height = len(solution)
    width = len(solution[0]) if height > 0 else 0
    
    # Create a numerical grid
    grid = np.zeros((height, width), dtype=int)
    
    # Map colors to integers
    color_map = {'-': 0}  # Uncolored cells are 0
    for i, color_char in enumerate(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']):
        color_map[color_char] = i + 1
    
    # Fill the grid
    for r in range(height):
        for c in range(width):
            cell = solution[r][c]
            grid[r, c] = color_map.get(cell, 0)
    
    # Set up the color mapping
    cmap_colors = [mcolors.hex2color(colors[0])]  # Background color
    for i in range(1, min(len(colors), 10)):
        cmap_colors.append(mcolors.hex2color(colors[i]))
    
    # Create a custom colormap
    cmap = mcolors.ListedColormap(cmap_colors)
    
    # Create the figure
    fig, ax = plt.figure(figsize=(width/2, height/2)), plt.gca()
    
    # Draw the grid
    img = ax.imshow(grid, cmap=cmap, vmin=0, vmax=len(cmap_colors)-1)
    
    # Add grid lines
    ax.set_xticks(np.arange(-0.5, width, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, height, 1), minor=True)
    ax.grid(which="minor", color="black", linestyle='-', linewidth=1)
    
    # Remove axis ticks
    ax.set_xticks([])
    ax.set_yticks([])
    
    # Add a legend
    patches = []
    for i, color in enumerate(cmap_colors):
        if i == 0:
            label = "Background"
        else:
            label = f"Color {chr(ord('a') + i - 1)}"
        patches.append(mpatches.Patch(color=color, label=label))
    plt.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save or show
    if output_file:
        plt.savefig(output_file, bbox_inches='tight')
        print(f"Solution visualized and saved to {output_file}")
    else:
        plt.show()
