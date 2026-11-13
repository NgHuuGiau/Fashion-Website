#!/bin/bash
# setup_server.sh - Cài đặt VPS cho Fashion Website
# Chạy với: sudo bash setup_server.sh

set -euo pipefail

DOMAIN="${1:-shop.example.com}"
ACME_EMAIL="${2:-admin@example.com}"
APP_DIR="/opt/fashion-website"
REPO_URL="https://github.com/NgHuuGiau/Fashion-Website.git"
[[ "$DOMAIN" =~ ^[A-Za-z0-9.-]+$ && "$ACME_EMAIL" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+$ ]] || {
    echo "Domain hoặc email ACME không hợp lệ" >&2
    exit 1
}

echo "=== Cài đặt VPS cho $DOMAIN ==="

# 1. Update & install dependencies
apt-get update && apt-get install -y \
    curl \
    git \
    gnupg2 \
    lsb-release \
    ca-certificates \
    ufw \
    fail2ban

# 2. Install Docker
if ! command -v docker &> /dev/null; then
    echo "Cài đặt Docker..."
    curl -fsSL https://get.docker.com | sh
    usermod -aG docker $SUDO_USER
fi

# 3. Install Docker Compose plugin
if ! docker compose version &> /dev/null; then
    echo "Cài đặt Docker Compose..."
    apt-get install -y docker-compose-plugin
fi

# 4. Configure firewall
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw --force enable

# 5. Configure fail2ban
cat > /etc/fail2ban/jail.local <<EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 10
EOF
systemctl restart fail2ban

# 6. Clone repository
if [ ! -d "$APP_DIR" ]; then
    git clone "$REPO_URL" "$APP_DIR"
    chown -R $SUDO_USER:$SUDO_USER "$APP_DIR"
else
    cd "$APP_DIR"
    git pull --ff-only origin main
fi

cd "$APP_DIR"
mkdir -p "$APP_DIR/logs" "$APP_DIR/backups"
chown -R "$SUDO_USER:$SUDO_USER" "$APP_DIR/logs" "$APP_DIR/backups"

# 7. Create .env.production from example
if [ ! -f .env.production ]; then
    cp .env.production.example .env.production
    echo "⚠️  CẦN CHỈNH SỬA .env.production VỚI GIÁ TRỊ THẬT!"
    echo "   nano $APP_DIR/.env.production"
fi
if [ ! -f .env.compose.production ]; then
    cp .env.compose.production.example .env.compose.production
    sed -i "s/^DOMAIN=.*/DOMAIN=$DOMAIN/" .env.compose.production
    sed -i "s/^ACME_EMAIL=.*/ACME_EMAIL=$ACME_EMAIL/" .env.compose.production
    echo "⚠️  CẦN CHỈNH SỬA .env.compose.production VỚI DOMAIN VÀ MẬT KHẨU THẬT!"
fi
chown "$SUDO_USER:$SUDO_USER" .env.production .env.compose.production
chmod 600 .env.production .env.compose.production

# 8. Create systemd service for auto-start
cat > /etc/systemd/system/fashion-website.service <<EOF
[Unit]
Description=Fashion Website
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$APP_DIR
ExecStart=/usr/bin/docker compose --env-file .env.compose.production -f docker-compose.yml -f docker-compose.production.yml up -d
ExecStop=/usr/bin/docker compose --env-file .env.compose.production -f docker-compose.yml -f docker-compose.production.yml down
TimeoutStartSec=120
User=$SUDO_USER
Group=docker

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable fashion-website.service

# 10. Create backup cron
cat > /etc/cron.d/fashion-backup <<EOF
# Sao lưu database và media mỗi ngày; script kiểm tra archive và dọn bản cũ.
30 2 * * * $SUDO_USER APP_DIR=$APP_DIR /bin/bash $APP_DIR/scripts/backup.sh >> $APP_DIR/logs/backup.log 2>&1
EOF

# 11. Create log rotation
cat > /etc/logrotate.d/fashion-website <<EOF
$APP_DIR/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 644 $SUDO_USER docker
    sharedscripts
    postrotate
        cd $APP_DIR && docker compose --env-file .env.compose.production -f docker-compose.yml -f docker-compose.production.yml restart app > /dev/null 2>&1 || true
    endscript
}
EOF

# 12. Create deploy script
cat > /usr/local/bin/deploy-fashion <<'EOF'
#!/bin/bash
set -euo pipefail
APP_DIR="/opt/fashion-website"
cd "$APP_DIR"
git pull --ff-only origin main
docker compose --env-file .env.compose.production -f docker-compose.yml -f docker-compose.production.yml pull
docker compose --env-file .env.compose.production -f docker-compose.yml -f docker-compose.production.yml up -d --build --remove-orphans
sleep 15
if ! curl -sf "https://$(sed -n 's/^DOMAIN=//p' .env.compose.production | head -n 1)/health/" >/dev/null; then
    echo "Health check failed!"
    docker compose --env-file .env.compose.production -f docker-compose.yml -f docker-compose.production.yml logs --tail=50
    exit 1
fi
docker image prune -f
echo "Deploy thành công!"
EOF
chmod +x /usr/local/bin/deploy-fashion

echo ""
echo "=== HOÀN TẤT ==="
echo ""
echo "Tiếp theo:"
echo "1. Chỉnh sửa $APP_DIR/.env.production với giá trị thật"
echo "2. Cấu hình DNS A record: $DOMAIN -> IP VPS này"
echo "3. Chạy deploy: /usr/local/bin/deploy-fashion"
echo "4. Kiểm tra: https://$DOMAIN/health/"
echo ""
echo "Service quản lý:"
echo "  systemctl start fashion-website"
echo "  systemctl stop fashion-website"
echo "  systemctl status fashion-website"
echo "  journalctl -u fashion-website -f"
