# Majiang AI Assistant - 麻将智能助手

🀄 基于 YOLOv8 视觉识别 + 硬核战术引擎的贵阳捉鸡麻将端到端 AI 助手

---

## 项目概述

本项目是一个完整的麻将智能辅助系统，实现了从**视觉感知**到**战术决策**的全流程自动化：

```
牌桌截图 → YOLO视觉识别 → 战术分析引擎 → 最优出牌建议
```

---

## 核心功能

### 1. 视觉识别模块 (`mahjong_vision.py`)
- **基于 YOLOv8**：使用自定义训练的 `yolov8x_v7_rotated_clean` 模型
- **实时检测**：识别麻将牌的位置、类别和置信度
- **智能排序**：按从左到右顺序自动整理手牌
- **术语对齐**：内部使用代号（C=万, B=条, D=筒），输出可转中文

### 2. 战术决策引擎 (`strategy/`)
- **极速判胡与听牌**：基于内存查表实现 O(1) 复杂度的微秒级判定
- **全阶段 AI 出牌推荐**：
  - **听牌状态**：直接给出最优听牌打法
  - **一向听**：精确预测，穷举未来进张
  - **多向听**：宏观降维，DFS 状态机规划做牌路线
  - **防守模式**：牌型过差时建议转防守

### 3. 端到端整合 (`mahjong_e2e.py`)
- **一键分析**：输入图片路径，输出完整决策报告
- **LLM 友好**：自动生成 Prompt，可直接发送给大模型
- **双语输出**：支持代号/中文切换

---

## 项目结构

```
majiangProject/
├── cv/                          # 计算机视觉相关
│   ├── dataset/                 # 数据集
│   ├── runs/detect/             # 训练结果和模型权重
│   └── ...
│
├── mahjong_vision.py           # 视觉识别模块 ⭐NEW
├── mahjong_e2e.py              # 端到端整合模块 ⭐NEW
├── END_TO_END.md               # 端到端使用文档 ⭐NEW
│
├── strategy/                   # 战术决策引擎
│   ├── main.py                 # 主入口
│   ├── judge_hu.py             # 胡牌判断
│   ├── check_ting.py           # 听牌检查
│   ├── best_discard.py         # 最优出牌
│   ├── draw_calculator.py      # 向听数计算
│   ├── analyzer_unit.py        # 单花色分析
│   └── tile_mapper.py          # 牌名映射
│
├── main.py                     # 纯逻辑引擎测试入口
└── Readme.md                   # 本文件
```

---

## 快速开始

### 环境准备

```bash
# 激活虚拟环境（已配置好 YOLOv8 + PyTorch）
source cv/dataset/yolo_env/bin/activate
```

### 端到端使用（推荐）

```python
from mahjong_e2e import MahjongEndToEndAgent

# 初始化代理
agent = MahjongEndToEndAgent()

# 分析牌桌图片
result = agent.process_image("path/to/screenshot.jpg", use_chinese=True)

# 查看决策
print(result["final_decision"])
# 输出：建议打出：二条 (2b)
#       理由：当前处于【一向听】状态...

# 获取 LLM Prompt
print(result["llm_prompt"])
```

### 命令行测试

```bash
# 分析图片
python mahjong_e2e.py cv/dataset/guiyang_test/test.png

# 或直接输入手牌
python mahjong_e2e.py
# 输入：1C 2C 3C 7C 8C 9C 2B 2B 5B 5B 5B 2B 3D
```

### 纯逻辑引擎测试（无需图片）

```bash
python main.py
```

---

## 术语对照

| 代号 | 中文 | 说明 |
|:---:|:---:|:---|
| 1C-9C | 一万-九万 | 万子 (Characters) |
| 1B-9B | 一条-九条 | 条子/索子 (Bamboos) |
| 1D-9D | 一筒-九筒 | 筒子 (Dots) |

**内部交互使用代号，展示给用户时自动翻译为中文。**

---

## 模型信息

- **模型**: YOLOv8x
- **版本**: v7_rotated_clean
- **类别**: 27 类（万、条、筒各 1-9）

---

## 示例输出

### 视觉识别
```
画面中共检测到 13 张牌。
从左到右依次为：1B, 1B, 1B, 2B, 3C, 6C, 6C, 8D, 8D, 8D, 6B
```

### 战术分析
```
当前处于【一向听】状态。
建议打出【2条】，未来摸到这 11 张牌即可听牌:
1万, 2万, 3万, 4万, 5万, 6万, 4条, 5条, 6条, 7条, 8条
```

---

## 技术栈

- **视觉**: YOLOv8 (Ultralytics), OpenCV
- **算法**: Python 3.12, 组合数学查表, DFS 状态机
- **平台**: Linux, NVIDIA GPU (CUDA)

---

## 更新日志

- **2026-03-27**: 接入 YOLOv8 视觉识别模块，实现端到端自动化
- **2026-03-15**: 完成战术引擎核心算法（一向听/多向听分层决策）
- **2026-03-14**: 项目初始化，完成基础牌理逻辑

---

## 后续计划

- [ ] **提高 YOLO 检测精度** - 增加训练数据，优化边缘案例（遮挡、反光）
- [ ] **优化麻将策略** - 添加防守策略（危险牌检测）、捉鸡规则支持
- [ ] **GUI 界面** - 实时显示识别结果和可视化分析

---

## 许可证

MIT License

---

## 致谢

感谢数据提供者 **yuqin sun** 对本项目的大力支持！

---

*Made with 🀄 by zxian & Mini Chao*
