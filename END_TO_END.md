# Mahjong End-to-End Skill - 完整使用指南

🀄 从视觉识别到战术决策的端到端麻将 AI 技能

---

## 📦 技能结构

```
mahjong-vision/
├── SKILL.md              # 技能说明
├── mahjong_vision.py     # 视觉识别模块
├── strategy_api.py       # 战术决策引擎
├── mahjong_e2e.py        # 端到端整合模块
└── USAGE.md              # 本文档
```

---

## 🚀 快速开始

### 方式 1: 端到端使用（推荐）

```python
from mahjong_e2e import MahjongEndToEndAgent

# 初始化代理（自动加载视觉和战术模块）
agent = MahjongEndToEndAgent()

# 处理牌桌图片
result = agent.process_image("/path/to/screenshot.jpg", use_chinese=True)

# 获取最终决策
print(result["final_decision"])
# 输出：建议打出：三筒 (3d)
#       理由：当前处于【一向听】状态...

# 获取 LLM Prompt（可直接发送给大模型）
print(result["llm_prompt"])
```

### 方式 2: 分步使用

```python
from mahjong_vision import MahjongVisionAgent
from strategy_api import MahjongStrategyEngine

# 初始化模块
vision = MahjongVisionAgent()
strategy = MahjongStrategyEngine()

# 步骤 1: 视觉识别
vision_result = vision.analyze_scene("screenshot.jpg", use_chinese=False)
hand_tiles = [tile['name'] for tile in vision_result['tiles']]

# 步骤 2: 战术分析
decision = strategy.evaluate_hand(hand_tiles)

# 步骤 3: 输出决策
print(decision['raw_text_summary'])
```

### 方式 3: 快速决策（已知手牌）

```python
from mahjong_e2e import MahjongEndToEndAgent

agent = MahjongEndToEndAgent()

# 直接输入手牌列表
hand = ['1C', '2C', '3C', '7C', '8C', '9C', '2B', '2B', '5B', '5B', '5B', '2B', '3D']
result = agent.quick_decision(hand, use_chinese=True)
print(result)
```

---

## 📊 完整工作流

```
┌─────────────────┐
│  牌桌截图       │
│  (JPG/PNG)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  视觉识别模块   │
│  MahjongVision  │
└────────┬────────┘
         │
         │ 输出：['1C', '2C', '3C', ...]
         ▼
┌─────────────────┐
│  战术决策引擎   │
│  StrategyEngine │
└────────┬────────┘
         │
         │ 输出：状态 + 建议
         ▼
┌─────────────────┐
│  最终决策       │
│  + LLM Prompt   │
└─────────────────┘
```

---

## 📋 输出数据详解

### process_image() 返回值

```python
{
    "image_path": "/path/to/screenshot.jpg",
    
    "vision_result": {
        "total_tiles": 13,
        "tiles": [
            {"name": "1C", "confidence": 0.95, "box": [...]}
        ],
        "raw_text_summary": "画面中共检测到 13 张牌...",
        "summary_chinese": "画面中共检测到 13 张牌..."
    },
    
    "strategy_result": {
        "hand": ["1c", "2c", "3c", ...],
        "status": "1_SHANTEN",
        "recommendations": [
            {
                "discard": "3d",
                "target_tiles": ["2d", "5d"],
                "target_count": 2
            }
        ],
        "raw_text_summary": "当前处于【一向听】状态..."
    },
    
    "final_decision": "建议打出：三筒 (3d)...",
    
    "llm_prompt": "🀄 麻将决策请求\n\n【视觉识别结果】..."
}
```

### 状态码说明

| 状态码 | 含义 | 说明 |
|--------|------|------|
| `HU` | 胡牌 | 牌型已满足胡牌条件 |
| `TING` | 听牌 | 打出一张后即可听牌 |
| `1_SHANTEN` | 一向听 | 距离听牌还差 1 张进张 |
| `N_SHANTEN` | 多向听 | 距离听牌还差多张 |
| `DEFEND` | 防守 | 建议转为防守策略 |

---

## 🤖 在 OpenClaw 中的完整使用示例

```python
from mahjong_e2e import MahjongEndToEndAgent

# 1. 在 OpenClaw 启动时初始化（全局单例）
mahjong_agent = MahjongEndToEndAgent()

# 2. 定义决策函数
def decide_mahjong_action(image_path):
    """
    OpenClaw 麻将决策入口
    
    Args:
        image_path: 牌桌截图路径
        
    Returns:
        str: 最终行动决策
    """
    # 处理图片
    result = mahjong_agent.process_image(image_path, use_chinese=True)
    
    # 检查错误
    if "error" in result.get("vision_result", {}):
        return f"视觉识别失败：{result['vision_result']['error']}"
    
    # 获取 LLM Prompt
    prompt = result["llm_prompt"]
    
    # 调用大模型（这里使用 OpenClaw 的 LLM 接口）
    # final_decision = call_llm(prompt)
    
    # 或直接使用内置决策
    return result["final_decision"]

# 3. 使用示例
action = decide_mahjong_action("/path/to/game_screenshot.jpg")
print(f"最终行动：{action}")
```

---

## 🧪 命令行测试

### 测试图片识别

```bash
cd /home/xzc/.openclaw/workspace/skills/mahjong-vision
python mahjong_e2e.py /path/to/test_image.jpg
```

### 测试手牌列表

```bash
python mahjong_e2e.py
# 按提示输入手牌，或直接回车使用测试手牌
```

### 单独测试视觉模块

```bash
python mahjong_vision.py /path/to/test_image.jpg
```

### 单独测试战术引擎

```bash
python strategy_api.py
```

---

## 📖 术语对照表

| 代号 | 中文 | 英文 |
|------|------|------|
| 1C-9C | 一万 - 九万 | 1-9 Characters |
| 1B-9B | 一条 - 九条 | 1-9 Bamboos |
| 1D-9D | 一筒 - 九筒 | 1-9 Dots |

---

## ⚠️ 注意事项

1. **图片格式**: 支持 JPG、PNG 等常见格式
2. **手牌数量**: 标准手牌为 13 张（准备打出时）或 14 张（胡牌检查）
3. **检测阈值**: 视觉识别默认置信度阈值 0.5
4. **模型路径**: 确保模型文件存在于指定路径
5. **依赖安装**: 
   ```bash
   pip install ultralytics torch opencv-python
   ```

---

## 🔧 扩展建议

- 添加 ROI 区域检测，专门识别手牌区
- 集成牌局历史记录（已打出的牌）
- 添加多人牌桌识别
- 支持特殊规则（捉鸡、杠上开花等）
- 添加防守策略计算（危险牌检测）

---

## 📝 版本信息

- 视觉模型：yolov8x_v7_rotated_clean
- 战术引擎：v1.0 (简化版向听数计算)
- 更新日期：2026-03-27
