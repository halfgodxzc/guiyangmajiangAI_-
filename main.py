import judge_hu
import check_ting
import tile_mapper
import best_discard

def main():
    print("="*40)
    print("      🚀 贵阳麻将视觉与牌理分析系统      ")
    print("="*40)

    # ---------------------------------------------------------
    # 【一向听测试用例】
    # 这是一副很典型的没听牌，但快听了的牌：
    # 123万(顺), 456条(顺), 789筒(顺)
    # 剩下：1万、2万 (缺3万)、5万、7万 (两个废牌单张)
    # ---------------------------------------------------------
    mock_yolo_output = ['1w', '2w', '3w', '7w', '8w', '9w', '2t', '2t', '5t', '5t', '8t', '8t', '3b', '4b']
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
        # 步骤 B: 检查是否听牌 (打出某张直接听)
        best_strategies = best_discard.get_best_discards(mapped_tiles, table)

        if best_strategies:
            print("👀 [结论]：您目前是 【听牌状态】！")
            print("\n💡 [AI 推荐打法 (直接听牌)]：")
            for discard_idx, ting_indices in best_strategies:
                discard_name = mapper.get_name(discard_idx)
                ting_names = [mapper.get_name(idx) for idx in ting_indices]
                print(f"   👉 打出 【{discard_name}】，可听 {len(ting_names)} 张牌: {ting_names}")
        
        else:
            # 步骤 C: 进入 一向听 深度预测！
            print("⏳ [结论]：还没听牌，AI 正在为您推演未来一向听走势 (可能需要零点几秒)...")
            shanten_1_strategies = best_discard.get_1_shanten_discards(mapped_tiles, table)
            
            if shanten_1_strategies:
                print("🧠 [结论]：您目前处于 【一向听状态】！")
                print("\n💡 [AI 远见推荐 (最大化进张)]：")
                for discard_idx, effective_draws in shanten_1_strategies:
                    discard_name = mapper.get_name(discard_idx)
                    draw_names = [mapper.get_name(idx) for idx in effective_draws]
                    print(f"   👉 打出 【{discard_name}】，未来如果摸到这 {len(draw_names)} 张牌任意一张，即可听牌：")
                    print(f"      进张列表: {draw_names}")
            else:
                print("❌ [结论]：手牌太烂了 (两向听以上)，AI 建议立刻放弃做大牌，安全防守！")

    print("\n" + "="*40)

if __name__ == "__main__":
    main()
