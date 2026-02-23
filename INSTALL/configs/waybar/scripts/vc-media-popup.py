#!/usr/bin/env python3
# vc-media-popup.py — Popup audio + luminosité violet-chaton
# Lancé depuis le clic sur wireplumber OU backlight

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, GtkLayerShell, GLib
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
"""

POPUP_WIDTH = 310

# ── Helpers ───────────────────────────────────────────────────────────────────

def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=2, **kw)

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

def vol_icon(muted):
    return '󰖁' if muted else '󰕾'

def mic_icon(muted):
    return '󰍭' if muted else '󰍬'

def bright_icon(pct):
    if pct < 34: return '󰃞'
    if pct < 67: return '󰃟'
    return '󰃠'

# ── Popup ─────────────────────────────────────────────────────────────────────

class MediaPopup(Gtk.Window):
    def __init__(self):
        super().__init__()
        self._blk = False

        # ── Position ─────────────────────────────────────────────────────────
        display = Gdk.Display.get_default()
        monitor = display.get_primary_monitor() if display else None
        screen_w = monitor.get_geometry().width if monitor else 1920
        module_center = screen_w - 16 - 210
        margin_left = max(0, module_center - POPUP_WIDTH // 2)

        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.OVERLAY)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.LEFT, True)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.TOP, 66)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.LEFT, margin_left)
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

        # ╔═══ SORTIE ══════════════════════════════════════════════════════════╗
        box.pack_start(self._section_header('SORTIE', '󰕾'), False, False, 0)
        box.pack_start(self._device_label(
            get_node_name('@DEFAULT_AUDIO_SINK@')), False, False, 2)
        sink_row, self.sink_scale, self.sink_pct, self.sink_icon = \
            self._slider_row(sink_vol, sink_muted, 'audio', vol_icon(sink_muted),
                             self._toggle_sink_mute, '@DEFAULT_AUDIO_SINK@')
        box.pack_start(sink_row, False, False, 4)

        # ╔═══ ENTRÉE ══════════════════════════════════════════════════════════╗
        sep1 = Gtk.Label(label='─' * 34)
        sep1.set_name('separator')
        box.pack_start(sep1, False, False, 0)

        box.pack_start(self._section_header('ENTRÉE', '󰍬'), False, False, 0)
        box.pack_start(self._device_label(
            get_node_name('@DEFAULT_AUDIO_SOURCE@')), False, False, 2)
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
        # Forcer un re-calcul après que les widgets sont visibles
        GLib.idle_add(self._redraw_scales)
        self.grab_focus()

    def _redraw_scales(self):
        """Force GTK3 à recalculer les highlights.
        set_value(même_valeur) est un no-op — on oscille ±1 pour déclencher
        un vrai recalcul de la position du highlight dans le trough."""
        self._blk = True
        for scale in [self.sink_scale, self.src_scale, self.bright_scale]:
            v   = scale.get_value()
            adj = scale.get_adjustment()
            lo  = adj.get_lower()
            scale.set_value(max(lo, v - 1))  # valeur différente → GTK recalcule
            scale.set_value(v)               # retour à la valeur réelle
        self._blk = False
        return False

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

        # Icône = bouton mute
        icon_btn = Gtk.Button(label=icon_char)
        icon_btn.set_name('mute-icon' if target == '@DEFAULT_AUDIO_SINK@' else 'mic-icon')
        if muted:
            icon_btn.get_style_context().add_class('muted')
        icon_btn.connect('clicked', mute_cb)
        row.pack_start(icon_btn, False, False, 0)

        # Slider
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

        # %
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

    def _refresh(self):
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

        return True


if __name__ == '__main__':
    win = MediaPopup()
    win.connect('destroy', Gtk.main_quit)
    Gtk.main()
