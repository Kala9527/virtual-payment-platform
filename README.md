# Virtual Payment Platform

本地私密在线支付交易平台，用于展示虚拟商品并让用户选择支付宝或微信收款码完成支付确认。

## 技术栈

- Backend: FastAPI, SQLAlchemy, SQLite
- Frontend: Vue 3, Vite, Pinia, Vue Router
- Runtime: Conda environment at `D:\Miniconda3\envs\virtual_pay_platform_env`

## 本地运行

后端：

```powershell
cd D:\工作区文件夹\test_explore\virtual-payment-platform\backend
conda activate D:\Miniconda3\envs\virtual_pay_platform_env
uvicorn app.main:app --reload --port 8006
```

前端：

```powershell
cd D:\工作区文件夹\test_explore\virtual-payment-platform\frontend
npm run dev
```

也可以直接双击项目根目录的 `start-backend.bat` 和 `start-frontend.bat` 分别启动后端和前端。

## 邮件通知

未配置 SMTP 时，确认支付会把邮件内容写入 `backend/outbox` 目录，便于本地测试。
需要真实发送时，复制 `backend/.env.example` 为 `backend/.env` 并配置 SMTP。
