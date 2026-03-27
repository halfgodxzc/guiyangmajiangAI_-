import judge_hu
import check_ting
import tile_mapper
import best_discard
import draw_calculator  
import analyzer_unit

class MahjongStrategyEngine:
    def __init__(self):
        """
        初始化麻将战术大脑。在 Agent 启动时只加载一次，避免重复实例化。
        """
        print("⚙️ [战术中枢] 正在加载规则库、查表引擎与分析器...")
        self.mapper = tile_mapper.TileMapper()
        self.table = judge_hu.MahjongTable()
        self.suit_analyzer = analyzer_unit.SingleSuitAnalyzer()
        self.shanten_calc = draw_calculator.ShantenCalculator(self.suit_analyzer)
        print("✅ [战术中枢] 初始化完毕，随时准备推演！")

    def evaluate_hand(self, yolo_tiles_list):
        """
        给 Agent 调用的核心策略接口。
        :param yolo_tiles_list: 视觉模块传来的手牌列表，例如 ['1C', '2C', '3C'...]
        :return: 包含当前状态、推荐打法、以及供 LLM 阅读的摘要文本的字典
        """
        yolo_tiles_list = [tile.lower() for tile in yolo_tiles_list]
        # 将视觉层的字符串列表转为算法层的底层数组
        mapped_tiles = self.mapper.yolo_to_array(yolo_tiles_list)
        human_readable_hand = self.mapper.array_to_names(mapped_tiles)

        # 初始化标准返回结构
        decision_data = {
            "hand": human_readable_hand,  # 当前逻辑手牌
            "status": "",                 # 状态标识 (HU, TING, 1_SHANTEN, N_SHANTEN, DEFEND)
            "recommendations": [],        # 结构化的推荐策略列表
            "raw_text_summary": ""        # 💡 最关键的字段：喂给大语言模型的纯文本战术报告
        }

        # -----------------------------------------
        # 步骤 A: 检查是否直接胡牌
        # -----------------------------------------
        if self.table.can_hu(mapped_tiles):
            decision_data["status"] = "HU"
            decision_data["raw_text_summary"] = "🎉 恭喜！当前手牌已直接满足胡牌条件，请立刻执行【胡牌】动作！"
            return decision_data

        # -----------------------------------------
        # 步骤 B: 检查是否听牌 (0向听)
        # -----------------------------------------
        best_strategies = best_discard.get_best_discards(mapped_tiles, self.table)
        if best_strategies:
            decision_data["status"] = "TING"
            summary_lines = ["当前处于【已听牌】状态！建议出牌及对应听牌如下："]
            
            for discard_idx, ting_indices in best_strategies:
                discard_name = self.mapper.get_name(discard_idx)
                ting_names = [self.mapper.get_name(idx) for idx in ting_indices]
                
                # 记录结构化数据供程序备用
                decision_data["recommendations"].append({
                    "discard": discard_name,
                    "target_tiles": ting_names,
                    "target_count": len(ting_names)
                })
                # 生成自然语言报告
                summary_lines.append(f"- 优先打出【{discard_name}】，可听 {len(ting_names)} 张牌: {', '.join(ting_names)}。")
            
            decision_data["raw_text_summary"] = "\n".join(summary_lines)
            return decision_data

        # -----------------------------------------
        # 步骤 C: 检查一向听 (差一张听牌)
        # -----------------------------------------
        shanten_1_strategies = best_discard.get_1_shanten_discards(mapped_tiles, self.table)
        if shanten_1_strategies:
            decision_data["status"] = "1_SHANTEN"
            summary_lines = ["当前处于【一向听】状态。建议最大化进张策略如下："]
            
            for discard_idx, effective_draws in shanten_1_strategies:
                discard_name = self.mapper.get_name(discard_idx)
                draw_names = [self.mapper.get_name(idx) for idx in effective_draws]
                
                decision_data["recommendations"].append({
                    "discard": discard_name,
                    "target_tiles": draw_names,
                    "target_count": len(draw_names)
                })
                summary_lines.append(f"- 战略打出【{discard_name}】，未来摸到这 {len(draw_names)} 张牌即可听牌: {', '.join(draw_names)}。")
                
            decision_data["raw_text_summary"] = "\n".join(summary_lines)
            return decision_data

        # -----------------------------------------
        # 步骤 D: 启动多向听宏观引擎 (较烂的牌)
        # -----------------------------------------
        multi_shanten_strategies = best_discard.get_ultimate_best_discards(mapped_tiles, self.shanten_calc)
        if multi_shanten_strategies:
            decision_data["status"] = "N_SHANTEN"
            summary_lines = ["当前手牌距离听牌较远(两向听及以上)。已启动宏观改良策略："]
            
            for discard_idx, effective_dict, total_count in multi_shanten_strategies:
                discard_name = self.mapper.get_name(discard_idx)
                
                draw_details_str = ", ".join([f"{self.mapper.get_name(idx)}(余{count}张)" for idx, count in effective_dict.items()])
                draw_names_list = [self.mapper.get_name(idx) for idx in effective_dict.keys()]
                
                decision_data["recommendations"].append({
                    "discard": discard_name,
                    "target_tiles": draw_names_list,
                    "target_count": total_count
                })
                summary_lines.append(f"- 建议打出【{discard_name}】，将迎来 {len(effective_dict)} 种改良牌 (共计 {total_count} 张进张机会)，改良目标: {draw_details_str}。")

            decision_data["raw_text_summary"] = "\n".join(summary_lines)
            return decision_data

        # -----------------------------------------
        # 步骤 E: 极端死牌兜底
        # -----------------------------------------
        decision_data["status"] = "DEFEND"
        decision_data["raw_text_summary"] = "⚠️ 当前手牌毫无进攻逻辑，建议放弃做牌，直接观察牌河死守防守！"
        return decision_data


# ==========================================
# OpenClaw (Agent) 主逻辑调用示范
# ==========================================
if __name__ == "__main__":
    # 1. 启动时初始化引擎
    engine = MahjongStrategyEngine()
    
    # 2. 模拟从你的 YOLO 视觉接口拿到的手牌
    # 这里直接对接上一节的 vision_tool.analyze_scene() 的输出
    vision_tiles = ['1C', '2C', '3C', '7C', '8C', '9C', '2B', '2B', '5B', '5B', '5B', '2B', '3D', '4D']
    
    # 3. 让引擎开始思考
    print("\n🤔 Agent 正在请求战术分析...")
    advice = engine.evaluate_hand(vision_tiles)
    
    # 4. Agent 直接拿到的数据格式
    print("\n🤖 [Agent 拿到的结构化报告]：")
    print(f"状态: {advice['status']}")
    
    print("\n📝 [喂给 LLM 的提示词文本]：")
    print(advice['raw_text_summary'])
