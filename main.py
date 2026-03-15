import judge_hu
import check_ting
import tile_mapper
import best_discard
import draw_calculator  # 导入你的新模块
import analyzer_unit

def main():
    print("="*50)
    print("      🚀 贵阳麻将视觉与牌理 AI 决策系统      ")
    print("="*50)

    # ---------------------------------------------------------
    # 【测试用例】
    # 你可以随时换成极度烂牌，看看多向听引擎的威力！
    # ---------------------------------------------------------
    mock_yolo_output = ['1c', '2c', '3c', '5c', '8c', '9c', '2b', '2b', '5b', '5b', '8b', '6b', '3d', '9d']
    print(f"📷 [YOLO端] 摸牌后总计14张: {mock_yolo_output}")

    mapper = tile_mapper.TileMapper()
    mapped_tiles = mapper.yolo_to_array(mock_yolo_output)
    
    human_readable_hand = mapper.array_to_names(mapped_tiles)
    print(f"🔄 [准备就绪] 逻辑手牌: {human_readable_hand}\n")
    print("--- 正在进行牌理分析 ---")

    table = judge_hu.MahjongTable()

    # 步骤 A: 检查是否直接胡牌
    if table.can_hu(mapped_tiles):
        print("🎉 [结论]：太棒了，直接胡牌！")
    else:
        # 步骤 B: 检查是否听牌 (打出某张直接听，0向听)
        best_strategies = best_discard.get_best_discards(mapped_tiles, table)

        if best_strategies:
            print("👀 [状态]：当前为 【听牌状态 (0向听)】")
            print("\n💡 [AI 终局推荐 (直接听牌)]：")
            for discard_idx, ting_indices in best_strategies:
                discard_name = mapper.get_name(discard_idx)
                ting_names = [mapper.get_name(idx) for idx in ting_indices]
                print(f"   👉 打出 【{discard_name}】，可听 {len(ting_names)} 张牌: {ting_names}")
        
        else:
            # 步骤 C: 进入 一向听 深度预测 (使用极速查表法穷举)
            shanten_1_strategies = best_discard.get_1_shanten_discards(mapped_tiles, table)
            
            if shanten_1_strategies:
                print("🧠 [状态]：当前处于 【一向听状态】")
                print("\n💡 [AI 远见推荐 (最大化进张直达听牌)]：")
                for discard_idx, effective_draws in shanten_1_strategies:
                    discard_name = mapper.get_name(discard_idx)
                    draw_names = [mapper.get_name(idx) for idx in effective_draws]
                    print(f"   👉 打出 【{discard_name}】，未来摸到以下 {len(draw_names)} 张牌即可听牌：")
                    print(f"      进张列表: {draw_names}")
            else:
                # 步骤 D: 一向听也没戏，启动多向听宏观公式引擎！
                print("⏳ [状态]：手牌在两向听及以上，启动多向听宏观策略引擎...")
                
                # 实例化单花色分析器和向听数计算器
                suit_analyzer = analyzer_unit.SingleSuitAnalyzer()
                shanten_calc = draw_calculator.ShantenCalculator(suit_analyzer)
                
                # 调用终极多向听策略
                multi_shanten_strategies = best_discard.get_ultimate_best_discards(mapped_tiles, shanten_calc)
                
                if multi_shanten_strategies:
                    print("🌌 [结论]：为您规划出最优的降维做牌路径！")
                    print("\n💡 [AI 宏观策略 (最大化牌型改良)]：")
                    for discard_idx, effective_dict, total_count in multi_shanten_strategies:
                        discard_name = mapper.get_name(discard_idx)
                        # 将字典里的 (进张牌索引: 剩余张数) 翻译成人类可读的格式
                        draw_details = [f"{mapper.get_name(idx)}(余{count}张)" for idx, count in effective_dict.items()]
                        
                        print(f"   👉 战略性打出 【{discard_name}】，将迎来 {len(effective_dict)} 种改良牌 (共计 {total_count} 张进张机会)")
                        print(f"      改良目标: {', '.join(draw_details)}")
                else:
                    print("❌ [结论]：手牌毫无逻辑可言，建议直接放弃进攻，死守防守！")

    print("\n" + "="*50)

if __name__ == "__main__":
    main()
