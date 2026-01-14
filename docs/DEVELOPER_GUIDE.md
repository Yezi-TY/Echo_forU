# DiffRhythm2 GUI 开发指南

## 开发环境搭建

### 前置要求

- Node.js 18+
- Python 3.9+
- pnpm
- Rust (用于 Tauri 开发)

### 安装步骤

1. 克隆项目
2. 安装前端依赖：
   ```bash
   cd frontend
   pnpm install
   ```

3. 安装后端依赖：
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

## 项目结构

- `frontend/shared/` - 共享前端代码
- `frontend/web/` - Next.js Web 应用
- `frontend/desktop/` - Tauri 桌面应用
- `backend/` - Python FastAPI 后端
- `Build/` - 所有生成的文件

## 开发流程

### 启动开发服务器

```bash
# 后端
cd backend
python main.py

# 前端 Web
cd frontend
pnpm --filter web dev

# 前端 Desktop
cd frontend
pnpm --filter desktop tauri dev
```

### 代码规范

- 前端：使用 ESLint 和 Prettier
- 后端：使用 Black 和 flake8

运行检查：
```bash
# 前端
pnpm lint

# 后端
black backend/
flake8 backend/
```

### 测试

```bash
# 后端测试
cd backend
pytest

# 前端测试
cd frontend/shared
pnpm test
```

## API 文档

启动后端服务后，访问 http://localhost:8000/api/docs 查看 Swagger API 文档。

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

