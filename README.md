# DiffRhythm2 GUI - 音乐生成图形界面

基于 DiffRhythm2 的跨平台音乐生成图形界面，支持 Web 和桌面应用。

## 功能特性

- 🎵 基于 DiffRhythm2 的高质量音乐生成
- 🌐 Web 界面（Next.js）
- 💻 桌面应用（Tauri，支持 Windows/Mac/Linux）
- 🎨 Material-UI 现代化界面设计
- 🌍 多语言支持（中文、英文、日文）
- ⚡ 硬件自适应优化（自动检测 GPU，优化性能）
- 📊 实时生成进度显示
- 📝 生成历史管理

## 技术栈

### 前端
- Next.js 14+ (App Router)
- React + TypeScript
- Material-UI (MUI) v5+
- pnpm workspaces
- Tauri 2.x (桌面应用)

### 后端
- Python FastAPI
- PyTorch 2.7
- DiffRhythm2 模型

## 项目结构

```
Music_Gen_UI/
├── frontend/          # 前端应用（pnpm workspaces）
│   ├── shared/       # 共享代码
│   ├── web/          # Next.js Web 应用
│   └── desktop/      # Tauri 桌面应用
├── backend/           # Python 后端服务
├── Build/            # 生成文件目录
└── example/          # 原始 DiffRhythm2 代码（参考）
```

## 快速开始

### 环境要求

- Node.js 18+
- Python 3.8+
- pnpm
- Rust (用于 Tauri 桌面应用)
- espeak-ng

### 安装

#### 方式一：使用自动设置脚本（推荐）

```bash
# 克隆项目
git clone <repository-url>
cd Music_Gen_UI

# 运行设置脚本（自动安装所有依赖）
chmod +x scripts/setup.sh
./scripts/setup.sh
```

#### 方式二：手动安装

```bash
# 克隆项目
git clone <repository-url>
cd Music_Gen_UI

# 安装前端依赖
cd frontend
pnpm install

# 安装后端依赖
cd ../backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 开发

#### 方式一：使用启动脚本（推荐）

```bash
# 启动后端服务
./scripts/start-backend.sh

# 启动 Web 应用（新终端）
./scripts/start-web.sh

# 启动桌面应用（新终端，可选）
./scripts/start-desktop.sh

# 或同时启动 Web 和桌面应用
./scripts/start-frontend.sh
```

#### 方式二：手动启动

```bash
# 启动后端服务
cd backend
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m backend.main

# 启动 Web 应用（新终端）
cd frontend
pnpm --filter web dev

# 启动桌面应用（新终端）
cd frontend
pnpm --filter desktop tauri:dev
```

## 开源项目引用

本项目基于以下开源项目：

### DiffRhythm2

- **项目**: [DiffRhythm2](https://github.com/ASLP-lab/DiffRhythm2)
- **作者**: ASLP Lab and Xiaomi Inc.
- **许可证**: Apache License 2.0
- **论文**: [DiffRhythm 2: Efficient and High Fidelity Song Generation via Block Flow Matching](https://arxiv.org/pdf/2510.22950)

**引用**:
```
@article{diffrhythm2,
  title={DiffRhythm 2: Efficient and High Fidelity Song Generation via Block Flow Matching},
  author={Jiang, Yuepeng and Chen, Huakang and Ning, Ziqian and Yao, Jixun and Han, Zerui and Wu, Di and Meng, Meng and Luan, Jian and Fu, Zhonghua and Xie, Lei},
  journal={arXiv preprint arXiv:2510.22950},
  year={2025}
}
```

### 其他依赖

详细的第三方开源项目列表请参见 [NOTICES.md](NOTICES.md)。

## 许可证

本项目采用 Apache License 2.0 许可证。详见 [LICENSE](LICENSE) 文件。

## 致谢

感谢以下项目和团队：

- **ASLP Lab 和 Xiaomi Inc.** - 开发了 DiffRhythm2 模型
- **Material-UI 团队** - 提供了优秀的 React UI 组件库
- **Tauri 团队** - 提供了轻量级的桌面应用框架
- **FastAPI 团队** - 提供了高性能的 Python Web 框架

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题或建议，请通过 GitHub Issues 联系。

