"""SVG templates."""

__author__ = 'Sergey Surkov'
__copyright__ = '2018 Sourcerer, Inc'

# GitHub avatar wrapped in SVG.
SVG_GITHUB = """
<svg xmlns="http://www.w3.org/2000/svg" version="1.1"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    viewBox="0 0 200 200">
  <defs>
    <clipPath id="circle-clip">
      <circle cx="100" cy="100" r="85"/>
    </clipPath>
  </defs>
  <image clip-path="url(#circle-clip)"
      width="200" height="200" xlink:href=""/>
  <circle cx="100" cy="100" r="95"
      stroke="#c1c5ca" stroke-width="1.5" fill="transparent" />
</svg>"""

# SVG badge.
SVG_BADGE = """
<svg xmlns="http://www.w3.org/2000/svg" version="1.1"
    xmlns:xlink="http://www.w3.org/1999/xlink">
  <defs>
    <clipPath id="badge-clip">
      <rect width="{badge_w}" height="{badge_h}" rx="5" />
    </clipPath>
  </defs>
  <g clip-path="url(#badge-clip)">
    <rect width="{label_w}" height="100%" fill="#777777"/>
    <rect x="{label_w}" width="{value_w}" height="100%"
        fill="{value_color}"/>
  </g>
  <g text-anchor="middle" font-size="34" fill="#ffffff"
      font-family="Roboto,DejaVu Sans,Verdana,Geneva,sans-serif">
    <text x="{label_x}" y="{label_y}">{label_text}</text>
    <text x="{value_x}" y="{value_y}">{value_text}</text>
  </g>
</svg>"""

# Legend.
SVG_LEGEND = """
<svg xmlns="http://www.w3.org/2000/svg" version="1.1"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    viewBox="0 0 200 200">
</svg>
"""

SVG_EMPTY = """
<svg xmlns="http://www.w3.org/2000/svg" version="1.1"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    viewBox="0 0 200 0">
</svg>
"""
