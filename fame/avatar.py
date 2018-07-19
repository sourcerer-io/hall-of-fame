"""Renderer renders hall of fame entries."""

__author__ = 'Sergey Surkov'
__copyright__ = '2018 Sourcerer, Inc'

import re
from xml.etree import ElementTree


class AvatarAdorner:
    SVG_GITHUB = """
    <svg xmlns="http://www.w3.org/2000/svg" version="1.1"
        xmlns:xlink="http://www.w3.org/1999/xlink"
        viewBox="0 0 200 200" width="70px" height="70px">
      <defs>
        <clipPath id="circleclip">
          <circle cx="100" cy="100" r="75"/>
        </clipPath>
      </defs>
      <image id="avatar" clip-path="url(#circleclip)"
          width="200" height="200" xlink:href=""/>
      <circle cx="100" cy="100" r="85"
          stroke="#c1c5ca" stroke-width="1.5" fill="transparent" />
    </svg>"""

    def __init__(self):
        pass

    def init_with_github(self, github_avatar_url):
        self.svg = ElementTree.fromstring(AvatarAdorner.SVG_GITHUB)
        ns = {'svg': 'http://www.w3.org/2000/svg'}
        image = self.svg.find('svg:image', namespaces=ns)
        image.set('{http://www.w3.org/1999/xlink}href', github_avatar_url)

    def adorn(self, badge, count):
        """Adorns an avatar with a badge.

        Args:
          badge: Badge type.
          count: Number to print for the badge.
        """
        self._nest_svg()
        self._estimate_badge_size(badge, count)
        self._make_space_for_badge()

        rect = ElementTree.SubElement(self.svg, 'rect')
        rect.set('width', '100%')
        rect.set('height', '100%')
        rect.set('fill', 'transparent')
        rect.set('stroke', '#333333')

    def get_avatar_svg(self):
        return ElementTree.tostring(self.svg, encoding='unicode')


    def _nest_svg(self):
        """Puts the input SVG under a nested SVG tag."""
        children = [c for c in self.svg]
        face_svg = ElementTree.SubElement(self.svg, 'svg')
        for child in children:
            self.svg.remove(child)
            face_svg.append(child)
        _, _, w, h = self.svg.get('viewBox').split(' ')
        face_svg.set('width', w)
        face_svg.set('height', h)
        self.face_svg = face_svg


    def _estimate_badge_size(self, badge, count):
        # All sizes are relative units.
        label_widths = { 'top': 50, 'new': 50, 'trending': 300 }
        self.badge_w = label_widths[badge]
        self.badge_h = 40
        self.badge_off = 10


    def _make_space_for_badge(self):
        """Makes space in the input SVG for the badge."""
        view_box = self.svg.get('viewBox')
        if not view_box:
            raise RenderingException('No viewBox found')
        _, _, w, h = map(float, view_box.split(' '))

        px_h = self.svg.get('height')
        if not px_h or not re.match(r'^\d+(\.\d+)?px$', px_h):
            raise RenderingException('SVG height not found')
        px_h = float(px_h[:-2])

        px_h *= (h + self.badge_h + self.badge_off) / h
        h += self.badge_h + self.badge_off

        px_w = self.svg.get('width')
        if not px_w or not re.match(r'^\d+(\.\d+)?px$', px_w):
            raise RenderingException('SVG witdh not found')
        px_w = float(px_w[:-2])
        if self.badge_w > w:
            # Badge is wider than face, center face with respect to the badge.
            px_w *= self.badge_w / w
            self.face_svg.set('x', '%.02f' % ((self.badge_w - w) / 2))
            w = self.badge_w
    
        self.svg.set('viewBox', '0 0 %.02f %.02f' % (w, h))
        self.svg.set('width', '%.02fpx' % px_w)
        self.svg.set('height', '%.02fpx' % px_h)


def register_svg_namespaces():
    """Some global initiaization."""
    ns = {'': 'http://www.w3.org/2000/svg',
          'xlink': 'http://www.w3.org/1999/xlink'}
    for prefix, uri in ns.items():
        ElementTree.register_namespace(prefix, uri)


register_svg_namespaces()
