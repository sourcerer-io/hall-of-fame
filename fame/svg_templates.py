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
      <circle cx="100" cy="100" r="90"/>
    </clipPath>
  </defs>
  <image clip-path="url(#circle-clip)"
      width="200" height="200" xlink:href=""/>
  <circle cx="100" cy="100" r="100"
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
    viewBox="0 0 300 200">
  <circle cx="80" cy="75" r="22" fill="{new_color}"/>
  <circle cx="140" cy="75" r="22" fill="{trending_color}"/>
  <circle cx="140" cy="135" r="22" fill="{top_color}"/>
  <g text-anchor="start"
      font-size="34" fill="#343434"
      font-family="Roboto,DejaVu Sans,Verdana,Geneva,sans-serif">
    <text x="180" y="83">weekly</text>
    <text x="180" y="143">all time</text>
  </g>
</svg>
"""

SVG_EMPTY = """
<svg xmlns="http://www.w3.org/2000/svg" version="1.1"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    viewBox="0 0 200 0">
</svg>
"""
