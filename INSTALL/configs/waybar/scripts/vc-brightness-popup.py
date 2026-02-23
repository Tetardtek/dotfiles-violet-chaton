#!/usr/bin/env python3
# vc-brightness-popup.py — Popup luminosité violet-chaton
# Lancé par le clic sur le module backlight de waybar

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, GtkLayerShell, GLib
import subprocess
import os
import re

# ── CSS ───────────────────────────────────────────────────────────────────────

CSS = b"""
window {
    background-color: rgba(52, 28, 74, 0.93);
    border: 3px solid rgba(255, 121, 198, 0.78);
    border-radius: 14px;
}

#container {
    padding: 14px 20px 16px 20px;
}

#bright-icon {
    color: #8be9fd;
    font-family: "JetBrainsMono Nerd Font";
    font-size: 18px;
    min-width: 24px;
}

#bright-title {
    color: rgba(248, 248, 242, 0.55);
    font-family: "JetBrainsMono Nerd Font";
    font-size: 11px;
}

#device-name {
    color: #8be9fd;
    font-family: "JetBrainsMono Nerd Font";
    font-size: 11px;
    font-weight: bold;
}

#bright-pct {
    color: #f8f8f2;
    font-family: "JetBrainsMono Nerd Font";
    font-size: 13px;
    font-weight: bold;
    min-width: 44px;
}

#separator {
    color: rgba(92, 73, 108, 0.60);
    margin: 4px 0;
}

scale trough {
    background-color: rgba(92, 73, 108, 0.55);
    border-radius: 3px;
    min-height: 6px;
    border: none;
}

scale highlight {
    background-color: #8be9fd;
    border-radius: 3px;
    border: none;
}

scale slider {
    background-color: #f8f8f2;
    border-radius: 50%;
    min-width: 18px;
    min-height: 18px;
    border: 2px solid rgba(139, 233, 253, 0.80);
    box-shadow: none;
    transition: none;
}

scale slider:hover {
    background-color: #8be9fd;
    border-color: #8be9fd;
}
"""

POPUP_WIDTH = 300

# ── Brightness helpers ────────────────────────────────────────────────────────

def get_brightness():
    """Retourne (valeur 0-100, nom du device)."""
    try:
        r = subprocess.run(
            ['brightnessctl', 'info'],
            capture_output=True, text=True, timeout=2
        )
        pct_match = re.search(r'\((\d+)%\)', r.stdout)
        dev_match = re.search(r"Device '([^']+)'", r.stdout)
        pct = int(pct_match.group(1)) if pct_match else 50
        dev = dev_match.group(1) if dev_match else 'Écran'
        # Rendre le nom plus lisible
        dev = dev.replace('_', ' ').replace('backlight', '').strip().title()
        return pct, dev
    except Exception:
        return 50, 'Écran'

def set_brightness(pct):
    pct = max(1, min(100, pct))  # minimum 1% pour ne pas éteindre l'écran
    subprocess.run(
        ['brightnessctl', 'set', f'{pct}%', '-q'],
        capture_output=True
    )
    # Feedback wob
    fifo = '/tmp/wob.fifo'
    if os.path.exists(fifo):
        try:
            fd = os.open(fifo, os.O_WRONLY | os.O_NONBLOCK)
            os.write(fd, f'{pct}\n'.encode())
            os.close(fd)
        except OSError:
            pass

def bright_icon(pct):
    if pct < 34:
        return '󰃞'
    if pct < 67:
        return '󰃟'
    return '󰃠'

# ── Popup ─────────────────────────────────────────────────────────────────────

class BrightnessPopup(Gtk.Window):
    def __init__(self):
        super().__init__()
        self._blocked = False

        # ── Position : centré sous le module backlight ────────────────────────
        display = Gdk.Display.get_default()
        monitor = display.get_primary_monitor() if display else None
        screen_w = monitor.get_geometry().width if monitor else 1920

        # Backlight est le 2e module de la pill droite (~250px depuis le bord)
        module_center = screen_w - 16 - 250
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
        provider.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # ── État initial ──────────────────────────────────────────────────────
        pct, dev = get_brightness()

        # ── Layout ────────────────────────────────────────────────────────────
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        container.set_name('container')
        self.add(container)

        # Ligne device
        dev_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        dev_icon = Gtk.Label(label='󰍹')
        dev_icon.set_name('bright-title')
        dev_row.pack_start(dev_icon, False, False, 0)
        dev_label = Gtk.Label(label=dev)
        dev_label.set_name('device-name')
        dev_label.set_halign(Gtk.Align.START)
        dev_label.set_ellipsize(3)
        dev_row.pack_start(dev_label, True, True, 0)
        container.pack_start(dev_row, False, False, 0)

        # Séparateur
        sep = Gtk.Label(label='─' * 30)
        sep.set_name('separator')
        container.pack_start(sep, False, False, 4)

        # En-tête : icône + "Luminosité" + %
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.icon = Gtk.Label(label=bright_icon(pct))
        self.icon.set_name('bright-icon')
        header.pack_start(self.icon, False, False, 0)

        title = Gtk.Label(label='Luminosité')
        title.set_name('bright-title')
        title.set_halign(Gtk.Align.START)
        header.pack_start(title, True, True, 0)

        self.pct = Gtk.Label(label=f'{pct}%')
        self.pct.set_name('bright-pct')
        self.pct.set_halign(Gtk.Align.END)
        header.pack_end(self.pct, False, False, 0)
        container.pack_start(header, False, False, 0)

        # Slider (min 1% pour ne pas éteindre l'écran)
        self.scale = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL, 1, 100, 5
        )
        self.scale.set_value(pct)
        self.scale.set_draw_value(False)
        self.scale.set_hexpand(True)
        self.scale.connect('value-changed', self._on_changed)
        container.pack_start(self.scale, False, False, 0)

        # ── Fermeture ─────────────────────────────────────────────────────────
        self.connect('key-press-event', self._on_key)
        self.connect('focus-out-event', lambda *_: self.destroy())

        self.show_all()
        self.grab_focus()

    def _on_changed(self, scale):
        if self._blocked:
            return
        pct = int(scale.get_value())
        self.pct.set_label(f'{pct}%')
        self.icon.set_label(bright_icon(pct))
        set_brightness(pct)

    def _on_key(self, _widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.destroy()


if __name__ == '__main__':
    win = BrightnessPopup()
    win.connect('destroy', Gtk.main_quit)
    Gtk.main()
