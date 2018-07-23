"""Renderer renders hall of fame entries."""

__author__ = 'Sergey Surkov'
__copyright__ = '2018 Sourcerer, Inc'

import base64
import re
from urllib.request import urlopen
from xml.etree import ElementTree


class AvatarError(Exception):
    def __init__(self, message):
        super().__init__(message)


class AvatarAdorner:
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

    SVG_BADGE = """
    <svg>
      <defs>
        <clipPath id="badge-clip">
          <rect width="{badge_w}" height="{badge_h}" rx="5" />
        </clipPath>
      </defs>
      <g clip-path="url(#badge-clip)">
        <rect width="{label_w}" height="100%" fill="#777777"/>
        <rect x="{label_w}" width="{count_w}" height="100%"
            fill="{count_color}"/> 
      </g>
      <g text-anchor="middle" font-size="34" fill="#ffffff"
          font-family="Roboto,DejaVu Sans,Verdana,Geneva,sans-serif">
        <text x="{label_x}" y="{label_y}">{label_text}</text>
        <text x="{count_x}" y="{count_y}">{count_text}</text>
      </g>
    </svg>"""

    def init_with_face(self, face_url):
        self.svg = ElementTree.fromstring(AvatarAdorner.SVG_GITHUB)
        self._init_face_image()
        self.face_image.set(
            '{http://www.w3.org/1999/xlink}href', face_url)

    def init_with_sourcerer(self, sourcerer_avatar_url):
        response = urlopen(sourcerer_avatar_url)
        data = response.read()
        self.svg = ElementTree.fromstring(data)
        self._init_face_image()

    def adorn(self, badge, count):
        """Adorns an avatar with a badge.

        Args:
          badge: Badge type.
          count: Number to print for the badge.
        """
        self.badge = badge
        self.badge_count = count

        self._embed_face()
        self._init_sizes_and_colors()
        self._nest_svg()
        self._estimate_badge_size()
        self._make_space_for_badge()
        self._attach_badge()

    def get_avatar_svg(self):
        return ElementTree.tostring(self.svg, encoding='unicode')

    def _init_face_image(self):
        ns = {'svg': 'http://www.w3.org/2000/svg'}
        self.face_image = self.svg.find('svg:image', namespaces=ns)

    def _embed_face(self):
        """Embeds referenced face image into the SVG.

        Browsers don't display referenced images in <img>.
        """
        face_url = self.face_image.get('{http://www.w3.org/1999/xlink}href')
        BASE64_HEADER = 'data:image/jpeg;base64,'
        if face_url.startswith(BASE64_HEADER):
            return

        data = urlopen(face_url).read()
        encoded = base64.b64encode(data).decode()
        data_url = BASE64_HEADER + encoded
        self.face_image.set('{http://www.w3.org/1999/xlink}href', data_url)
        print('i Embedded JPEG %s' % face_url)

    def _init_sizes_and_colors(self):
        view_box = self.svg.get('viewBox')
        if not view_box:
            raise AvatarError('No viewBox found')
        _, _, self.face_w, self.face_h = map(float, view_box.split(' '))

        # Set SVG size to something reasonable and square.
        FACE_SIZE = '52px'
        self.svg.set('width', FACE_SIZE)
        self.svg.set('height', FACE_SIZE)

        count_colors = {
            'new': '#4CB04F', 'trending': '#2B95CF', 'top': '#F28F56' }
        self.count_color = count_colors[self.badge]

    def _nest_svg(self):
        """Puts the input SVG under a nested SVG tag."""
        children = [c for c in self.svg]
        face_svg = ElementTree.SubElement(self.svg, 'svg')
        for child in children:
            self.svg.remove(child)
            face_svg.append(child)
        face_svg.set('width', '%.02f' % self.face_w)
        face_svg.set('height', '%.02f' % self.face_h)
        self.face_svg = face_svg

    def _estimate_badge_size(self):
        # All sizes are relative units.
        label_widths = { 'top': 90, 'new': 90, 'trending': 146 }
        self.badge_count_w = len(str(self.badge_count)) * 20 + 20
        self.badge_w = label_widths[self.badge] + self.badge_count_w
        self.badge_h = 50
        self.badge_off = 10

    def _make_space_for_badge(self):
        """Makes space in the input SVG for the badge."""
        w, h = self.face_w, self.face_h

        px_h = self.svg.get('height')
        if not px_h or not re.match(r'^\d+(\.\d+)?px$', px_h):
            raise AvatarError('SVG height not found')
        px_h = float(px_h[:-2])

        px_h *= (h + self.badge_h + self.badge_off) / h
        h += self.badge_h + self.badge_off

        px_w = self.svg.get('width')
        if not px_w or not re.match(r'^\d+(\.\d+)?px$', px_w):
            raise AvatarError('SVG witdh not found')
        px_w = float(px_w[:-2])
        if self.badge_w > w:
            # Badge is wider than face, center face with respect to the badge.
            px_w *= self.badge_w / w
            self.face_svg.set('x', '%.02f' % ((self.badge_w - w) / 2))
            w = self.badge_w
    
        self.svg.set('viewBox', '0 0 %.02f %.02f' % (w, h))
        self.svg.set('width', '%.02fpx' % px_w)
        self.svg.set('height', '%.02fpx' % px_h)

    def _attach_badge(self):
        svg_badge = AvatarAdorner.SVG_BADGE.format(
           badge_w=self.badge_w, badge_h=self.badge_h,
           label_w=(self.badge_w - self.badge_count_w),
           label_x=(self.badge_w - self.badge_count_w) / 2,
           label_y=self.badge_h - 13,
           label_text=self.badge,
           count_x=self.badge_w - self.badge_count_w / 2,
           count_y=self.badge_h - 13,
           count_w=self.badge_count_w,
           count_text=str(self.badge_count), count_color=self.count_color)
        self.badge_svg = ElementTree.fromstring(svg_badge)
        self.svg.append(self.badge_svg)

        self.badge_svg.set('y', '%.02f' % (self.face_h + self.badge_off))
        if self.badge_w < self.face_w:
            x = (self.face_w - self.badge_w) / 2
            self.badge_svg.set('x', '%.02f' % x)
        self.badge_svg.set('width', '%.02f' % self.badge_w)
        self.badge_svg.set('height', '%.02f' % self.badge_h)
        self.badge_svg.set(
            'viewBox', '0 0 %.02f %.02f' % (self.badge_w, self.badge_h))

def register_svg_namespaces():
    """Some global initiaization."""
    ns = {'': 'http://www.w3.org/2000/svg',
          'xlink': 'http://www.w3.org/1999/xlink'}
    for prefix, uri in ns.items():
        ElementTree.register_namespace(prefix, uri)


register_svg_namespaces()
