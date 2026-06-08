#!/bin/bash

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

echo -e "${GREEN}=======================================${NC}"
echo -e "${GREEN}    Custom SlowDNS Server Installer    ${NC}"
echo -e "${GREEN}=======================================${NC}"

# Check Root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}Error: Please run as root user!${NC}"
  exit 1
fi

# 1. User Input for Domain & NS
echo -e "${YELLOW}[*] Configuration Details:${NC}"
read -p "Enter your Nameserver (NS) Domain (e.g., ns.yourdomain.com): " NS_DOMAIN
if [ -z "$NS_DOMAIN" ]; then
    echo -e "${RED}Domain cannot be empty!${NC}"
    exit 1
fi

# 2. Update and Install Dependencies
echo -e "${YELLOW}[*] Updating system and installing dependencies...${NC}"
apt-get update -y
apt-get install -y git golang curl iptables tmux openbox

# 3. Clone and Build DNSTT
echo -e "${YELLOW}[*] Downloading and building DNSTT Core...${NC}"
cd /usr/local/src
rm -rf dnstt
git clone https://www.bamsoftware.com/git/dnstt.git
cd dnstt/dnstt-server
go build

# Copy binary to global path
cp dnstt-server /usr/local/bin/dnstt-server
chmod +x /usr/local/bin/dnstt-server

# 4. Generate Crypto Keys (New Version Syntax)
echo -e "${YELLOW}[*] Generating DNSTT Crypto Keys...${NC}"
cd /usr/local/bin
rm -f server.key server.pub
dnstt-server -gen-key -privkey-file server.key -pubkey-file server.pub

PUB_KEY=$(cat server.pub)

# 5. Configure Firewall (IPTables Forwarding)
echo -e "${YELLOW}[*] Configuring Firewall & Port Forwarding...${NC}"
iptables -I INPUT -p udp --dport 53 -j ACCEPT
iptables -t nat -I PREROUTING -i eth0 -p udp --dport 53 -j REDIRECT --to-ports 8530
ip6tables -I INPUT -p udp --dport 53 -j ACCEPT 2>/dev/null
ip6tables -t nat -I PREROUTING -i eth0 -p udp --dport 53 -j REDIRECT --to-ports 8530 2>/dev/null

# Save IPTables Rules
apt-get install iptables-persistent -y
netfilter-persistent save

# 6. Create Systemd Service for Auto-Run (New Version Syntax)
echo -e "${YELLOW}[*] Creating Systemd Background Service...${NC}"
cat <<EOF > /etc/systemd/system/dnstt.service
[Unit]
Description=Custom SlowDNS DNSTT Server Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/usr/local/bin
ExecStart=/usr/local/bin/dnstt-server -udp :8530 -privkey-file server.key \$NS_DOMAIN 127.0.0.1:22
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Reload and Start Service
systemctl daemon-reload
systemctl enable dnstt
systemctl restart dnstt

# 7. Installation Summary
echo -e "${GREEN}=======================================${NC}"
echo -e "${GREEN}     SlowDNS Installation Completed!    ${NC}"
echo -e "${GREEN}=======================================${NC}"
echo -e "${YELLOW}Your NS Domain:${NC} $NS_DOMAIN"
echo -e "${YELLOW}Your Public Key:${NC} $PUB_KEY"
echo -e "${YELLOW}SSH Target Port:${NC} 22 (Default Local SSH)"
echo -e "${GREEN}=======================================${NC}"
echo -e "You can now use this Public Key and NS Domain in your tunnel clients."

