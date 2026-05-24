<p align="center">
  <h1 align="center">🎨 RepoViz</h1>
  <p align="center">
    <strong>Lightweight Git Repository Data Visualization Poster Generator</strong>
  </p>
  <p align="center">
    <a href="#-project-introduction--english">English</a> ·
    <a href="#-项目介绍--简体中文">简体中文</a> ·
    <a href="#-專案介紹--繁體中文">繁體中文</a>
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/Zero_Dependency-SVG_SVG-success.svg" alt="Zero Dependency SVG">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg" alt="Cross Platform">
</p>

---

<a id="-project-introduction--english"></a>

## 🎉 Project Introduction | English

**RepoViz** is a lightweight CLI tool that analyzes your local Git repository and generates beautiful data visualization posters in **SVG** and **PNG** formats. Inspired by trending GitHub visualization tools, RepoViz is built from scratch with a focus on **privacy-first local analysis**, **zero cloud dependencies**, and **elegant design**.

### 💡 Why RepoViz?

- 🔒 **100% Local** — All analysis happens on your machine. No data leaves your computer.
- ⚡ **Zero Dependency SVG** — SVG generation uses pure Python string building. No external libraries needed.
- 🎨 **3 Beautiful Templates** — Minimal, Gradient, and Dark themes to match your style.
- 📐 **2 Poster Sizes** — README-optimized (800×400) and Social-sharing (1200×630).
- 🖥️ **Cross-Platform** — Works on Windows, macOS, and Linux.

### ✨ Core Features

| Feature | Description |
|---------|-------------|
| 📊 **Language Distribution** | Auto-detect programming languages by file extension with GitHub-style color coding |
| 🗓️ **Commit Heatmap** | GitHub-style contribution heatmap for the past year (52 weeks × 7 days) |
| 👥 **Contributor Stats** | Top N contributors with commit count and line change statistics |
| 📈 **Code Growth Trend** | Monthly total line count evolution over time |
| ⏰ **Activity Patterns** | Commit distribution by day-of-week and hour-of-day |
| 📋 **Repo Overview** | Total commits, files, repo age, and more at a glance |

### 🚀 Quick Start

**Install:**

```bash
pip install git+https://github.com/gitstq/RepoViz.git
```

**Or clone and run directly:**

```bash
git clone https://github.com/gitstq/RepoViz.git
cd RepoViz
pip install -r requirements.txt
python -m repoviz.cli /path/to/your/repo
```

**Basic Usage:**

```bash
# Generate SVG poster with gradient theme for current directory
repoviz .

# Generate PNG poster with dark theme
repoviz /path/to/repo -f png -t dark

# Generate both formats with minimal theme for social sharing
repoviz . -f both -t minimal -s social

# Custom output path
repoviz . -o ./assets/poster.svg

# Exclude specific sections
repoviz . --no-heatmap --no-activity
```

### 📖 Detailed Usage Guide

**CLI Options:**

```
repoviz [PATH] [OPTIONS]

Arguments:
  PATH                    Git repository path (default: current directory)

Options:
  -o, --output PATH       Output file path (default: repoviz.<format>)
  -f, --format FORMAT     Output format: svg / png / both (default: svg)
  -t, --template NAME     Template: minimal / gradient / dark (default: gradient)
  -s, --size SIZE         Poster size: readme / social (default: readme)
  --top N                 Top N contributors (default: 5)
  --no-heatmap            Exclude commit heatmap
  --no-languages          Exclude language distribution
  --no-contributors       Exclude contributor stats
  --no-activity           Exclude activity patterns
  -v, --version           Show version
```

**Template Preview:**

| Template | Style | Best For |
|----------|-------|----------|
| `minimal` | Clean white background, gray text, blue accents | Professional READMEs |
| `gradient` | Purple-to-blue gradient, white text | Eye-catching profiles |
| `dark` | Dark gray background, green/cyan accents | Dark-themed projects |

**Embedding SVG in README:**

```markdown
![RepoViz](repoviz.svg)
```

### 💡 Design Philosophy & Roadmap

**Design Principles:**
- **Privacy First**: All computation is local. No API calls, no data uploads.
- **Simplicity**: One command to generate. No configuration files needed.
- **Elegance**: Clean, modern visual design inspired by GitHub's aesthetic.

**Roadmap:**
- [ ] Web UI for interactive poster customization
- [ ] Additional templates (neon, pastel, retro)
- [ ] Organization/team-level multi-repo dashboards
- [ ] CI/CD integration for auto-updated README posters
- [ ] Animated SVG support

### 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Commit Convention:** Follow [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`, `refactor:`, etc.)

### 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

<a id="-项目介绍--简体中文"></a>

## 🎉 项目介绍 | 简体中文

**RepoViz** 是一款轻量级 CLI 工具，能够分析本地 Git 仓库数据并生成精美的 **SVG/PNG 可视化海报**。灵感来源于 GitHub Trending 上的热门仓库可视化工具，RepoViz 从零自研，专注于**隐私优先的本地分析**、**零云端依赖**和**优雅的设计美学**。

### 💡 为什么选择 RepoViz？

- 🔒 **100% 本地运行** — 所有分析均在本地完成，数据不离开你的电脑
- ⚡ **零依赖 SVG 生成** — SVG 渲染使用纯 Python 字符串拼接，无需任何外部库
- 🎨 **3 种精美模板** — 极简、渐变、暗黑三种风格，满足不同审美需求
- 📐 **2 种海报尺寸** — README 优化版（800×400）和社交分享版（1200×630）
- 🖥️ **跨平台兼容** — 完美支持 Windows、macOS 和 Linux

### ✨ 核心特性

| 特性 | 说明 |
|------|------|
| 📊 **语言分布** | 通过文件扩展名自动检测编程语言，采用 GitHub 官方配色方案 |
| 🗓️ **提交热力图** | 类似 GitHub 贡献图的过去一年提交频率可视化（52周×7天） |
| 👥 **贡献者统计** | Top N 贡献者排行，展示提交数和代码行数变更 |
| 📈 **代码增长趋势** | 按月统计的总代码行数演变曲线 |
| ⏰ **活跃时段分析** | 按星期几和小时维度的提交分布热力图 |
| 📋 **仓库概览** | 总提交数、文件数、仓库年龄等关键指标一览 |

### 🚀 快速开始

**安装：**

```bash
pip install git+https://github.com/gitstq/RepoViz.git
```

**或克隆后直接运行：**

```bash
git clone https://github.com/gitstq/RepoViz.git
cd RepoViz
pip install -r requirements.txt
python -m repoviz.cli /path/to/your/repo
```

**基础用法：**

```bash
# 使用渐变模板为当前目录生成 SVG 海报
repoviz .

# 使用暗黑模板生成 PNG 海报
repoviz /path/to/repo -f png -t dark

# 同时生成两种格式，使用极简模板，社交分享尺寸
repoviz . -f both -t minimal -s social

# 自定义输出路径
repoviz . -o ./assets/poster.svg

# 排除特定模块
repoviz . --no-heatmap --no-activity
```

### 📖 详细使用指南

**CLI 参数说明：**

```
repoviz [路径] [选项]

参数：
  PATH                    Git 仓库路径（默认：当前目录）

选项：
  -o, --output PATH       输出文件路径（默认：repoviz.<格式>）
  -f, --format FORMAT     输出格式：svg / png / both（默认：svg）
  -t, --template NAME     模板：minimal / gradient / dark（默认：gradient）
  -s, --size SIZE         海报尺寸：readme / social（默认：readme）
  --top N                 Top N 贡献者（默认：5）
  --no-heatmap            不包含提交热力图
  --no-languages          不包含语言分布
  --no-contributors       不包含贡献者统计
  --no-activity           不包含活跃时段
  -v, --version           显示版本号
```

**模板风格说明：**

| 模板 | 风格 | 适用场景 |
|------|------|----------|
| `minimal` | 白底、灰色文字、蓝色强调 | 专业 README 嵌入 |
| `gradient` | 紫蓝渐变背景、白色文字 | 吸引眼球的项目主页 |
| `dark` | 深灰背景、绿色/青色强调 | 暗黑主题项目 |

**在 README 中嵌入 SVG 海报：**

```markdown
![RepoViz](repoviz.svg)
```

### 💡 设计思路与迭代规划

**设计理念：**
- **隐私优先**：所有计算均在本地完成，无 API 调用，无数据上传
- **简洁至上**：一条命令生成海报，无需配置文件
- **优雅美学**：参考 GitHub 设计语言，打造现代感视觉体验

**后续规划：**
- [ ] Web UI 交互式海报自定义编辑器
- [ ] 更多模板（霓虹、马卡龙、复古风等）
- [ ] 组织/团队级多仓库聚合仪表盘
- [ ] CI/CD 集成，自动更新 README 海报
- [ ] 动画 SVG 支持

### 🤝 贡献指南

欢迎贡献代码！请按以下步骤操作：

1. Fork 本仓库
2. 创建功能分支（`git checkout -b feature/amazing-feature`）
3. 提交更改（`git commit -m 'feat: 新增超棒功能'`）
4. 推送分支（`git push origin feature/amazing-feature`）
5. 发起 Pull Request

**提交规范**：遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范（`feat:`、`fix:`、`docs:`、`refactor:` 等）

### 📄 开源协议

本项目基于 **MIT 协议** 开源。详见 [LICENSE](LICENSE) 文件。

---

<a id="-專案介紹--繁體中文"></a>

## 🎉 專案介紹 | 繁體中文

**RepoViz** 是一款輕量級 CLI 工具，能夠分析本地 Git 倉庫資料並生成精美的 **SVG/PNG 視覺化海報**。靈感來自 GitHub Trending 上的熱門倉庫視覺化工具，RepoViz 從零自研，專注於**隱私優先的本地分析**、**零雲端依賴**和**優雅的設計美學**。

### 💡 為什麼選擇 RepoViz？

- 🔒 **100% 本地運行** — 所有分析均在本地完成，資料不離開你的電腦
- ⚡ **零依賴 SVG 生成** — SVG 渲染使用純 Python 字串拼接，無需任何外部函式庫
- 🎨 **3 種精美模板** — 極簡、漸層、暗黑三種風格，滿足不同審美需求
- 📐 **2 種海報尺寸** — README 最佳化版（800×400）和社群分享版（1200×630）
- 🖥️ **跨平台相容** — 完美支援 Windows、macOS 和 Linux

### ✨ 核心特性

| 特性 | 說明 |
|------|------|
| 📊 **語言分佈** | 透過副檔名自動偵測程式語言，採用 GitHub 官方配色方案 |
| 🗓️ **提交熱力圖** | 類似 GitHub 貢獻圖的過去一年提交頻率視覺化（52 週×7 天） |
| 👥 **貢獻者統計** | Top N 貢獻者排行，展示提交數和程式碼行數變更 |
| 📈 **程式碼增長趨勢** | 按月統計的總程式碼行數演變曲線 |
| ⏰ **活躍時段分析** | 按星期幾和小時維度的提交分佈熱力圖 |
| 📋 **倉庫概覽** | 總提交數、檔案數、倉庫年齡等關鍵指標一覽 |

### 🚀 快速開始

**安裝：**

```bash
pip install git+https://github.com/gitstq/RepoViz.git
```

**或複製後直接運行：**

```bash
git clone https://github.com/gitstq/RepoViz.git
cd RepoViz
pip install -r requirements.txt
python -m repoviz.cli /path/to/your/repo
```

**基礎用法：**

```bash
# 使用漸層模板為目前目錄生成 SVG 海報
repoviz .

# 使用暗黑模板生成 PNG 海報
repoviz /path/to/repo -f png -t dark

# 同時生成兩種格式，使用極簡模板，社群分享尺寸
repoviz . -f both -t minimal -s social

# 自訂輸出路徑
repoviz . -o ./assets/poster.svg

# 排除特定模組
repoviz . --no-heatmap --no-activity
```

### 📖 詳細使用指南

**CLI 參數說明：**

```
repoviz [路徑] [選項]

參數：
  PATH                    Git 倉庫路徑（預設：目前目錄）

選項：
  -o, --output PATH       輸出檔案路徑（預設：repoviz.<格式>）
  -f, --format FORMAT     輸出格式：svg / png / both（預設：svg）
  -t, --template NAME     模板：minimal / gradient / dark（預設：gradient）
  -s, --size SIZE         海報尺寸：readme / social（預設：readme）
  --top N                 Top N 貢獻者（預設：5）
  --no-heatmap            不包含提交熱力圖
  --no-languages          不包含語言分佈
  --no-contributors       不包含貢獻者統計
  --no-activity           不包含活躍時段
  -v, --version           顯示版本號
```

**模板風格說明：**

| 模板 | 風格 | 適用場景 |
|------|------|----------|
| `minimal` | 白底、灰色文字、藍色強調 | 專業 README 嵌入 |
| `gradient` | 紫藍漸層背景、白色文字 | 吸引眼球的作品集首頁 |
| `dark` | 深灰背景、綠色/青色強調 | 暗黑主題專案 |

**在 README 中嵌入 SVG 海報：**

```markdown
![RepoViz](repoviz.svg)
```

### 💡 設計思路與迭代規劃

**設計理念：**
- **隱私優先**：所有計算均在本地完成，無 API 呼叫，無資料上傳
- **簡潔至上**：一條指令生成海報，無需設定檔
- **優雅美學**：參考 GitHub 設計語言，打造現代感視覺體驗

**後續規劃：**
- [ ] Web UI 互動式海報自訂編輯器
- [ ] 更多模板（霓虹、馬卡龍、復古風等）
- [ ] 組織/團隊級多倉庫聚合儀表板
- [ ] CI/CD 整合，自動更新 README 海報
- [ ] 動畫 SVG 支援

### 🤝 貢獻指南

歡迎貢獻程式碼！請按以下步驟操作：

1. Fork 本倉庫
2. 建立功能分支（`git checkout -b feature/amazing-feature`）
3. 提交變更（`git commit -m 'feat: 新增超棒功能'`）
4. 推送分支（`git push origin feature/amazing-feature`）
5. 發起 Pull Request

**提交規範**：遵循 [Conventional Commits](https://www.conventionalcommits.org/) 規範（`feat:`、`fix:`、`docs:`、`refactor:` 等）

### 📄 開源協議

本專案基於 **MIT 協議** 開源。詳見 [LICENSE](LICENSE) 檔案。
