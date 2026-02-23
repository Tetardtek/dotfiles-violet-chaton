#!/usr/bin/env python3
# wob-overlay.py — Overlay volume/luminosité violet-chaton (remplace wob)
# Protocole FIFO : "v:N" = volume (rose), "b:N" = luminosité (cyan), "N" = volume

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, GtkLayerShell, GLib
import os
import threading

FIFO          = '/tmp/wob.fifo'
POPUP_WIDTH   = 280
POPUP_HEIGHT  = -1
MARGIN_BOTTOM = 48
HIDE_DELAY    = 1200  # ms

CSS = """
window {
    background: transparent;
}

#wob-box {
    background-color: rgba(38, 21, 55, 0.92);
    border: 2px solid rgba(92, 73, 108, 0.80);
    border-radius: 12px;
    padding: 10px 16px;
}

#wob-box.vol {
    border-color: rgba(255, 121, 198, 0.85);
}

#wob-box.bright {
    border-color: rgba(139, 233, 253, 0.85);
}

#wob-icon {
    font-family: "JetBrainsMono Nerd Font";
    font-size: 15px;
    min-width: 22px;
    margin-right: 4px;
}

#wob-pct {
    color: #f8f8f2;
    font-family: "JetBrainsMono Nerd Font";
    font-size: 11px;
    font-weight: bold;
    min-width: 36px;
    margin-left: 6px;
}

/* ── Volume (rose) ──────────────────────────────────────────── */

progressbar.vol trough {
    background-color: rgba(92, 73, 108, 0.45);
    border-radius: 5px;
    min-height: 7px;
    border: none;
}

progressbar.vol progress {
    background-color: #ff79c6;
    border-radius: 5px;
    border: none;
    min-height: 7px;
}

/* ── Luminosité (cyan) ──────────────────────────────────────── */

progressbar.bright trough {
    background-color: rgba(92, 73, 108, 0.45);
    border-radius: 5px;
    min-height: 7px;
    border: none;
}

progressbar.bright progress {
    background-color: #8be9fd;
    border-radius: 5px;
    border: none;
    min-height: 7px;
}
"""

VOL_ICONS   = ['󰕿', '󰖀', '󰕾']
BRIGHT_ICONS = ['󰃞', '󰃟', '󰃠']

def _icon(icons, pct):
    if pct <= 0:
        return icons[0]
    if pct < 50:
        return icons[1]
    return icons[2]


class WobOverlay(Gtk.Window):
    def __init__(self):
        super().__init__()
        self._hide_timer = None

        # ── Layer shell ──────────────────────────────────────────────────────
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.OVERLAY)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.BOTTOM, True)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.BOTTOM, MARGIN_BOTTOM)
        GtkLayerShell.set_exclusive_zone(self, -1)
        GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.NONE)

        self.set_decorated(False)
        self.set_resizable(False)
        self.set_app_paintable(True)
        self.set_default_size(POPUP_WIDTH, POPUP_HEIGHT)

        # Fenêtre transparente
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual:
            self.set_visual(visual)

        # ── CSS ──────────────────────────────────────────────────────────────
        provider = Gtk.CssProvider()
        provider.load_from_data(CSS.encode())
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # ── Layout ───────────────────────────────────────────────────────────
        outer = Gtk.Box()
        outer.set_name('wob-box')
        self._box = outer
        self.add(outer)

        self._icon_lbl = Gtk.Label()
        self._icon_lbl.set_name('wob-icon')
        outer.pack_start(self._icon_lbl, False, False, 0)

        self._bar = Gtk.ProgressBar()
        self._bar.set_hexpand(True)
        self._bar.set_valign(Gtk.Align.CENTER)
        outer.pack_start(self._bar, True, True, 0)

        self._pct_lbl = Gtk.Label()
        self._pct_lbl.set_name('wob-pct')
        self._pct_lbl.set_halign(Gtk.Align.END)
        outer.pack_end(self._pct_lbl, False, False, 0)

        self.show_all()
        self.hide()

    def show_value(self, val, kind='v'):
        """Appelé depuis le thread FIFO via GLib.idle_add."""
        val = max(0, min(100, val))
        fraction = val / 100.0

        # Icône + couleur selon le type
        if kind == 'b':
            icon = _icon(BRIGHT_ICONS, val)
            css_class = 'bright'
        else:
            icon = _icon(VOL_ICONS, val)
            css_class = 'vol'

        sc  = self._bar.get_style_context()
        bsc = self._box.get_style_context()
        for c in ['vol', 'bright']:
            sc.remove_class(c)
            bsc.remove_class(c)
        sc.add_class(css_class)
        bsc.add_class(css_class)

        self._icon_lbl.set_label(icon)
        self._icon_lbl.set_markup(
            f'<span foreground="{"#8be9fd" if kind == "b" else "#ff79c6"}">{icon}</span>'
        )
        self._bar.set_fraction(fraction)
        self._pct_lbl.set_label(f'{val}%')

        self.show()

        # Reset timer
        if self._hide_timer:
            GLib.source_remove(self._hide_timer)
        self._hide_timer = GLib.timeout_add(HIDE_DELAY, self._do_hide)

    def _do_hide(self):
        self.hide()
        self._hide_timer = None
        return False


def _fifo_reader(overlay):
    """Thread : lit le FIFO en boucle et schedule les mises à jour UI."""
    while True:
        try:
            if not os.path.exists(FIFO):
                os.mkfifo(FIFO)
            # O_RDWR : ne bloque pas à l'ouverture ET garde le FIFO ouvert
            # entre deux écritures (pas d'EOF même sans writer actif)
            fd = os.open(FIFO, os.O_RDWR)
            with os.fdopen(fd, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    # Protocole : "v:N", "b:N" ou plain "N"
                    if ':' in line:
                        kind, _, raw = line.partition(':')
                    else:
                        kind, raw = 'v', line
                    try:
                        val = int(raw)
                        GLib.idle_add(overlay.show_value, val, kind)
                    except ValueError:
                        pass
        except OSError:
            import time
            time.sleep(0.5)


if __name__ == '__main__':
    win = WobOverlay()
    win.connect('destroy', Gtk.main_quit)

    t = threading.Thread(target=_fifo_reader, args=(win,), daemon=True)
    t.start()

    Gtk.main()
