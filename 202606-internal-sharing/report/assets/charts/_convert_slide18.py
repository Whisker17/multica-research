#!/usr/bin/env python3
"""Convert slide18 SVG to PNG using cairosvg."""
import xml.etree.ElementTree as ET

svg_path = '/Users/whisker/Work/research/work/multica-research/202606-internal-sharing/report/assets/charts/slide18-arc-arch.svg'
png_path = '/Users/whisker/Work/research/work/multica-research/202606-internal-sharing/report/assets/charts/slide18-arc-arch.png'

# Validate XML
ET.parse(svg_path)
print('SVG XML is valid')

# Convert to PNG
try:
    import cairosvg
    cairosvg.svg2png(url=svg_path, write_to=png_path, scale=2)
    print(f'PNG exported to {png_path}')
except ImportError:
    print('cairosvg not installed, trying rsvg-convert...')
    import subprocess
    result = subprocess.run(['rsvg-convert', '-z', '2', svg_path, '-o', png_path], capture_output=True, text=True)
    if result.returncode == 0:
        print(f'PNG exported via rsvg-convert to {png_path}')
    else:
        print(f'rsvg-convert failed: {result.stderr}')
        print('Trying sips...')
        result2 = subprocess.run(['sips', '-s', 'format', 'png', svg_path, '--out', png_path], capture_output=True, text=True)
        if result2.returncode == 0:
            print(f'PNG exported via sips to {png_path}')
        else:
            print(f'All conversion methods failed. SVG is available at {svg_path}')
