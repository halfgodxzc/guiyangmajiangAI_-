class SingleSuitAnalyzer:
    def __init__(self):
        # 缓存字典，避免重复计算相同状态的牌型
        self.memo = {}

    def analyze(self, arr):
        """
        分析单花色数组 (长度为9)，返回最优的 (m, d)
        m: 面子数量 (顺子/刻子)
        d: 搭子数量 (对子/两面/边/嵌)
        """
        # 转成元组才能做字典的 Key
        state = tuple(arr)
        if state in self.memo:
            return self.memo[state]

        best_m = 0
        best_d = 0

        # 找第一个有牌的索引开始拆
        start_idx = -1
        for i in range(9):
            if arr[i] > 0:
                start_idx = i
                break

        # 递归出口：牌都抽光了，或者全是 0 了
        if start_idx == -1:
            return (0, 0)

        # -----------------------------------------------------
        # 核心 DFS 分支：尝试在这个 start_idx 上拔取各种组合
        # -----------------------------------------------------
        
        # 1. 尝试拔刻子 (m)
        if arr[start_idx] >= 3:
            arr[start_idx] -= 3
            sub_m, sub_d = self.analyze(arr)
            best_m, best_d = self._update_best(best_m, best_d, sub_m + 1, sub_d)
            arr[start_idx] += 3
            
        # 2. 尝试拔顺子 (m)
        if start_idx <= 6 and arr[start_idx] > 0 and arr[start_idx+1] > 0 and arr[start_idx+2] > 0:
            arr[start_idx] -= 1
            arr[start_idx+1] -= 1
            arr[start_idx+2] -= 1
            sub_m, sub_d = self.analyze(arr)
            best_m, best_d = self._update_best(best_m, best_d, sub_m + 1, sub_d)
            arr[start_idx] += 1
            arr[start_idx+1] += 1
            arr[start_idx+2] += 1

        # 3. 尝试拔对子搭 (d)
        if arr[start_idx] >= 2:
            arr[start_idx] -= 2
            sub_m, sub_d = self.analyze(arr)
            best_m, best_d = self._update_best(best_m, best_d, sub_m, sub_d + 1)
            arr[start_idx] += 2

        # 4. 尝试拔两面/边搭 (d)
        if start_idx <= 7 and arr[start_idx] > 0 and arr[start_idx+1] > 0:
            arr[start_idx] -= 1
            arr[start_idx+1] -= 1
            sub_m, sub_d = self.analyze(arr)
            best_m, best_d = self._update_best(best_m, best_d, sub_m, sub_d + 1)
            arr[start_idx] += 1
            arr[start_idx+1] += 1

        # 5. 尝试拔嵌搭 (d)
        if start_idx <= 6 and arr[start_idx] > 0 and arr[start_idx+2] > 0:
            arr[start_idx] -= 1
            arr[start_idx+2] -= 1
            sub_m, sub_d = self.analyze(arr)
            best_m, best_d = self._update_best(best_m, best_d, sub_m, sub_d + 1)
            arr[start_idx] += 1
            arr[start_idx+2] += 1

        # 6. 直接把这张牌当废牌丢掉，看剩下的牌能组成什么
        arr[start_idx] -= 1
        sub_m, sub_d = self.analyze(arr)
        best_m, best_d = self._update_best(best_m, best_d, sub_m, sub_d)
        arr[start_idx] += 1

        self.memo[state] = (best_m, best_d)
        return best_m, best_d

    def _update_best(self, cur_m, cur_d, new_m, new_d):
        """
        比大小逻辑：面子 (m) 价值远大于搭子 (d)
        如果 m 更大，直接替换；如果 m 一样大，选 d 更大的。
        """
        if new_m > cur_m:
            return new_m, new_d
        elif new_m == cur_m and new_d > cur_d:
            return new_m, new_d
        return cur_m, cur_d

    def evaluate_suit(self, arr):
        """
        对外接口：计算带将牌 (p=1) 和不带将牌 (p=0) 的两种最高成绩单
        """
        # 1. 假设这组牌里没有将牌 (p=0)
        m0, d0 = self.analyze(list(arr))
        
        # 2. 假设这组牌里提供将牌 (p=1)
        # 遍历找对子，强制拔出当将牌，算剩下的最大 m 和 d
        best_m1, best_d1 = -1, -1
        for i in range(9):
            if arr[i] >= 2:
                arr_copy = list(arr)
                arr_copy[i] -= 2
                m, d = self.analyze(arr_copy)
                if m > best_m1 or (m == best_m1 and d > best_d1):
                    best_m1, best_d1 = m, d
                    
        return {"p0": (m0, d0), "p1": (best_m1, best_d1)}

# ================= 测试代码 =================
if __name__ == "__main__":
    analyzer = SingleSuitAnalyzer()
    
    # 测试人类贪心陷阱：22234 万 (5张牌)
    # 人类可能看成 222 + 34 (m=1, d=1, p=0)
    # 但实际最优是 234 + 22 (m=1, d=0, p=1)
    test_arr = [0, 3, 1, 1, 0, 0, 0, 0, 0] 
    
    result = analyzer.evaluate_suit(test_arr)
    print("测试牌型 [2,2,2,3,4]:")
    print(f"不带将牌的最高战力 (p=0): {result['p0'][0]}个面子, {result['p0'][1]}个搭子")
    print(f"带将牌的最高战力   (p=1): {result['p1'][0]}个面子, {result['p1'][1]}个搭子")
