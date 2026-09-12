class Solution {
    struct State {
        long long score = 0;
        vector<int> ids;
    };

    int n;
    vector<vector<int>> a;
    vector<int> nxt;
    vector<vector<State>> dp;
    vector<vector<bool>> seen;

    bool better(const State& x, const State& y) {
        if (x.score != y.score)
            return x.score > y.score;

        return lexicographical_compare(
            x.ids.begin(), x.ids.end(),
            y.ids.begin(), y.ids.end()
        );
    }

    State solve(int i, int k) {
        if (i == n || k == 0)
            return {0, {}};

        if (seen[i][k])
            return dp[i][k];

        seen[i][k] = true;

        // Don't take interval i
        State best = solve(i + 1, k);

        // Take interval i
        State take = solve(nxt[i], k - 1);
        take.score += a[i][2];
        take.ids.push_back(a[i][3]);

        sort(take.ids.begin(), take.ids.end());

        if (better(take, best))
            best = take;

        return dp[i][k] = best;
    }

public:
    vector<int> maximumWeight(vector<vector<int>>& intervals) {
        n = intervals.size();

        // Add original index
        a.clear();
        for (int i = 0; i < n; ++i) {
            a.push_back({
                intervals[i][0],
                intervals[i][1],
                intervals[i][2],
                i
            });
        }

        // Sort by left endpoint
        sort(a.begin(), a.end(), [](const vector<int>& x,
                                    const vector<int>& y) {
            if (x[0] != y[0])
                return x[0] < y[0];
            return x[1] < y[1];
        });

        // Find first interval with left > current right
        nxt.assign(n, n);

        vector<int> starts(n);
        for (int i = 0; i < n; ++i)
            starts[i] = a[i][0];

        for (int i = 0; i < n; ++i) {
            nxt[i] = upper_bound(
                starts.begin(),
                starts.end(),
                a[i][1]
            ) - starts.begin();
        }

        dp.assign(n, vector<State>(5));
        seen.assign(n, vector<bool>(5, false));

        return solve(0, 4).ids;
    }
};