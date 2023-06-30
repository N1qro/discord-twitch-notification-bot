from typing import List
from collections import defaultdict
from itertools import pairwise


class Solution:
    def maxProfit(self, prices: List[int], fee: int) -> int:
        total = 0
        for price1, price2 in pairwise(prices):
            if price2 > price1 + fee:
                total += price2 - price1 - fee
                print(price1, price2, total)

        return total


prices = [1, 3, 2, 8, 4, 9]
fee = 2

sol = Solution()
print(sol.maxProfit(prices, fee))