# 阿里云 ECS 公网 IP 部署步骤

本文档适合第一次把本项目部署到公网测试。目标形态是：GitHub 私有仓库存放源码，阿里云 ECS 拉取代码，前端构建为静态文件，由 FastAPI 同一个服务对外提供页面和 API，数据库暂时使用 SQLite。

## 1. 注册和准备账号

1. 注册 GitHub 账号并登录：https://github.com
2. 注册阿里云账号并完成实名认证：https://www.aliyun.com
3. 在阿里云控制台确认账户余额或绑定支付方式。
4. 本地安装 Git，并确认可以访问 GitHub：

```powershell
git --version
git config --global user.name
git config --global user.email
```

## 2. 创建 GitHub 私有仓库

1. 打开 https://github.com/new
2. Repository owner 选择 `Kala9527`。
3. Repository name 填 `virtual-payment-platform`。
4. Visibility 选择 `Private`。
5. 不要勾选添加 README、.gitignore、license，因为本地项目里已经有文件。
6. 点击 Create repository。

本地项目首次推送：

```powershell
cd D:\工作区文件夹\test_explore\virtual-payment-platform
git remote add origin https://github.com/Kala9527/virtual-payment-platform.git
git branch -M main
git push -u origin main
```

如果提示登录，使用浏览器登录 GitHub，或使用 GitHub Personal Access Token 作为密码。

## 3. 购买阿里云 ECS

第一次公网测试可以选择低配置：

- 地域：优先选择离主要访问者近的地域，例如华东 1、华东 2、华南 1。
- 实例规格：1 vCPU / 1 GB 或 2 vCPU / 2 GB 均可，预算允许建议 2 GB 内存。
- 镜像：Ubuntu 22.04 LTS 或 Ubuntu 24.04 LTS。
- 系统盘：20 GB 起。
- 公网 IP：勾选分配公网 IPv4。
- 带宽：按固定带宽 1 Mbps 起，测试够用。
- 登录方式：建议 SSH 密钥；也可以先用密码。
- 安全组：后续至少放行 TCP 22 和 TCP 8006。

购买完成后，在 ECS 实例详情页记录公网 IP，例如：

```text
SERVER_IP=你的公网IP
```

## 4. 配置安全组

进入 ECS 实例详情页：

1. 点击安全组。
2. 进入安全组规则。
3. 入方向添加规则：

| 协议类型 | 端口范围 | 授权对象 | 用途 |
| --- | --- | --- | --- |
| SSH | 22 | 你的本机公网 IP/32 | 服务器登录 |
| TCP | 8006 | 0.0.0.0/0 | 本项目公网测试 |

测试阶段可以先开放 8006。正式上线建议改用 Nginx + HTTPS，只开放 80/443。

## 5. 登录服务器

Windows PowerShell：

```powershell
ssh root@SERVER_IP
```

如果是密钥：

```powershell
ssh -i C:\path\to\your-key.pem root@SERVER_IP
```

## 6. 安装服务器依赖

在 ECS 上执行：

```bash
apt update
apt install -y git curl python3 python3-venv python3-pip nginx
curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
apt install -y nodejs
node -v
npm -v
python3 --version
```

## 7. 让服务器可以拉取私有仓库

推荐方式是给服务器创建只用于部署的 SSH key：

```bash
ssh-keygen -t ed25519 -C "aliyun-ecs-virtual-payment-platform" -f ~/.ssh/virtual_payment_platform -N ""
cat ~/.ssh/virtual_payment_platform.pub
```

复制输出的公钥，打开 GitHub 仓库：

1. Settings
2. Deploy keys
3. Add deploy key
4. Title 填 `aliyun-ecs`
5. Key 粘贴公钥
6. 只需要拉取代码就不要勾选 Allow write access
7. Add key

然后在服务器配置 SSH：

```bash
cat > ~/.ssh/config <<'EOF'
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/virtual_payment_platform
  IdentitiesOnly yes
EOF
chmod 600 ~/.ssh/config
ssh -T git@github.com
```

看到认证成功或无 shell 权限的提示即可。

## 8. 拉取项目代码

```bash
mkdir -p /opt/apps
cd /opt/apps
git clone git@github.com:Kala9527/virtual-payment-platform.git
cd virtual-payment-platform
```

## 9. 配置后端环境和 SQLite

```bash
cd /opt/apps/virtual-payment-platform
cp backend/.env.example backend/.env
nano backend/.env
```

建议测试阶段内容：

```env
APP_ENV=production
FRONTEND_ORIGIN=http://SERVER_IP:8006
FRONTEND_ORIGINS=http://SERVER_IP:8006
DATABASE_URL=sqlite:////opt/apps/virtual-payment-platform/backend/app.db
MERCHANT_EMAIL=merchant@example.com
```

把 `SERVER_IP` 替换为你的 ECS 公网 IP。暂时不配置 SMTP 时，支付确认邮件会写入 `backend/outbox/`。

## 10. 安装后端依赖

```bash
cd /opt/apps/virtual-payment-platform/backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python -m pytest
```

## 11. 构建前端

本项目生产环境下前端默认使用同源 API，所以不需要额外设置 `VITE_API_BASE_URL`：

```bash
cd /opt/apps/virtual-payment-platform/frontend
npm ci
npm run build
```

构建后会生成 `frontend/dist`，FastAPI 会自动挂载这个目录。

## 12. 先手动启动测试

```bash
cd /opt/apps/virtual-payment-platform/backend
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8006
```

在浏览器打开：

```text
http://SERVER_IP:8006
http://SERVER_IP:8006/health
```

如果页面能打开，按 `Ctrl+C` 停止手动进程，继续配置后台服务。

## 13. 配置 systemd 后台运行

创建服务文件：

```bash
cat > /etc/systemd/system/virtual-payment-platform.service <<'EOF'
[Unit]
Description=Virtual Payment Platform
After=network.target

[Service]
WorkingDirectory=/opt/apps/virtual-payment-platform/backend
EnvironmentFile=/opt/apps/virtual-payment-platform/backend/.env
ExecStart=/opt/apps/virtual-payment-platform/backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8006
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now virtual-payment-platform
systemctl status virtual-payment-platform
```

查看日志：

```bash
journalctl -u virtual-payment-platform -f
```

## 14. 后续更新部署

本地修改并推送后，在服务器执行：

```bash
cd /opt/apps/virtual-payment-platform
git pull

cd backend
source .venv/bin/activate
pip install -r requirements.txt

cd ../frontend
npm ci
npm run build

systemctl restart virtual-payment-platform
systemctl status virtual-payment-platform
```

## 15. 常见问题

- 页面打不开：检查阿里云安全组是否放行 8006，服务是否正在运行。
- `/health` 正常但页面异常：重新执行 `cd frontend && npm run build`。
- API 跨域报错：确认 `backend/.env` 中 `FRONTEND_ORIGINS` 是 `http://SERVER_IP:8006`。
- SQLite 权限错误：确认服务运行用户对 `/opt/apps/virtual-payment-platform/backend` 有写权限。
- GitHub clone 失败：检查 Deploy key 是否添加到正确仓库，服务器 SSH config 是否指向正确私钥。

## 16. 正式上线前建议

- 使用域名、Nginx 反向代理和 HTTPS。
- 关闭公网 8006，只开放 80/443。
- 把 SQLite 迁移到 MySQL、PostgreSQL 或阿里云 RDS。
- 配置真实 SMTP。
- 添加备份脚本，至少备份 `backend/app.db`。
