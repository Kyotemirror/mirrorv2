#!/bin/bash

# =========================
# Configuration
# =========================
APP_NAME="Kyote Smart Mirror V1.01"
APP_DIR="/home/pi/mirror"

SERVICE_NAME="smart-mirror.service"
SERVICE_PATH="/etc/systemd/system/$SERVICE_NAME"

WPA_CONF="/etc/wpa_supplicant/wpa_supplicant.conf"
IFACE="wlan0"

BOOT_THEME_NAME="kyote"
PLYMOUTH_THEME_DIR="/usr/share/plymouth/themes/$BOOT_THEME_NAME"
BOOT_BG_SRC="$APP_DIR/assets/boot_background.png"
BOOT_LOGO_SRC="$APP_DIR/assets/logo.png"

# =========================
# Root check
# =========================
if [[ $EUID -ne 0 ]]; then
  exec sudo "$0" "$@"
fi

# =========================
# Welcome
# =========================
whiptail --title "$APP_NAME Setup" \
--msgbox "Welcome to the $APP_NAME setup wizard.\n\nThis will guide you through Wi‑Fi setup, auto‑start, and fast branded boot." 12 70

# =========================
# Wi‑Fi Setup (Scan List)
# =========================
if whiptail --title "$APP_NAME Setup" \
--yesno "Do you want to connect to Wi‑Fi now?" 10 60; then

  ip link set "$IFACE" up

  SSIDS=$(iw dev "$IFACE" scan 2>/dev/null | grep "SSID:" | sed 's/SSID: //' | grep -v '^$' | sort -u)

  if [[ -z "$SSIDS" ]]; then
    whiptail --msgbox "❌ No Wi‑Fi networks found.\n\nTry again later." 10 60
    exit 1
  fi

  MENU_ITEMS=()
  while read -r ssid; do
    MENU_ITEMS+=("$ssid" "")
  done <<< "$SSIDS"

  SELECTED_SSID=$(whiptail --title "Select Wi‑Fi Network" \
    --menu "Choose a Wi‑Fi network:" 20 70 12 \
    "${MENU_ITEMS[@]}" \
    3>&1 1>&2 2>&3)

  [[ -z "$SELECTED_SSID" ]] && exit 1

  WIFI_PASS=$(whiptail --title "Wi‑Fi Password" \
    --passwordbox "Enter password for \"$SELECTED_SSID\":" 10 70 \
    3>&1 1>&2 2>&3)

  [[ -z "$WIFI_PASS" ]] && exit 1

  cp "$WPA_CONF" "$WPA_CONF.bak.$(date +%s)"
  wpa_passphrase "$SELECTED_SSID" "$WIFI_PASS" >> "$WPA_CONF"
  wpa_cli -i "$IFACE" reconfigure >/dev/null 2>&1

  whiptail --msgbox "✅ Wi‑Fi configured successfully." 10 60
fi

# =========================
# Autostart Setup
# =========================
if whiptail --title "$APP_NAME Setup" \
--yesno "Enable Smart Mirror to start automatically on boot?" 10 60; then

  cat > "$SERVICE_PATH" <<EOF
[Unit]
Description=Smart Mirror Pygame App
After=network.target graphical.target
Wants=network-online.target

[Service]
Type=simple
User=pi
WorkingDirectory=$APP_DIR
ExecStart=/usr/bin/python3 $APP_DIR/app.py
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/pi/.Xauthority
Restart=always
RestartSec=5
KillSignal=SIGINT
TimeoutStopSec=10

[Install]
WantedBy=graphical.target
EOF

  systemctl daemon-reexec
  systemctl daemon-reload
  systemctl enable "$SERVICE_NAME"

  whiptail --msgbox "✅ Auto‑start enabled." 10 60
fi

# =========================
# Fast Branded Boot
# =========================
if whiptail --title "$APP_NAME Setup" \
--yesno "Enable fast branded boot?\n\nThis hides Linux text and shows your logo immediately on power‑on." 12 70; then

  apt-get update
  apt-get install -y plymouth plymouth-themes

  sed -i 's/console=tty1//g' /boot/cmdline.txt
  grep -q "quiet splash" /boot/cmdline.txt || \
    sed -i 's/$/ quiet splash loglevel=0 vt.global_cursor_default=0/' /boot/cmdline.txt

  mkdir -p "$PLYMOUTH_THEME_DIR"

  cp "$BOOT_BG_SRC" "$PLYMOUTH_THEME_DIR/background.png"
  cp "$BOOT_LOGO_SRC" "$PLYMOUTH_THEME_DIR/logo.png"

  cat > "$PLYMOUTH_THEME_DIR/$BOOT_THEME_NAME.plymouth" <<EOF
[Plymouth Theme]
Name=Kyote Smart Mirror
Description=Fast branded boot
ModuleName=script
EOF

  cat > "$PLYMOUTH_THEME_DIR/$BOOT_THEME_NAME.script" <<'EOF'
background = Image("background.png");
logo = Image("logo.png");

screen_width = Window.GetWidth();
screen_height = Window.GetHeight();

bg = Sprite();
bg.SetImage(background);
bg.SetPosition(0, 0);

logo_sprite = Sprite();
logo_sprite.SetImage(logo);
logo_sprite.SetPosition(
  (screen_width - logo.GetWidth()) / 2,
  (screen_height - logo.GetHeight()) / 2
);
EOF

  plymouth-set-default-theme "$BOOT_THEME_NAME" -R

  whiptail --msgbox "✅ Fast branded boot enabled.\n\nYour logo will appear immediately on power‑on." 10 70
fi

# =========================
# Done
# =========================
whiptail --title "$APP_NAME Setup" \
--msgbox "🎉 Setup complete!\n\nReboot the device to experience the full fast‑boot mirror." 12 60
