class Solution:
    def winnerSquareGame(self, n: int) -> bool:
        dp = [False] * (n + 1)

        for i in range(1, n + 1):
            s = 1
            while s * s <= i:
                if not dp[i - s * s]:
                    dp[i] = True
                    break
                s += 1

        return dp[n]