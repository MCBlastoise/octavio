#!/bin/sh
set -e

# Setting up useful variables

SERVER_USERNAME="ayyub"
SERVER_HOSTNAME="octavio-server.mit.edu"

# Do separate installs (e.g. audio stuff) necessary

echo "Installing necessary packages"
sudo apt install autossh
# exit

# Establish device information

echo "What is the unique device number?"
read DEVICE_NUM
PORT=$(( $DEVICE_NUM + 2000 ))
echo "SSH tunnel port will be $PORT"

echo

# Create WIFI connections

MIT_NETWORK_NAME="A"
if nmcli connection show "$MIT_NETWORK_NAME" > /dev/null 2>&1; then
    echo "Connection $MIT_NETWORK_NAME already exists. Skipping connection."
else
    echo "Enter your password for the MIT network:"
    read MIT_PASSWORD
    echo "Creating the following connection:\n\tSSID: $MIT_NETWORK_NAME\n\tPassword: $MIT_PASSWORD"
    nmcli connection add type wifi con-name "$MIT_NETWORK_NAME" ssid "$MIT_NETWORK_NAME"
    nmcli connection modify "$MIT_NETWORK_NAME" wifi-sec.key-mgmt wpa-psk
    nmcli connection modify "$MIT_NETWORK_NAME" wifi-sec.psk "$MIT_PASSWORD"
    nmcli connection modify "$MIT_NETWORK_NAME" connection.autoconnect yes
    nmcli connection modify "$MIT_NETWORK_NAME" connection.autoconnect-priority 8
fi

echo

echo "Would you like to enter a mobile hotspot? If so, enter the SSID:"
read HOTSPOT_SSID
if [ -z "$HOTSPOT_SSID" ]; then
    echo "No hotspot provided. Skipping connection."
elif nmcli connection show "$HOTSPOT_SSID" > /dev/null 2>&1; then
    echo "Connection $HOTSPOT_SSID already exists. Skipping connection."
else
    echo "Enter your password for the mobile hotspot:"
    read HOTSPOT_PASSWORD
    echo "Creating the following connection:\n\tSSID: $HOTSPOT_SSID\n\tPassword: $HOTSPOT_PASSWORD"

    nmcli connection add type wifi con-name "$HOTSPOT_SSID" ssid "$HOTSPOT_SSID"
    nmcli connection modify "$HOTSPOT_SSID" wifi-sec.key-mgmt wpa-psk
    nmcli connection modify "$HOTSPOT_SSID" wifi-sec.psk "$HOTSPOT_PASSWORD"
    nmcli connection modify "$HOTSPOT_SSID" connection.autoconnect yes
    nmcli connection modify "$HOTSPOT_SSID" connection.autoconnect-priority 10
fi

echo

echo "Would you like to enter a home network? If so, enter the SSID:"
read HOME_SSID
if [ -z "$HOME_SSID" ]; then
    echo "No home network provided. Skipping connection."
elif nmcli connection show "$HOME_SSID" > /dev/null 2>&1; then
    echo "Connection $HOME_SSID already exists. Skipping connection."
else
    echo "Enter your password for the home network:"
    read HOME_PASSWORD
    echo "Creating the following connection:\n\tSSID: $HOME_SSID\n\tPassword: $HOME_PASSWORD"

    nmcli connection add type wifi con-name "$HOME_SSID" ssid "$HOME_SSID"
    nmcli connection modify "$HOME_SSID" wifi-sec.key-mgmt wpa-psk
    nmcli connection modify "$HOME_SSID" wifi-sec.psk "$HOME_PASSWORD"
    nmcli connection modify "$HOME_SSID" connection.autoconnect yes
    nmcli connection modify "$HOME_SSID" connection.autoconnect-priority 5
fi

echo

# Generate SSH keys on Pi and exchange with server

ssh-keygen -t ed25519 -C "\"Raspberry Pi $DEVICE_NUM\""
ssh-copy-id -i ~/.ssh/id_ed25519.pub $SERVER_USERNAME@$SERVER_HOSTNAME

# Setup tunnel-to-lab systemd service

# Make and populate venv environment

# Construct project-specific files

# Create (copy over) and activate client systemd service
