#!/bin/bash
# ==========================================
# 家庭私厨 — 阿里云部署脚本
# 用法: ./deploy.sh <服务器IP> [用户名]
# ==========================================
set -e

SERVER_IP="${1:?请提供服务器 IP，例如: ./deploy.sh 47.xx.xx.xx root}"
SERVER_USER="${2:-root}"
REMOTE_DIR="/opt/caipu"

echo "🚀 开始部署到 ${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}"

# 1. 创建远程目录
ssh "${SERVER_USER}@${SERVER_IP}" "mkdir -p ${REMOTE_DIR}/backend ${REMOTE_DIR}/uploads"

# 2. 上传后端代码
echo "📦 上传 backend/ ..."
rsync -avz --exclude '__pycache__' --exclude '*.pyc' --exclude 'data/*backup*' \
  ../../backend/ "${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/backend/"

# 3. 上传 init.sql
echo "📦 上传 init.sql ..."
scp ../../init.sql "${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/"

# 4. 上传 index.html
echo "📦 上传 index.html ..."
scp ../../index.html "${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/"

# 5. 上传配置
echo "📦 上传部署配置 ..."
scp nginx-caipu.conf "${SERVER_USER}@${SERVER_IP}:/tmp/"
scp caipu-api.service "${SERVER_USER}@${SERVER_IP}:/tmp/"
scp gunicorn_config.py "${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/backend/"

# 6. 在服务器上执行初始化
echo "🔧 服务器端初始化..."
ssh "${SERVER_USER}@${SERVER_IP}" << 'REMOTE_SCRIPT'
set -e
cd /opt/caipu/backend

# 安装 Python 依赖
pip3 install -r requirements.txt
pip3 install gunicorn

# 初始化数据库
echo "🗄️ 初始化数据库..."
mysql -u root -p < /opt/caipu/init.sql
python3 main.py seed

# 创建日志目录
mkdir -p /var/log/caipu /var/log/nginx

# 配置 systemd
cp /tmp/caipu-api.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable caipu-api
systemctl restart caipu-api

# 配置 Nginx
if command -v nginx &>/dev/null; then
  cp /tmp/nginx-caipu.conf /etc/nginx/conf.d/caipu.conf
  nginx -t && systemctl reload nginx
  echo "✅ Nginx 已配置"
else
  echo "⚠️ Nginx 未安装，跳过。请手动安装: apt install nginx"
fi

echo ""
echo "✅ 部署完成！"
echo "   curl http://127.0.0.1:5000/api/health"
REMOTE_SCRIPT

echo ""
echo "===== 部署完毕 ====="
echo "验证: curl http://${SERVER_IP}/api/health"
