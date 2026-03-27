#!/usr/bin/env python3
"""
Mahjong End-to-End Skill - 麻将端到端决策技能
整合视觉识别 + 战术决策，实现从看图到出牌的完整流程
"""

import os
import sys

# 添加当前目录和 strategy 目录到路径，方便导入
_current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _current_dir)
sys.path.insert(0, os.path.join(_current_dir, 'strategy'))

from mahjong_vision import MahjongVisionAgent
from strategy.main import MahjongStrategyEngine


class MahjongEndToEndAgent:
    """
    麻将端到端智能代理 (纯净静默版 API)
    
    完整工作流：
    1. 视觉识别牌桌图片
    2. 战术大脑分析手牌
    3. 输出最终决策建议
    """
    
    # 术语映射表
    TILE_NAME_MAP = {
        '1c': '一万', '2c': '二万', '3c': '三万', '4c': '四万', '5c': '五万',
        '6c': '六万', '7c': '七万', '8c': '八万', '9c': '九万',
        '1b': '一条', '2b': '二条', '3b': '三条', '4b': '四条', '5b': '五条',
        '6b': '六条', '7b': '七条', '8b': '八条', '9b': '九条',
        '1d': '一筒', '2d': '二筒', '3d': '三筒', '4d': '四筒', '5d': '五筒',
        '6d': '六筒', '7d': '七筒', '8d': '八筒', '9d': '九筒',
    }
    
    def __init__(self, model_path=None):
        """初始化端到端代理（无打印干扰）"""
        self.vision = MahjongVisionAgent(model_path)
        self.strategy = MahjongStrategyEngine()
    
    def process_image(self, image_path: str, use_chinese: bool = True) -> dict:
        """
        处理牌桌图片，输出完整决策
        """
        result = {
            "image_path": image_path,
            "vision_result": None,
            "strategy_result": None,
            "final_decision": None,
            "llm_prompt": ""
        }
        
        # 步骤 1: 视觉识别
        if not os.path.exists(image_path):
            result["vision_result"] = {"error": f"图片文件不存在：{image_path}"}
            result["final_decision"] = f"错误：找不到图片文件 {image_path}"
            return result
        
        vision_result = self.vision.analyze_scene(image_path, use_chinese=False)
        result["vision_result"] = vision_result
        
        if vision_result['total_tiles'] == 0:
            result["final_decision"] = "未检测到麻将牌，无法决策"
            return result
        
        # 步骤 2: 战术分析
        hand_tiles = [tile['name'] for tile in vision_result['tiles']]
        strategy_result = self.strategy.evaluate_hand(hand_tiles)
        result["strategy_result"] = strategy_result
        
        # 步骤 3: 构建 LLM Prompt
        if use_chinese:
            vision_summary_cn = vision_result.get('summary_chinese') or vision_result['raw_text_summary']
            strategy_summary = strategy_result['raw_text_summary']
            
            llm_prompt = f"""
🀄 麻将决策请求

【视觉识别结果】
{vision_summary_cn}

【战术分析结果】
{strategy_summary}

【手牌详情】
代号：{', '.join(hand_tiles)}

请根据以上信息，输出最终行动决策。
格式：Action: Discard [牌名]
理由：[简要说明]
"""
        else:
            llm_prompt = f"""
🀄 Mahjong Decision Request

【Vision Result】
{vision_result['raw_text_summary']}

【Strategy Analysis】
{strategy_result['raw_text_summary']}

【Hand Details】
Tiles: {', '.join(hand_tiles)}

Please output your final action decision.
Format: Action: Discard [tile]
Reason: [brief explanation]
"""
        
        result["llm_prompt"] = llm_prompt
        
        # 生成最终决策建议
        if strategy_result['recommendations']:
            best_rec = strategy_result['recommendations'][0]
            discard = best_rec['discard']
            discard_cn = self.TILE_NAME_MAP.get(discard.lower(), discard)
            result["final_decision"] = (
                f"建议打出：{discard_cn} ({discard})\n"
                f"理由：{strategy_result['raw_text_summary']}"
            )
        else:
            result["final_decision"] = strategy_result['raw_text_summary']
        
        return result
    
    def quick_decision(self, hand_tiles: list[str], use_chinese: bool = True) -> str:
        """
        快速决策（跳过视觉识别，直接分析手牌）
        """
        strategy_result = self.strategy.evaluate_hand(hand_tiles)
        
        if use_chinese:
            output = f"📊 手牌状态：{strategy_result['status']}\n\n"
            output += f"📝 {strategy_result['raw_text_summary']}\n"
            
            if strategy_result['recommendations']:
                best = strategy_result['recommendations'][0]
                discard_cn = self.vision._translate_to_chinese(best['discard'])
                output += f"\n🎯 建议打出：{discard_cn} ({best['discard']})"
        else:
            output = f"Status: {strategy_result['status']}\n"
            output += strategy_result['raw_text_summary']
        
        return output


# ==========================================
# 命令行测试入口 (人类测试时依然保留 print)
# ==========================================
if __name__ == "__main__":
    print("🀄 麻将端到端决策技能 - 测试模式\n")
    print("=" * 60)
    
    # 初始化代理
    agent = MahjongEndToEndAgent()
    
    # 测试模式选择
    if len(sys.argv) > 1:
        # 图片模式
        image_path = sys.argv[1]
        print(f"\n📷 处理图片：{image_path}\n")
        result = agent.process_image(image_path, use_chinese=True)
        
        print("\n" + "=" * 60)
        print("📋 完整决策报告:\n")
        print(result["final_decision"])
        print("\n" + "=" * 60)
        if result["llm_prompt"]:
            print("\n🤖 LLM Prompt (可直接发送给大模型):")
            print(result["llm_prompt"])
    else:
        # 手牌列表模式
        print("📋 请输入手牌 (空格分隔，如：1C 2C 3C 7C 8C 9C 2B 2B 5B 5B 5B 2B 3D)")
        print("或直接按 Enter 使用测试手牌\n")
        
        user_input = input("手牌：").strip()
        
        if user_input:
            test_hand = user_input.split()
        else:
            test_hand = ['1C', '2C', '3C', '7C', '8C', '9C', '2B', '2B', '5B', '5B', '5B', '2B', '3D']
        
        print(f"\n测试手牌：{test_hand}")
        result = agent.quick_decision(test_hand, use_chinese=True)
        print("\n" + "=" * 60)
        print(result)
        print("=" * 60)
