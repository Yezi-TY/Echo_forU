# 第三方开源项目声明

本项目使用了以下开源项目和库，特此声明并致谢。

## 主要依赖

### DiffRhythm2

- **项目**: DiffRhythm2
- **来源**: https://github.com/ASLP-lab/DiffRhythm2
- **作者**: ASLP Lab and Xiaomi Inc.
- **许可证**: Apache License 2.0
- **用途**: 音乐生成核心模型
- **论文**: https://arxiv.org/pdf/2510.22950

**引用**:
```
@article{diffrhythm2,
  title={DiffRhythm 2: Efficient and High Fidelity Song Generation via Block Flow Matching},
  author={Jiang, Yuepeng and Chen, Huakang and Ning, Ziqian and Yao, Jixun and Han, Zerui and Wu, Di and Meng, Meng and Luan, Jian and Fu, Zhonghua and Xie, Lei},
  journal={arXiv preprint arXiv:2510.22950},
  year={2025}
}
```

### MuQ-MuLan

- **项目**: MuQ-MuLan
- **来源**: Hugging Face - OpenMuQ/MuQ-MuLan-large
- **用途**: 风格提示编码
- **许可证**: 需要检查许可证

### BigVGAN

- **项目**: BigVGAN
- **用途**: 音频解码器
- **许可证**: 需要检查许可证

## Python 依赖

### 深度学习框架

- **PyTorch** (torch==2.7) - Apache License 2.0
- **torchaudio** (torchaudio==2.7) - BSD License
- **torchdiffeq** (torchdiffeq==0.2.5) - MIT License
- **transformers** (transformers==4.47.1) - Apache License 2.0

### 音频处理

- **librosa** (librosa==0.9.2) - ISC License
- **pedalboard** - MIT License
- **phonemizer** - GPL v3 License

### 文本处理

- **jieba** (jieba==0.42.1) - MIT License
- **pypinyin** (pypinyin==0.54.0) - MIT License
- **cn2an** (cn2an==0.5.23) - MIT License
- **pykakasi** (pykakasi==2.3.0) - Apache License 2.0
- **pyopenjtalk** (pyopenjtalk==0.4.1) - Apache License 2.0

### Web 框架

- **FastAPI** - MIT License
- **uvicorn** - BSD License

### 其他

- **numpy** (numpy==1.26.0) - BSD License
- **scipy** (scipy==1.15.2) - BSD License
- **einops** (einops==0.8.1) - MIT License
- **huggingface-hub** (huggingface-hub==0.31.1) - Apache License 2.0
- **safetensors** (safetensors==0.5.3) - Apache License 2.0
- **onnx** (onnx==1.17.0) - Apache License 2.0
- **onnxruntime** - MIT License

## 前端依赖

### 核心框架

- **React** - MIT License
- **Next.js** - MIT License
- **TypeScript** - Apache License 2.0

### UI 组件库

- **Material-UI (MUI)** - MIT License
- **@emotion/react** - MIT License
- **@emotion/styled** - MIT License

### 状态管理

- **Zustand** - MIT License
- **React Query** - MIT License

### 国际化

- **react-i18next** - MIT License
- **i18next** - MIT License
- **i18next-browser-languagedetector** - MIT License

### 桌面应用

- **Tauri** - Apache License 2.0 / MIT License

## 开发工具

- **pnpm** - MIT License
- **ESLint** - MIT License
- **Prettier** - MIT License
- **pytest** - MIT License
- **Black** - MIT License
- **flake8** - MIT License

## 系统依赖

- **espeak-ng** - GPL v3 License

---

**注意**: 本列表可能不完整，建议定期更新。所有依赖的完整许可证信息请参考各项目的官方文档。

