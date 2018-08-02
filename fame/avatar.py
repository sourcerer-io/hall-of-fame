"""Renderer renders hall of fame entries."""

__author__ = 'Sergey Surkov'
__copyright__ = '2018 Sourcerer, Inc'

import base64
from urllib.request import urlopen
from xml.etree import ElementTree

from .svg_templates import SVG_GITHUB, SVG_BADGE


class AvatarError(Exception):
    def __init__(self, message):
        super().__init__(message)


# Badge configuration.
BADGE_H = 50
BADGE_OFF = 10

# Labels.
TRENDING = 'trending'
NEW = 'new'
TOP = 'top'

# Badge colors.
BADGE_COLORS = {NEW: '#4CB04F', TRENDING: '#2B95CF', TOP: '#F28F56'}


class Badger:
    """Badger makes badges. In case you wonder."""
    def __init__(self):
        # A supercrude way to estimate symbol widths.
        self.symbols = {s: 20 for s in ' 0123456789abcdefghijklmnopqrstuvwxyz'}
        self.symbols.update({s: 9 for s in 'fjt'})
        self.symbols.update({s: 5 for s in 'il'})
        self.symbols.update({s: 30 for s in 'mw'})

    def make_badge(self, label, value):
        if label not in [TRENDING, NEW, TOP]:
            raise AvatarError('Invalid badge label: %s' % label)

        self.label = label
        self.value = str(value)
        self.value_color = BADGE_COLORS[self.label]

        self._estimate_badge_size()
        self._make_badge()

    def get_badge_svg_dom(self):
        return self.svg

    def get_badge_svg_string(self):
        return ElementTree.tostring(self.svg, encoding='unicode')

    def get_badge_size(self):
        return self.badge_w, self.badge_h

    def _estimate_badge_size(self):
        # All sizes are relative units.
        self.label_w = self._estimate_string_size(self.label)
        self.value_w = self._estimate_string_size(self.value)
        self.badge_w = self.label_w + self.value_w
        self.badge_h = BADGE_H

    def _estimate_string_size(self, s):
        return sum([self.symbols[c] for c in s]) + 20

    def _make_badge(self):
        svg = SVG_BADGE.format(
           badge_w=self.badge_w, badge_h=self.badge_h,
           label_w=self.label_w,
           label_x=self.label_w / 2, label_y=self.badge_h - 13,
           label_text=self.label,
           value_x=self.badge_w - self.value_w / 2,
           value_y=self.badge_h - 13,
           value_w=self.value_w,
           value_text=self.value, value_color=self.value_color)
        self.svg = ElementTree.fromstring(svg)

        self.svg.set('width', '%.02f' % self.badge_w)
        self.svg.set('height', '%.02f' % self.badge_h)
        self.svg.set(
            'viewBox', '0 0 %.02f %.02f' % (self.badge_w, self.badge_h))


class AvatarAdorner:
    def init_with_face(self, face_url):
        self.svg = ElementTree.fromstring(SVG_GITHUB)
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
        if badge not in [TRENDING, NEW, TOP]:
            raise AvatarError('Invalid badge: %s' % badge)

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
        if not face_url.startswith('http'):
            # Relative path.
            face_url = 'https://sourcerer.io' + face_url

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

        self.count_color = BADGE_COLORS[self.badge]

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
        label_widths = {TOP: 90, NEW: 90, TRENDING: 146}
        self.badge_count_w = len(str(self.badge_count)) * 20 + 20
        self.badge_w = label_widths[self.badge] + self.badge_count_w
        self.badge_h = BADGE_H
        self.badge_off = BADGE_OFF

    def _make_space_for_badge(self):
        """Makes space in the input SVG for the badge."""
        w, h = self.face_w, self.face_h
        h += self.badge_h + self.badge_off

        if self.badge_w > w:
            # Badge is wider than face, center face with respect to the badge.
            self.face_svg.set('x', '%.02f' % ((self.badge_w - w) / 2))
            w = self.badge_w

        self.svg.set('viewBox', '0 0 %.02f %.02f' % (w, h))

    def _attach_badge(self):
        svg_badge = SVG_BADGE.format(
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
