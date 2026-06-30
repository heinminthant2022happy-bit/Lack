#!/bin/bash

# Ensure root access
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root user!"
  exit 1
fi

# Automatically install core dependency for speed capping
if ! command -v wondershaper &> /dev/null; then
    apt-get update -y && apt-get install -y wondershaper iptables-persistent
fi

# Text Database Setup
DB_USERS="/etc/slowdns_users.db"
touch $DB_USERS

# UI Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Get Primary Network Interface for Traffic Control
NET_INT=$(ip route get 8.8.8.8 | awk '{print $5; exit}')

clear

# --------------------------------------------------------------------
# 1. CREATE ACCOUNT (FREE & VIP FLEXIBLE)
# --------------------------------------------------------------------
create_account() {
    echo -e "${CYAN}--- Create New Tunnel Account ---${NC}"
    read -p "Enter Username: " username
    [ -z "$username" ] && { echo -e "${RED}Username cannot be empty!${NC}"; return; }
    if id "$username" &>/dev/null; then echo -e "${RED}User '$username' already exists!${NC}"; return; fi
    
    read -p "Enter Password: " password
    read -p "Enter Duration Days (e.g., 30): " days
    read -p "Enter Bandwidth Limit in GB (0 for Unlimited): " gb_limit
    read -p "Enter Speed Limit in Mbps (0 for Unlimited): " speed_limit

    # Calculate date
    exp_date=$(date -d "+$days days" +%Y-%m-%d)
    
    # Secure system user creation without bash login access
    useradd -e "$exp_date" -M -s /bin/false "$username"
    echo "$username:$password" | chpasswd

    # Save to Local DB: username|password|exp_date|gb_limit|speed_limit
    echo "$username|$password|$exp_date|$gb_limit|$speed_limit" >> $DB_USERS

    # Register Firewall Traffic Accounting Rules for this user
    iptables -I INPUT -p tcp --dport 22 -m comment --comment "vpngb_$username" -j ACCEPT
    iptables -I OUTPUT -p tcp --sport 22 -m comment --comment "vpngb_$username" -j ACCEPT
    netfilter-persistent save &>/dev/null

    # Show Output Info Share Format
    clear
    echo -e "${GREEN}=======================================${NC}"
    echo -e "${GREEN}      ACCOUNT CREATED SUCCESSFULLY!    ${NC}"
    echo -e "${GREEN}=======================================${NC}"
    echo -e "${YELLOW}Copy and Send this to your Client:${NC}"
    echo -e "---------------------------------------"
    echo -e "➔ USERNAME     : $username"
    echo -e "➔ PASSWORD     : $password"
    echo -e "➔ EXPIRED DATE : $exp_date ($days Days)"
    if [ "$gb_limit" -eq 0 ]; then
        echo -e "➔ DATA QUOTA   : Unlimited GB"
    else
        echo -e "➔ DATA QUOTA   : $gb_limit GB"
    fi
    if [ "$speed_limit" -eq 0 ]; then
        echo -e "➔ SPEED LIMIT  : Max Server Speed"
    else
        echo -e "➔ SPEED LIMIT  : $speed_limit Mbps"
    fi
    echo -e "---------------------------------------"
    echo -e "➔ NAMESERVER   : nsgood.shiplay.my.id"
    echo -e "${GREEN}=======================================${NC}"
}

# --------------------------------------------------------------------
# 2. ACCOUNT TRAFFIC & STATUS MONITOR (FIXED UI BUG)
# --------------------------------------------------------------------
monitor_accounts() {
    echo -e "${YELLOW}=======================================================================${NC}"
    echo -e "                      TUNNEL ACCOUNTS LIVE MONITOR                     "
    echo -e "${YELLOW}=======================================================================${NC}"
    printf "%-15s | %-12s | %-15s | %-12s\n" "Username" "Status" "Bandwidth Used" "Speed Cap"
    echo -e "-----------------------------------------------------------------------"

    if [ ! -s $DB_USERS ]; then
        echo -e "                      No accounts found in Database.                   "
    else
        while IFS='|' read -r user pass exp gb speed; do
            [ -z "$user" ] && continue
            
            # Check Active Online Count
            online_count=$(ps aux | grep sshd | grep "$user" | grep -v grep | wc -l)
            if [ "$online_count" -gt 0 ]; then
                online_status="$online_count Active"
                status_color=$GREEN
            else
                online_status="Offline"
                status_color=$RED
            fi

            # Extract Traffic
            bytes=$(iptables -L -n -v -x | grep "vpngb_$user" | awk '{sum+=$2} END {print sum}')
            [ -z "$bytes" ] && bytes=0
            usage=$(awk "BEGIN {printf \"%.2f GB\", $bytes/1073741824}")

            sp_text="${speed} Mbps"
            [ "$speed" -eq 0 ] && sp_text="Max Speed"
            [ "$gb" -gt 0 ] && usage="$usage / ${gb}GB"

            # Formatted Output using standard dynamic colors inside printf
            printf "%-15s | %b%-12s%b | %-15s | %-12s\n" "$user" "$status_color" "$online_status" "$NC" "$usage" "$sp_text"
        done < $DB_USERS
    fi
    echo -e "-----------------------------------------------------------------------"
}

# --------------------------------------------------------------------
# 3. DELETE / PURGE ACCOUNT
# --------------------------------------------------------------------
delete_account() {
    echo -e "${RED}--- Delete Tunnel Account ---${NC}"
    read -p "Enter username to delete: " username
    if [ -z "$username" ]; then return; fi

    if id "$username" &>/dev/null; then
        userdel -f "$username"
        # Wipe database trace
        sed -i "/^$username|/d" $DB_USERS
        # Clean specific IPTables tracking loops
        iptables -D INPUT -p tcp --dport 22 -m comment --comment "vpngb_$username" -j ACCEPT 2>/dev/null
        iptables -D OUTPUT -p tcp --sport 22 -m comment --comment "vpngb_$username" -j ACCEPT 2>/dev/null
        netfilter-persistent save &>/dev/null
        echo -e "${GREEN}Account '$username' and all its configurations completely deleted!${NC}"
    else
        echo -e "${RED}User not found!${NC}"
    fi
}

# --------------------------------------------------------------------
# 4. BACKGROUND SYSTEM DAEMON LOGIC
# --------------------------------------------------------------------
run_enforcement() {
    [ ! -s $DB_USERS ] && return
    while IFS='|' read -r user pass exp gb speed; do
        [ -z "$user" ] && continue
        
        # Apply Dynamic Traffic Shaping if speed limit exists
        if [ "$speed" -gt 0 ] && [ "$NET_INT" != "" ]; then
            let kbps=$speed*1024
            wondershaper clear $NET_INT &>/dev/null
            wondershaper $NET_INT $kbps $kbps &>/dev/null
        fi

        # Check Data Quota Breach
        bytes=$(iptables -L -n -v -x | grep "vpngb_$user" | awk '{sum+=$2} END {print sum}')
        [ -z "$bytes" ] && bytes=0
        let current_gb=$bytes/1073741824
        
        if [ "$gb" -gt 0 ] && [ "$current_gb" -ge "$gb" ]; then
            # Lock system password and kick active sessions out
            passwd -l "$user" &>/dev/null
            pkill -u "$user" &>/dev/null
        fi
    done < $DB_USERS
}

# MAIN INTERACTIVE PANEL LOOP
while true; do
    # Run ongoing server-side checks
    run_enforcement

    echo -e "\n${YELLOW}=======================================${NC}"
    echo -e "${GREEN}    SlowDNS Dynamic Management Panel   ${NC}"
    echo -e "${YELLOW}=======================================${NC}"
    echo -e "${CYAN}[1]${NC} Create New Client Account"
    echo -e "${CYAN}[2]${NC} Monitor Accounts & Bandwidth"
    echo -e "${CYAN}[3]${NC} Delete Client Account"
    echo -e "${CYAN}[4]${NC} Exit Panel"
    echo -e "${YELLOW}=======================================${NC}"
    read -p "Choose an option [1-4]: " option
    echo ""

    case $option in
        1) create_account ;;
        2) monitor_accounts ;;
        3) delete_account ;;
        4) echo -e "${GREEN}Panel closed. Goodbye!${NC}"; exit 0 ;;
        *) echo -e "${RED}Invalid Selection! Please input 1-4.${NC}" ;;
    esac
done
