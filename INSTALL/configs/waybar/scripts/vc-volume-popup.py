#!/usr/bin/env python3
# vc-volume-popup.py — Popup volume slider violet-chaton
# Lancé par le clic sur le module wireplumber de waybar

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

#vol-icon {
    color: #ff79c6;
    font-family: "JetBrainsMono Nerd Font";
    font-size: 18px;
    min-width: 24px;
}

#vol-title {
    color: rgba(248, 248, 242, 0.55);
    font-family: "JetBrainsMono Nerd Font";
    font-size: 11px;
}

#sink-name {
    color: #8be9fd;
    font-family: "JetBrainsMono Nerd Font";
    font-size: 11px;
    font-weight: bold;
}

#vol-pct {
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
    background-color: #ff79c6;
    border-radius: 3px;
    border: none;
}

scale slider {
    background-color: #f8f8f2;
    border-radius: 50%;
    min-width: 18px;
    min-height: 18px;
    border: 2px solid rgba(255, 121, 198, 0.80);
    box-shadow: none;
    transition: none;
}

scale slider:hover {
    background-color: #e79cfe;
    border-color: #ff79c6;
}

#mute-btn {
    background: rgba(73, 49, 97, 0.50);
    border: 1px solid rgba(92, 73, 108, 0.60);
    border-radius: 8px;
    color: rgba(248, 248, 242, 0.65);
    font-family: "JetBrainsMono Nerd Font";
    font-size: 12px;
    padding: 5px 16px;
    margin-top: 6px;
}

#mute-btn:hover {
    background: rgba(255, 121, 198, 0.18);
    border-color: rgba(255, 121, 198, 0.45);
    color: #ff79c6;
}

#mute-btn.muted {
    color: #f38ba8;
    border-color: rgba(243, 139, 168, 0.45);
    background: rgba(243, 139, 168, 0.10);
}

#mic-btn {
    background: rgba(73, 49, 97, 0.50);
    border: 1px solid rgba(139, 233, 253, 0.35);
    border-radius: 8px;
    color: #8be9fd;
    font-family: "JetBrainsMono Nerd Font";
    font-size: 12px;
    padding: 5px 16px;
    margin-top: 4px;
}

#mic-btn:hover {
    background: rgba(139, 233, 253, 0.12);
    border-color: rgba(139, 233, 253, 0.60);
    color: #8be9fd;
}

#mic-btn.muted {
    color: #f38ba8;
    border-color: rgba(243, 139, 168, 0.45);
    background: rgba(243, 139, 168, 0.10);
}
"""

POPUP_WIDTH = 300

# ── Audio helpers ─────────────────────────────────────────────────────────────

def get_volume():
    """Retourne (volume 0-100, is_muted)"""
    try:
        r = subprocess.run(
            ['wpctl', 'get-volume', '@DEFAULT_AUDIO_SINK@'],
            capture_output=True, text=True, timeout=2
        )
        parts = r.stdout.strip().split()
        vol = int(float(parts[1]) * 100)
        muted = '[MUTED]' in r.stdout
        return min(max(vol, 0), 100), muted
    except Exception:
        return 50, False

def get_sink_name():
    """Retourne le nom humain de la sortie audio active."""
    try:
        r = subprocess.run(
            ['wpctl', 'inspect', '@DEFAULT_AUDIO_SINK@'],
            capture_output=True, text=True, timeout=2
        )
        # Chercher node.description en priorité, sinon node.nick
        for field in ('node.description', 'node.nick'):
            m = re.search(rf'{field}\s*=\s*"([^"]+)"', r.stdout)
            if m:
                return m.group(1)
    except Exception:
        pass
    return 'Sortie audio'

def set_volume(vol):
    subprocess.run(
        ['wpctl', 'set-volume', '-l', '1.0', '@DEFAULT_AUDIO_SINK@', f'{vol}%'],
        capture_output=True
    )
    # Feedback wob (non-bloquant)
    fifo = '/tmp/wob.fifo'
    if os.path.exists(fifo):
        try:
            fd = os.open(fifo, os.O_WRONLY | os.O_NONBLOCK)
            os.write(fd, f'{vol}\n'.encode())
            os.close(fd)
        except OSError:
            pass

def toggle_mute():
    subprocess.run(
        ['wpctl', 'set-mute', '@DEFAULT_AUDIO_SINK@', 'toggle'],
        capture_output=True
    )

def get_mic_muted():
    """Retourne True si le micro actif est muté."""
    try:
        r = subprocess.run(
            ['wpctl', 'get-volume', '@DEFAULT_AUDIO_SOURCE@'],
            capture_output=True, text=True, timeout=2
        )
        return '[MUTED]' in r.stdout
    except Exception:
        return False

def toggle_mic_mute():
    subprocess.run(
        ['wpctl', 'set-mute', '@DEFAULT_AUDIO_SOURCE@', 'toggle'],
        capture_output=True
    )

def vol_icon(vol, muted):
    if muted or vol == 0:
        return '󰝟'
    if vol < 50:
        return '󰕿'
    return '󰕾'

# ── Popup ─────────────────────────────────────────────────────────────────────

class VolumePopup(Gtk.Window):
    def __init__(self):
        super().__init__()
        self._blocked = False

        # ── Position : centré sous le module wireplumber ──────────────────────
        # Wireplumber = 1er module de la pill droite (côté droit de l'écran).
        # On centre le popup horizontalement sous ce module.
        display = Gdk.Display.get_default()
        monitor = display.get_primary_monitor() if display else None
        if monitor:
            screen_w = monitor.get_geometry().width
        else:
            screen_w = 1920  # fallback

        # La pill droite a ~16px de marge depuis le bord droit.
        # Le module wireplumber est le 1er élément : ~180px depuis le bord droit.
        module_center = screen_w - 16 - 180
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
        vol, muted = get_volume()
        self._muted = muted
        self._mic_muted = get_mic_muted()
        sink = get_sink_name()

        # ── Layout ────────────────────────────────────────────────────────────
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        container.set_name('container')
        self.add(container)

        # Ligne sink (sortie active)
        sink_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        sink_icon = Gtk.Label(label='󰓃')
        sink_icon.set_name('vol-title')
        sink_row.pack_start(sink_icon, False, False, 0)
        self.sink_label = Gtk.Label(label=sink)
        self.sink_label.set_name('sink-name')
        self.sink_label.set_halign(Gtk.Align.START)
        self.sink_label.set_ellipsize(3)  # PANGO_ELLIPSIZE_END
        sink_row.pack_start(self.sink_label, True, True, 0)
        container.pack_start(sink_row, False, False, 0)

        # Séparateur
        sep = Gtk.Label(label='─' * 30)
        sep.set_name('separator')
        container.pack_start(sep, False, False, 4)

        # En-tête volume : icône + "Volume" + %
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.icon = Gtk.Label(label=vol_icon(vol, muted))
        self.icon.set_name('vol-icon')
        header.pack_start(self.icon, False, False, 0)

        title = Gtk.Label(label='Volume')
        title.set_name('vol-title')
        title.set_halign(Gtk.Align.START)
        header.pack_start(title, True, True, 0)

        self.pct = Gtk.Label(label=f'{vol}%')
        self.pct.set_name('vol-pct')
        self.pct.set_halign(Gtk.Align.END)
        header.pack_end(self.pct, False, False, 0)
        container.pack_start(header, False, False, 0)

        # Slider
        self.scale = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL, 0, 100, 5
        )
        self.scale.set_value(vol)
        self.scale.set_draw_value(False)
        self.scale.set_hexpand(True)
        self.scale.connect('value-changed', self._on_changed)
        container.pack_start(self.scale, False, False, 0)

        # Bouton mute
        self.mute_btn = Gtk.Button(label=f'󰖁  {"Remettre le son" if muted else "Muet"}')
        self.mute_btn.set_name('mute-btn')
        self.mute_btn.set_halign(Gtk.Align.CENTER)
        if muted:
            self.mute_btn.get_style_context().add_class('muted')
        self.mute_btn.connect('clicked', self._on_mute)
        container.pack_start(self.mute_btn, False, False, 0)

        # ── Section micro ─────────────────────────────────────────────────────
        sep2 = Gtk.Label(label='─' * 30)
        sep2.set_name('separator')
        container.pack_start(sep2, False, False, 4)

        mic_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        mic_icon = Gtk.Label(label='󰍬')
        mic_icon.set_name('vol-title')
        mic_icon.set_markup('<span font_family="JetBrainsMono Nerd Font" size="large">󰍬</span>')
        mic_row.pack_start(mic_icon, False, False, 0)

        mic_title = Gtk.Label(label='Micro')
        mic_title.set_name('vol-title')
        mic_title.set_halign(Gtk.Align.START)
        mic_row.pack_start(mic_title, True, True, 0)

        mic_label = '󰍭  Coupé' if self._mic_muted else '󰍬  Actif'
        self.mic_btn = Gtk.Button(label=mic_label)
        self.mic_btn.set_name('mic-btn')
        if self._mic_muted:
            self.mic_btn.get_style_context().add_class('muted')
        self.mic_btn.connect('clicked', self._on_mic_mute)
        mic_row.pack_end(self.mic_btn, False, False, 0)

        container.pack_start(mic_row, False, False, 0)

        # ── Refresh périodique (détecte changement de sink/micro) ─────────────
        GLib.timeout_add(2000, self._refresh_sink)

        # ── Fermeture ─────────────────────────────────────────────────────────
        self.connect('key-press-event', self._on_key)
        self.connect('focus-out-event', lambda *_: self.destroy())

        self.show_all()
        self.grab_focus()

    def _on_changed(self, scale):
        if self._blocked:
            return
        vol = int(scale.get_value())
        self.pct.set_label(f'{vol}%')
        self.icon.set_label(vol_icon(vol, self._muted))
        set_volume(vol)

    def _on_mute(self, btn):
        toggle_mute()
        _, self._muted = get_volume()
        vol = int(self.scale.get_value())
        self.icon.set_label(vol_icon(vol, self._muted))
        if self._muted:
            btn.get_style_context().add_class('muted')
            btn.set_label('󰕿  Remettre le son')
        else:
            btn.get_style_context().remove_class('muted')
            btn.set_label('󰖁  Muet')

    def _refresh_sink(self):
        """Met à jour la sortie et l'état du micro si changement détecté."""
        # Sortie audio
        sink = get_sink_name()
        if self.sink_label.get_label() != sink:
            self.sink_label.set_label(sink)
            vol, muted = get_volume()
            self._blocked = True
            self.scale.set_value(vol)
            self._blocked = False
            self.pct.set_label(f'{vol}%')
            self._muted = muted
            self.icon.set_label(vol_icon(vol, muted))

        # Micro
        mic_muted = get_mic_muted()
        if mic_muted != self._mic_muted:
            self._mic_muted = mic_muted
            if mic_muted:
                self.mic_btn.get_style_context().add_class('muted')
                self.mic_btn.set_label('󰍭  Coupé')
            else:
                self.mic_btn.get_style_context().remove_class('muted')
                self.mic_btn.set_label('󰍬  Actif')

        return True  # continuer le timer

    def _on_mic_mute(self, btn):
        toggle_mic_mute()
        self._mic_muted = get_mic_muted()
        if self._mic_muted:
            btn.get_style_context().add_class('muted')
            btn.set_label('󰍭  Coupé')
        else:
            btn.get_style_context().remove_class('muted')
            btn.set_label('󰍬  Actif')

    def _on_key(self, _widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.destroy()


if __name__ == '__main__':
    win = VolumePopup()
    win.connect('destroy', Gtk.main_quit)
    Gtk.main()
