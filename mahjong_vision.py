#!/usr/bin/env python3
"""
Mahjong Vision Skill - 麻将视觉识别模块
让 OpenClaw 能够看懂麻将牌桌局势

术语对齐：
- C = 万 (Characters/Wan)
- B = 条/索 (Bamboos/Suo)  
- D = 筒 (Dots/Tong)
"""

from ultralytics import YOLO
import os

# 模型路径配置
MODEL_PATH = "/mnt/145495b6-a8d0-425a-938b-a42e4ea063b1/majiangProject/cv/runs/detect/majiang_runs_guiyang/yolov8x_v7_rotated_clean/weights/best.pt"

# 术语映射表：代号 -> 中文名称
TILE_NAME_MAP = {
    # 万子 (C = Characters/Wan)
    "1C": "一万", "2C": "二万", "3C": "三万", "4C": "四万", "5C": "五万",
    "6C": "六万", "7C": "七万", "8C": "八万", "9C": "九万",
    
    # 条子/索子 (B = Bamboos/Suo)
    "1B": "一条", "2B": "二条", "3B": "三条", "4B": "四条", "5B": "五条",
    "6B": "六条", "7B": "七条", "8B": "八条", "9B": "九条",
    
    # 筒子 (D = Dots/Tong)
    "1D": "一筒", "2D": "二筒", "3D": "三筒", "4D": "四筒", "5D": "五筒",
    "6D": "六筒", "7D": "七筒", "8D": "八筒", "9D": "九筒",
    
    # 字牌 (如有需要可扩展)
    "EAST": "东风", "SOUTH": "南风", "WEST": "西风", "NORTH": "北风",
    "RED": "红中", "GREEN": "发财", "WHITE": "白板"
}


class MahjongVisionAgent:
    """
    麻将视觉感知代理
    
    作为 OpenClaw 的 Tool/Skill 使用，提供麻将牌桌的视觉分析能力。
    
    术语说明:
    - 内部使用代号：1C, 2C, 3C... (C=万，B=条，D=筒)
    - 输出可翻译为中文：一万，二万，三万...
    """
    
    def __init__(self, model_path=None):
        """
        初始化视觉感知模块
        
        Args:
            model_path: 可选的自定义模型路径，默认使用内置路径
        """
        path = model_path or MODEL_PATH
        print(f"👁️  麻将视觉模块初始化，加载模型：{path} ...")
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"模型文件不存在：{path}")
        
        self.model = YOLO(path)
        print("✅ 麻将视觉模块就绪，等待 OpenClaw 召唤！")
    
    def translate_tile_name(self, code_name):
        """
        将代号翻译为中文名称
        
        Args:
            code_name: 代号，如 "1C", "5B", "9D"
            
        Returns:
            str: 中文名称，如 "一万", "五条", "九筒"
        """
        return TILE_NAME_MAP.get(code_name, code_name)
    
    def translate_to_chinese(self, tile_list):
        """
        将代号列表翻译为中文列表
        
        Args:
            tile_list: 代号列表，如 ["1C", "2C", "3C"]
            
        Returns:
            list: 中文名称列表，如 ["一万", "二万", "三万"]
        """
        return [self.translate_tile_name(tile) for tile in tile_list]
    
    def analyze_scene(self, image_source, use_chinese=False):
        """
        分析麻将牌桌图片，识别所有麻将牌
        
        Args:
            image_source: 图片文件路径
            use_chinese: 是否使用中文输出（默认 False，使用代号）
            
        Returns:
            dict: 包含以下字段的结构化数据:
                - total_tiles: 检测到的牌总数
                - tiles: 每张牌的详细信息列表
                - raw_text_summary: 自然语言摘要（专为 LLM 设计）
                - summary_chinese: 中文摘要（当 use_chinese=True 时填充）
        """
        if not os.path.exists(image_source):
            return {
                "total_tiles": 0,
                "tiles": [],
                "raw_text_summary": f"图片文件不存在：{image_source}"
            }
        
        # 执行 YOLO 检测
        results = self.model.predict(
            source=image_source,
            save=False,
            conf=0.2,
            iou=0.5,
            verbose=False
        )
        
        scene_data = {
            "total_tiles": 0,
            "tiles": [],
            "raw_text_summary": ""
        }
        
        # 处理检测结果
        if not results or len(results[0].boxes) == 0:
            scene_data["raw_text_summary"] = "画面中未检测到任何麻将牌。"
            return scene_data
        
        boxes = results[0].boxes
        scene_data["total_tiles"] = len(boxes)
        
        # 提取每张牌的信息
        temp_tiles = []
        for box in boxes:
            cls_name = self.model.names[int(box.cls[0])]
            conf = float(box.conf[0])
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            
            temp_tiles.append({
                "name": cls_name,
                "confidence": round(conf, 3),
                "box": [int(x1), int(y1), int(x2), int(y2)],
                "center_x": (x1 + x2) / 2.0,
                "center_y": (y1 + y2) / 2.0
            })
        
        # 🧮 核心逻辑：按 X 坐标从左到右排序（模拟理牌）
        sorted_tiles = sorted(temp_tiles, key=lambda t: t["center_x"])
        scene_data["tiles"] = sorted_tiles
        
        # 📝 生成 LLM 友好的自然语言描述（代号格式，内部使用）
        tile_names_ordered = [t["name"] for t in sorted_tiles]
        scene_data["raw_text_summary"] = (
            f"画面中共检测到 {len(boxes)} 张牌。"
            f"从左到右依次为：{', '.join(tile_names_ordered)}。"
        )
        
        # 🀄 生成中文摘要（给用户看）
        if use_chinese:
            tile_names_chinese = self.translate_to_chinese(tile_names_ordered)
            scene_data["summary_chinese"] = (
                f"画面中共检测到 {len(boxes)} 张牌。"
                f"从左到右依次为：{', '.join(tile_names_chinese)}。"
            )
            # 同时翻译 tiles 列表中的 name 字段
            for tile in scene_data["tiles"]:
                tile["name_chinese"] = self.translate_tile_name(tile["name"])
        else:
            scene_data["summary_chinese"] = None
        
        return scene_data
    
    def detect_hand_tiles(self, image_source, expected_count=13, use_chinese=False):
        """
        专门检测手牌区域（可选扩展功能）
        
        Args:
            image_source: 图片文件路径
            expected_count: 期望的手牌数量（默认 13 张）
            use_chinese: 是否使用中文输出
            
        Returns:
            dict: 手牌信息，格式同 analyze_scene
        """
        # 当前实现与 analyze_scene 相同
        # 未来可以添加 ROI 裁剪等优化
        return self.analyze_scene(image_source, use_chinese=use_chinese)


# ==========================================
# 命令行测试入口
# ==========================================
if __name__ == "__main__":
    import sys
    
    print("🀄 麻将视觉识别技能 - 测试模式\n")
    print("📖 术语对齐说明：")
    print("   C = 万 (Characters/Wan)")
    print("   B = 条/索 (Bamboos/Suo)")
    print("   D = 筒 (Dots/Tong)")
    print()
    
    # 初始化
    vision_tool = MahjongVisionAgent()
    
    # 测试图片
    test_image = sys.argv[1] if len(sys.argv) > 1 else "test.png"
    
    if not os.path.exists(test_image):
        print(f"❌ 测试图片不存在：{test_image}")
        print("用法：python mahjong_vision.py <图片路径>")
        sys.exit(1)
    
    # 执行检测
    print(f"\n📷 分析图片：{test_image}")
    observation = vision_tool.analyze_scene(test_image, use_chinese=True)
    
    # 输出结果
    print("\n🤖 视觉观测数据：")
    print(f"   总牌数：{observation['total_tiles']}")
    print(f"   代号摘要 (内部使用): {observation['raw_text_summary']}")
    print(f"   中文摘要 (给用户看): {observation['summary_chinese']}")
    
    if observation['tiles']:
        print("\n📋 详细牌列表:")
        for i, tile in enumerate(observation['tiles'], 1):
            code = tile['name']
            chinese = tile.get('name_chinese', code)
            conf = tile['confidence']
            print(f"   {i}. {code} → {chinese} (置信度：{conf:.2f})")
