#!/usr/bin/env python3
# vc-media-popup.py — Popup audio + luminosité violet-chaton
# Lancé depuis le clic sur wireplumber OU backlight

import gi
import math
import threading
import urllib.request

gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
gi.require_version('GdkPixbuf', '2.0')
gi.require_version('Pango', '1.0')
gi.require_version('PangoCairo', '1.0')
from gi.repository import Gtk, Gdk, GtkLayerShell, GLib, GdkPixbuf, Pango, PangoCairo
import subprocess
import os
import re

# ── CSS ───────────────────────────────────────────────────────────────────────

CSS = """
window {
    background-color: rgba(52, 28, 74, 0.93);
    border: 3px solid rgba(255, 121, 198, 0.78);
    border-radius: 14px;
}

#container {
    padding: 14px 20px 16px 20px;
}

/* ── Labels ────────────────────────────────────────────────────────────────── */

#section-label {
    color: #ff79c6;
    font-family: "JetBrainsMono Nerd Font";
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 0.08em;
}

#device-name {
    color: rgba(248, 248, 242, 0.75);
    font-family: "JetBrainsMono Nerd Font";
    font-size: 11px;
}

#pct-label {
    color: #f8f8f2;
    font-family: "JetBrainsMono Nerd Font";
    font-size: 12px;
    font-weight: bold;
    min-width: 38px;
}

#separator {
    color: rgba(92, 73, 108, 0.50);
    margin: 6px 0 4px 0;
}

/* ── Boutons mute (icônes cliquables) ───────────────────────────────────────── */

#mute-icon {
    font-family: "JetBrainsMono Nerd Font";
    font-size: 17px;
    color: #ff79c6;
    background: transparent;
    border: none;
    border-radius: 6px;
    padding: 0 4px;
    min-width: 28px;
}

#mute-icon:hover {
    background: rgba(255, 121, 198, 0.15);
}

#mute-icon.muted {
    color: rgba(243, 139, 168, 0.70);
}

#mic-icon {
    font-family: "JetBrainsMono Nerd Font";
    font-size: 17px;
    color: #ff79c6;
    background: transparent;
    border: none;
    border-radius: 6px;
    padding: 0 4px;
    min-width: 28px;
}

#mic-icon:hover {
    background: rgba(255, 121, 198, 0.15);
}

#mic-icon.muted {
    color: rgba(243, 139, 168, 0.70);
}

/* ── Sliders audio (rose) ───────────────────────────────────────────────────── */

scale.audio {
    min-height: 22px;
}

scale.audio trough {
    background-color: rgba(92, 73, 108, 0.55);
    border-radius: 3px;
    min-height: 5px;
    border: none;
}

scale.audio trough highlight {
    background-color: #ff79c6;
    min-height: 6px;
    border-radius: 3px;
    border: none;
}

scale.audio.muted trough highlight {
    background-color: rgba(108, 112, 134, 0.40);
}

scale.audio slider {
    background-color: #f8f8f2;
    border-radius: 50%;
    min-width: 16px;
    min-height: 16px;
    border: 2px solid rgba(255, 121, 198, 0.80);
    box-shadow: none;
    transition: none;
}

scale.audio slider:hover {
    background-color: #e79cfe;
    border-color: #ff79c6;
}

scale.audio.muted slider {
    border-color: rgba(108, 112, 134, 0.60);
}

/* ── Sélecteur de périphérique de sortie ────────────────────────────────────── */

#device-btn {
    background-color: transparent;
    color: rgba(248, 248, 242, 0.65);
    font-family: "JetBrainsMono Nerd Font";
    font-size: 11px;
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 5px 10px;
    min-width: 0;
}

#device-btn:hover {
    background-color: rgba(91, 70, 113, 0.55);
    color: #f8f8f2;
    border-color: rgba(92, 73, 108, 0.60);
}

#device-btn.active {
    background-color: rgba(255, 121, 198, 0.14);
    color: #ff79c6;
    border-color: rgba(255, 121, 198, 0.55);
}

/* ── Slider luminosité (cyan) ───────────────────────────────────────────────── */

scale.bright {
    min-height: 22px;
}

scale.bright trough {
    background-color: rgba(92, 73, 108, 0.55);
    border-radius: 3px;
    min-height: 5px;
    border: none;
}

scale.bright trough highlight {
    background-color: #8be9fd;
    min-height: 6px;
    border-radius: 3px;
    border: none;
}

scale.bright slider {
    background-color: #f8f8f2;
    border-radius: 50%;
    min-width: 16px;
    min-height: 16px;
    border: 2px solid rgba(139, 233, 253, 0.80);
    box-shadow: none;
    transition: none;
}

scale.bright slider:hover {
    background-color: #8be9fd;
    border-color: #8be9fd;
}

#bright-icon {
    color: #8be9fd;
    font-family: "JetBrainsMono Nerd Font";
    font-size: 17px;
    min-width: 28px;
}

/* ── Section MPRIS ────────────────────────────────────────────────────────── */

#mpris-title {
    color: #f8f8f2;
    font-family: "JetBrainsMono Nerd Font";
    font-size: 12px;
    font-weight: bold;
}

#mpris-artist {
    color: rgba(248, 248, 242, 0.55);
    font-family: "JetBrainsMono Nerd Font";
    font-size: 11px;
}

#mpris-btn {
    background-color: transparent;
    color: #e79cfe;
    font-family: "JetBrainsMono Nerd Font";
    font-size: 16px;
    border: none;
    border-radius: 6px;
    padding: 4px 8px;
    min-width: 0;
}

#mpris-btn:hover {
    background-color: rgba(231, 156, 254, 0.15);
}

#mpris-btn.play {
    font-size: 20px;
    color: #ff79c6;
    padding: 4px 12px;
}

#mpris-btn.play:hover {
    background-color: rgba(255, 121, 198, 0.15);
}
"""

POPUP_WIDTH = 310

# ── Helpers ───────────────────────────────────────────────────────────────────

def run(cmd, env=None, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=2,
                          env=env, **kw)

def get_sink_volume():
    r = run(['wpctl', 'get-volume', '@DEFAULT_AUDIO_SINK@'])
    parts = r.stdout.strip().split()
    vol = int(float(parts[1]) * 100) if len(parts) >= 2 else 50
    return min(max(vol, 0), 100), '[MUTED]' in r.stdout

def get_source_volume():
    r = run(['wpctl', 'get-volume', '@DEFAULT_AUDIO_SOURCE@'])
    parts = r.stdout.strip().split()
    vol = int(float(parts[1]) * 100) if len(parts) >= 2 else 50
    return min(max(vol, 0), 100), '[MUTED]' in r.stdout

def get_node_name(target):
    r = run(['wpctl', 'inspect', target])
    for field in ('node.description', 'node.nick'):
        m = re.search(rf'{field}\s*=\s*"([^"]+)"', r.stdout)
        if m:
            return m.group(1)
    return target

def set_sink_vol(v):
    run(['wpctl', 'set-volume', '-l', '1.0', '@DEFAULT_AUDIO_SINK@', f'{v}%'])
    _wob(f'v:{v}')

def set_source_vol(v):
    run(['wpctl', 'set-volume', '@DEFAULT_AUDIO_SOURCE@', f'{v}%'])
    _wob(f'v:{v}')

def toggle_sink_mute():
    run(['wpctl', 'set-mute', '@DEFAULT_AUDIO_SINK@', 'toggle'])

def toggle_source_mute():
    run(['wpctl', 'set-mute', '@DEFAULT_AUDIO_SOURCE@', 'toggle'])

def get_brightness():
    r = run(['brightnessctl', 'info'])
    m = re.search(r'\((\d+)%\)', r.stdout)
    return int(m.group(1)) if m else 50

def set_brightness(v):
    v = max(1, v)
    run(['brightnessctl', 'set', f'{v}%', '-q'])
    _wob(f'b:{v}')

def _wob(msg):
    fifo = '/tmp/wob.fifo'
    if os.path.exists(fifo):
        try:
            fd = os.open(fifo, os.O_WRONLY | os.O_NONBLOCK)
            os.write(fd, f'{msg}\n'.encode())
            os.close(fd)
        except OSError:
            pass

def get_sinks():
    """Retourne [(sink_name, description, is_default)] — exclut SUSPENDED."""
    env = {**os.environ, 'LANG': 'C', 'LC_ALL': 'C'}
    r_default = run(['pactl', 'get-default-sink'], env=env)
    default_name = r_default.stdout.strip()

    r_full = run(['pactl', 'list', 'sinks'], env=env)
    sinks, state, name, desc = [], None, None, None
    for line in r_full.stdout.splitlines():
        st = re.search(r'^\s+State:\s+(\S+)', line)
        nm = re.search(r'^\s+Name:\s+(.+)$', line)
        ds = re.search(r'^\s+Description:\s+(.+)$', line)
        if st: state = st.group(1)
        elif nm: name = nm.group(1).strip()
        elif ds and name:
            desc = ds.group(1).strip()
            if state != 'SUSPENDED':
                sinks.append((name, desc, name == default_name))
            state, name, desc = None, None, None
    return sinks

def set_default_sink(name):
    run(['pactl', 'set-default-sink', name])

def get_sources():
    """Retourne [(source_name, description, is_default)] — exclut les .monitor."""
    env = {**os.environ, 'LANG': 'C', 'LC_ALL': 'C'}
    r_default = run(['pactl', 'get-default-source'], env=env)
    default_name = r_default.stdout.strip()

    r_full = run(['pactl', 'list', 'sources'], env=env)
    sources, name, desc = [], None, None
    for line in r_full.stdout.splitlines():
        nm = re.search(r'^\s+Name:\s+(.+)$', line)
        ds = re.search(r'^\s+Description:\s+(.+)$', line)
        if nm:
            name = nm.group(1).strip()
        elif ds and name:
            desc = ds.group(1).strip()
            if '.monitor' not in name:
                sources.append((name, desc, name == default_name))
            name, desc = None, None
    return sources

def set_default_source(name):
    run(['pactl', 'set-default-source', name])

def get_mpris_info():
    """Retourne dict ou None si pas de lecteur actif."""
    try:
        r = run(['playerctl', 'metadata', '--format',
                 '{{title}}||{{artist}}||{{mpris:artUrl}}||{{status}}'])
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if r.returncode != 0 or not r.stdout.strip():
        return None
    parts = r.stdout.strip().split('||', 3)
    if len(parts) < 4:
        return None
    title, artist, art_url, status = [p.strip() for p in parts]
    if not title:
        return None
    return {
        'title':   title,
        'artist':  artist,
        'art_url': art_url,
        'status':  status.lower(),   # 'playing' | 'paused' | 'stopped'
    }

def source_icon(name, desc):
    s = (name + desc).lower()
    if 'bluetooth' in s or 'bluez' in s: return '󰥰'
    if 'usb' in s:                        return '󱡬'
    if 'headset' in s or 'headphone' in s: return '󰋎'
    return '󰍬'

def sink_icon(name, desc):
    s = (name + desc).lower()
    if 'hdmi' in s or 'dp-' in s or 'displayport' in s: return '󰡁'
    if 'bluetooth' in s or 'bluez' in s:                 return '󰥰'
    if 'usb' in s:                                        return '󱡬'
    if 'headphone' in s or 'headset' in s:               return '󰋋'
    return '󰓃'

def short_desc(desc, maxlen=16):
    return desc if len(desc) <= maxlen else desc[:maxlen - 1] + '…'

def vol_icon(muted):
    return '󰖁' if muted else '󰕾'

def mic_icon(muted):
    return '󰍭' if muted else '󰍬'

def bright_icon(pct):
    if pct < 34: return '󰃞'
    if pct < 67: return '󰃟'
    return '󰃠'

# ── Art widget (album art / miniature YouTube) ────────────────────────────────

class ArtWidget(Gtk.DrawingArea):
    SIZE = 72

    def __init__(self):
        super().__init__()
        self._pixbuf = None
        self._url    = None
        self.set_size_request(self.SIZE, self.SIZE)
        self.connect('draw', self._on_draw)

    def load_url(self, url):
        if url == self._url:
            return
        self._url    = url
        self._pixbuf = None
        self.queue_draw()
        if not url:
            return
        threading.Thread(target=self._fetch, args=(url,), daemon=True).start()

    def _fetch(self, url):
        try:
            if url.startswith('file://'):
                raw = GdkPixbuf.Pixbuf.new_from_file(url[7:])
            else:
                req = urllib.request.Request(
                    url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=5) as resp:
                    data = resp.read()
                loader = GdkPixbuf.PixbufLoader()
                loader.write(data)
                loader.close()
                raw = loader.get_pixbuf()

            if raw:
                s  = self.SIZE
                ow, oh = raw.get_width(), raw.get_height()
                scale  = min(s / ow, s / oh)
                nw = max(1, int(ow * scale))
                nh = max(1, int(oh * scale))
                pixbuf = raw.scale_simple(nw, nh, GdkPixbuf.InterpType.BILINEAR)
            else:
                pixbuf = None
        except Exception:
            pixbuf = None
        GLib.idle_add(self._set_pixbuf, pixbuf, url)

    def _set_pixbuf(self, pixbuf, url):
        if url == self._url:
            self._pixbuf = pixbuf
            self.queue_draw()
        return False

    def _on_draw(self, _widget, cr):
        s, r = self.SIZE, 10

        # Coins arrondis (clip)
        cr.new_sub_path()
        cr.arc(r,     r,     r, math.pi,       3 * math.pi / 2)
        cr.arc(s - r, r,     r, -math.pi / 2,  0)
        cr.arc(s - r, s - r, r, 0,              math.pi / 2)
        cr.arc(r,     s - r, r, math.pi / 2,   math.pi)
        cr.close_path()
        cr.clip()

        # Fond violet
        cr.set_source_rgba(73/255, 49/255, 97/255, 0.85)
        cr.paint()

        if self._pixbuf:
            pw = self._pixbuf.get_width()
            ph = self._pixbuf.get_height()
            Gdk.cairo_set_source_pixbuf(cr, self._pixbuf,
                                        (s - pw) / 2, (s - ph) / 2)
            cr.paint()
        else:
            # Icône note de musique (placeholder)
            layout = PangoCairo.create_layout(cr)
            layout.set_markup('<span font="JetBrainsMono Nerd Font 24">󰝚</span>')
            lw, lh = layout.get_size()
            cr.set_source_rgba(231/255, 156/255, 254/255, 0.45)
            cr.move_to((s - lw / Pango.SCALE) / 2,
                       (s - lh / Pango.SCALE) / 2)
            PangoCairo.show_layout(cr, layout)


# ── Popup ─────────────────────────────────────────────────────────────────────

class MediaPopup(Gtk.Window):
    def __init__(self):
        super().__init__()
        self._blk       = False
        self._has_mpris = False

        # ── Position — ancré à droite, toujours dans l'écran ─────────────────
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.OVERLAY)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT, True)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.TOP, 66)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.RIGHT, 12)
        GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.ON_DEMAND)
        GtkLayerShell.set_exclusive_zone(self, -1)
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_default_size(POPUP_WIDTH, -1)

        # ── CSS ───────────────────────────────────────────────────────────────
        provider = Gtk.CssProvider()
        provider.load_from_data(CSS.encode())
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # ── États initiaux ────────────────────────────────────────────────────
        sink_vol, sink_muted   = get_sink_volume()
        src_vol,  src_muted    = get_source_volume()
        self._sink_muted = sink_muted
        self._src_muted  = src_muted

        # ── Layout ────────────────────────────────────────────────────────────
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        box.set_name('container')
        self.add(box)

        # ╔═══ LECTURE (MPRIS) — affiché seulement si lecteur actif ════════════╗
        mpris_info = get_mpris_info()
        if mpris_info:
            self._build_mpris_section(box, mpris_info)
            sep0 = Gtk.Label(label='─' * 34)
            sep0.set_name('separator')
            box.pack_start(sep0, False, False, 0)

        # ╔═══ SORTIE ══════════════════════════════════════════════════════════╗
        sinks = get_sinks()
        box.pack_start(self._section_header('SORTIE', '󰕾'), False, False, 0)
        self.sink_device_lbl = self._device_label(
            get_node_name('@DEFAULT_AUDIO_SINK@'))
        box.pack_start(self.sink_device_lbl, False, False, 2)
        if len(sinks) > 1:
            box.pack_start(self._sink_selector(sinks), False, False, 4)
        sink_row, self.sink_scale, self.sink_pct, self.sink_icon = \
            self._slider_row(sink_vol, sink_muted, 'audio', vol_icon(sink_muted),
                             self._toggle_sink_mute, '@DEFAULT_AUDIO_SINK@')
        box.pack_start(sink_row, False, False, 4)

        # ╔═══ ENTRÉE ══════════════════════════════════════════════════════════╗
        sep1 = Gtk.Label(label='─' * 34)
        sep1.set_name('separator')
        box.pack_start(sep1, False, False, 0)

        sources = get_sources()
        box.pack_start(self._section_header('ENTRÉE', '󰍬'), False, False, 0)
        self.src_device_lbl = self._device_label(
            get_node_name('@DEFAULT_AUDIO_SOURCE@'))
        box.pack_start(self.src_device_lbl, False, False, 2)
        if len(sources) > 1:
            box.pack_start(self._source_selector(sources), False, False, 4)
        src_row, self.src_scale, self.src_pct, self.src_icon = \
            self._slider_row(src_vol, src_muted, 'audio', mic_icon(src_muted),
                             self._toggle_src_mute, '@DEFAULT_AUDIO_SOURCE@')
        box.pack_start(src_row, False, False, 4)

        # ╔═══ LUMINOSITÉ ══════════════════════════════════════════════════════╗
        sep2 = Gtk.Label(label='─' * 34)
        sep2.set_name('separator')
        box.pack_start(sep2, False, False, 0)

        bright_row, self.bright_scale, self.bright_pct, self.bright_icon_lbl = \
            self._bright_row(get_brightness())
        box.pack_start(bright_row, False, False, 6)

        # ── Refresh + fermeture ───────────────────────────────────────────────
        GLib.timeout_add(2000, self._refresh)
        self.connect('key-press-event', lambda w, e:
                     self.destroy() if e.keyval == Gdk.KEY_Escape else None)
        self.connect('focus-out-event', lambda *_: self.destroy())
        self.show_all()
        # GTK3 bug : set_value() avant réalisation → highlight width=0 à max
        GLib.idle_add(self._redraw_scales)
        self.grab_focus()

    # ── MPRIS section builder ─────────────────────────────────────────────────

    def _build_mpris_section(self, box, info):
        box.pack_start(self._section_header('LECTURE', '󰝚'), False, False, 0)

        content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        content.set_margin_top(4)
        content.set_margin_bottom(4)

        # Album art
        self.mpris_art = ArtWidget()
        content.pack_start(self.mpris_art, False, False, 0)

        # Infos + contrôles
        info_col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        info_col.set_valign(Gtk.Align.CENTER)

        self.mpris_title = Gtk.Label(label=info['title'])
        self.mpris_title.set_name('mpris-title')
        self.mpris_title.set_halign(Gtk.Align.START)
        self.mpris_title.set_ellipsize(3)
        self.mpris_title.set_max_width_chars(20)
        info_col.pack_start(self.mpris_title, False, False, 0)

        self.mpris_artist = Gtk.Label(label=info['artist'] or '—')
        self.mpris_artist.set_name('mpris-artist')
        self.mpris_artist.set_halign(Gtk.Align.START)
        self.mpris_artist.set_ellipsize(3)
        self.mpris_artist.set_max_width_chars(20)
        info_col.pack_start(self.mpris_artist, False, False, 0)

        # Contrôles prev / play-pause / next
        ctrl = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        ctrl.set_margin_top(4)

        btn_prev = Gtk.Button(label='󰒮')
        btn_prev.set_name('mpris-btn')
        btn_prev.connect('clicked', lambda _: run(['playerctl', 'previous']))

        self.btn_play = Gtk.Button(
            label='󰏤' if info['status'] == 'playing' else '󰐊')
        self.btn_play.set_name('mpris-btn')
        self.btn_play.get_style_context().add_class('play')
        self.btn_play.connect('clicked', self._on_play_pause)

        btn_next = Gtk.Button(label='󰒭')
        btn_next.set_name('mpris-btn')
        btn_next.connect('clicked', lambda _: run(['playerctl', 'next']))

        ctrl.pack_start(btn_prev,       False, False, 0)
        ctrl.pack_start(self.btn_play,  False, False, 0)
        ctrl.pack_start(btn_next,       False, False, 0)
        info_col.pack_start(ctrl, False, False, 0)

        content.pack_start(info_col, True, True, 0)
        box.pack_start(content, False, False, 4)

        # Charger l'artwork en arrière-plan
        if info.get('art_url'):
            self.mpris_art.load_url(info['art_url'])

        self._has_mpris   = True
        self._mpris_status = info['status']

    def _on_play_pause(self, _btn):
        run(['playerctl', 'play-pause'])
        info = get_mpris_info()
        if info and self._has_mpris:
            self._mpris_status = info['status']
            self.btn_play.set_label(
                '󰏤' if info['status'] == 'playing' else '󰐊')

    # ── Sélecteur de sortie ────────────────────────────────────────────────────

    def _sink_selector(self, sinks):
        self._sink_btns  = {}
        self._sink_descs = {}
        col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        for name, desc, is_default in sinks:
            self._sink_descs[name] = desc
            btn = Gtk.Button()
            btn.set_name('device-btn')
            btn.set_hexpand(True)
            lbl = Gtk.Label(label=self._sink_label(name, desc, is_default))
            lbl.set_halign(Gtk.Align.START)
            btn.add(lbl)
            if is_default:
                btn.get_style_context().add_class('active')
            btn.connect('clicked', self._on_sink_selected, name)
            col.pack_start(btn, False, True, 0)
            self._sink_btns[name] = btn
        return col

    def _sink_label(self, name, desc, active):
        check = '  ' if active else ''
        return f'{sink_icon(name, desc)}  {desc}{check}'

    def _source_selector(self, sources):
        self._src_btns  = {}
        self._src_descs = {}
        col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        for name, desc, is_default in sources:
            self._src_descs[name] = desc
            btn = Gtk.Button()
            btn.set_name('device-btn')
            btn.set_hexpand(True)
            lbl = Gtk.Label(label=self._src_label(name, desc, is_default))
            lbl.set_halign(Gtk.Align.START)
            btn.add(lbl)
            if is_default:
                btn.get_style_context().add_class('active')
            btn.connect('clicked', self._on_source_selected, name)
            col.pack_start(btn, False, True, 0)
            self._src_btns[name] = btn
        return col

    def _src_label(self, name, desc, active):
        check = '  ' if active else ''
        return f'{source_icon(name, desc)}  {desc}{check}'

    def _on_source_selected(self, _btn, name):
        for n, b in self._src_btns.items():
            b.get_style_context().remove_class('active')
            b.get_child().set_label(self._src_label(n, self._src_descs[n], False))
        self._src_btns[name].get_style_context().add_class('active')
        self._src_btns[name].get_child().set_label(
            self._src_label(name, self._src_descs[name], True))
        set_default_source(name)
        self.src_device_lbl.set_label(self._src_descs[name])
        vol, muted = get_source_volume()
        self._blk = True
        self.src_scale.set_value(vol)
        self.src_pct.set_label(f'{vol}%')
        self._blk = False
        self._src_muted = muted
        self._apply_mute(self.src_scale, self.src_icon, muted, mic_icon)
        subprocess.Popen(['pkill', '-RTMIN+1', 'waybar'],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def _on_sink_selected(self, _btn, name):
        for n, b in self._sink_btns.items():
            b.get_style_context().remove_class('active')
            b.get_child().set_label(
                self._sink_label(n, self._sink_descs[n], False))
        self._sink_btns[name].get_style_context().add_class('active')
        self._sink_btns[name].get_child().set_label(
            self._sink_label(name, self._sink_descs[name], True))
        set_default_sink(name)
        self.sink_device_lbl.set_label(self._sink_descs[name])
        vol, muted = get_sink_volume()
        self._blk = True
        self.sink_scale.set_value(vol)
        self.sink_pct.set_label(f'{vol}%')
        self._blk = False
        self._sink_muted = muted
        self._apply_mute(self.sink_scale, self.sink_icon, muted, vol_icon)
        subprocess.Popen(['pkill', '-RTMIN+1', 'waybar'],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # ── Builders UI ───────────────────────────────────────────────────────────

    def _section_header(self, label, icon):
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        ico = Gtk.Label(label=icon)
        ico.set_name('section-label')
        row.pack_start(ico, False, False, 0)
        lbl = Gtk.Label(label=label)
        lbl.set_name('section-label')
        lbl.set_halign(Gtk.Align.START)
        row.pack_start(lbl, True, True, 0)
        return row

    def _device_label(self, name):
        lbl = Gtk.Label(label=name)
        lbl.set_name('device-name')
        lbl.set_halign(Gtk.Align.START)
        lbl.set_ellipsize(3)
        lbl.set_margin_start(4)
        return lbl

    def _slider_row(self, val, muted, css_class, icon_char, mute_cb, target):
        """Retourne (row, scale, pct_label, icon_btn)"""
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        icon_btn = Gtk.Button(label=icon_char)
        icon_btn.set_name('mute-icon' if target == '@DEFAULT_AUDIO_SINK@' else 'mic-icon')
        if muted:
            icon_btn.get_style_context().add_class('muted')
        icon_btn.connect('clicked', mute_cb)
        row.pack_start(icon_btn, False, False, 0)

        scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 5)
        scale.set_value(val)
        scale.set_draw_value(False)
        scale.set_hexpand(True)
        scale.get_style_context().add_class(css_class)
        if muted:
            scale.get_style_context().add_class('muted')
        scale.connect('value-changed', lambda s, t=target:
                      self._on_audio_changed(s, pct_lbl, t))
        row.pack_start(scale, True, True, 0)

        pct_lbl = Gtk.Label(label=f'{val}%')
        pct_lbl.set_name('pct-label')
        pct_lbl.set_halign(Gtk.Align.END)
        row.pack_end(pct_lbl, False, False, 0)

        return row, scale, pct_lbl, icon_btn

    def _bright_row(self, pct):
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        icon_lbl = Gtk.Label(label=bright_icon(pct))
        icon_lbl.set_name('bright-icon')
        row.pack_start(icon_lbl, False, False, 0)

        scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 1, 100, 5)
        scale.set_value(pct)
        scale.set_draw_value(False)
        scale.set_hexpand(True)
        scale.get_style_context().add_class('bright')
        scale.connect('value-changed', self._on_bright_changed)
        row.pack_start(scale, True, True, 0)

        pct_lbl = Gtk.Label(label=f'{pct}%')
        pct_lbl.set_name('pct-label')
        pct_lbl.set_halign(Gtk.Align.END)
        row.pack_end(pct_lbl, False, False, 0)

        return row, scale, pct_lbl, icon_lbl

    # ── Handlers ──────────────────────────────────────────────────────────────

    def _on_audio_changed(self, scale, pct_lbl, target):
        if self._blk:
            return
        v = int(scale.get_value())
        pct_lbl.set_label(f'{v}%')
        if target == '@DEFAULT_AUDIO_SINK@':
            set_sink_vol(v)
        else:
            set_source_vol(v)

    def _on_bright_changed(self, scale):
        if self._blk:
            return
        v = int(scale.get_value())
        self.bright_pct.set_label(f'{v}%')
        self.bright_icon_lbl.set_label(bright_icon(v))
        set_brightness(v)

    def _apply_mute(self, scale, icon_btn, muted, icon_fn):
        sc = scale.get_style_context()
        bc = icon_btn.get_style_context()
        if muted:
            sc.add_class('muted')
            bc.add_class('muted')
        else:
            sc.remove_class('muted')
            bc.remove_class('muted')
        icon_btn.set_label(icon_fn(muted))

    def _toggle_sink_mute(self, _btn):
        toggle_sink_mute()
        _, self._sink_muted = get_sink_volume()
        self._apply_mute(self.sink_scale, self.sink_icon,
                         self._sink_muted, vol_icon)

    def _toggle_src_mute(self, _btn):
        toggle_source_mute()
        _, self._src_muted = get_source_volume()
        self._apply_mute(self.src_scale, self.src_icon,
                         self._src_muted, mic_icon)

    def _redraw_scales(self):
        """Force GTK3 à recalculer les highlights."""
        self._blk = True
        for scale in [self.sink_scale, self.src_scale, self.bright_scale]:
            v   = scale.get_value()
            adj = scale.get_adjustment()
            lo  = adj.get_lower()
            scale.set_value(max(lo, v - 1))
            scale.set_value(v)
        self._blk = False
        return False

    def _refresh(self):
        # ── Audio ──────────────────────────────────────────────────────────────
        sink_vol, sink_muted = get_sink_volume()
        src_vol,  src_muted  = get_source_volume()

        if sink_muted != self._sink_muted:
            self._sink_muted = sink_muted
            self._apply_mute(self.sink_scale, self.sink_icon,
                             sink_muted, vol_icon)
        if src_muted != self._src_muted:
            self._src_muted = src_muted
            self._apply_mute(self.src_scale, self.src_icon,
                             src_muted, mic_icon)

        self._blk = True
        self.sink_scale.set_value(sink_vol)
        self.sink_pct.set_label(f'{sink_vol}%')
        self.src_scale.set_value(src_vol)
        self.src_pct.set_label(f'{src_vol}%')
        self._blk = False

        # ── MPRIS ──────────────────────────────────────────────────────────────
        if self._has_mpris:
            info = get_mpris_info()
            if info:
                self.mpris_title.set_label(info['title'])
                self.mpris_artist.set_label(info['artist'] or '—')
                if info['status'] != self._mpris_status:
                    self._mpris_status = info['status']
                    self.btn_play.set_label(
                        '󰏤' if info['status'] == 'playing' else '󰐊')
                cur_url = info.get('art_url', '')
                if cur_url != self.mpris_art._url:
                    self.mpris_art.load_url(cur_url)

        return True


if __name__ == '__main__':
    win = MediaPopup()
    win.connect('destroy', Gtk.main_quit)
    Gtk.main()
