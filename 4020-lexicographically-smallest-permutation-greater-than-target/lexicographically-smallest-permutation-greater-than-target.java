class Solution {
    public String lexGreaterPermutation(String s, String target) {
        int n = s.length();

        int[] count = new int[26];

        for (char c : s.toCharArray()) {
            count[c - 'a']++;
        }

        // Try to keep the prefix equal to target
        for (int i = 0; i < n; i++) {

            int x = target.charAt(i) - 'a';

            // Can we use target[i]?
            if (count[x] > 0) {
                count[x]--;
                continue;
            }

            // Cannot match target[i].
            // Try to make this position bigger.
            for (int c = x + 1; c < 26; c++) {

                if (count[c] > 0) {
                    count[c]--;

                    return buildAnswer(target, i, c, count);
                }
            }

            // Can't make current position bigger.
            // Backtrack to an earlier position.
            for (int j = i - 1; j >= 0; j--) {

                int prev = target.charAt(j) - 'a';

                count[prev]++;

                for (int c = prev + 1; c < 26; c++) {

                    if (count[c] > 0) {
                        count[c]--;

                        return buildAnswer(target, j, c, count);
                    }
                }
            }

            return "";
        }

        // s can form target exactly.
        // Need STRICTLY greater, so backtrack.
        for (int i = n - 1; i >= 0; i--) {

            int x = target.charAt(i) - 'a';

            count[x]++;

            for (int c = x + 1; c < 26; c++) {

                if (count[c] > 0) {
                    count[c]--;

                    return buildAnswer(target, i, c, count);
                }
            }
        }

        return "";
    }

    private String buildAnswer(String target, int index,
                               int bigger, int[] count) {

        StringBuilder ans = new StringBuilder();

        // Prefix stays equal to target
        ans.append(target, 0, index);

        // Make this character bigger
        ans.append((char) ('a' + bigger));

        // Smallest possible suffix
        for (int i = 0; i < 26; i++) {
            while (count[i] > 0) {
                ans.append((char) ('a' + i));
                count[i]--;
            }
        }

        return ans.toString();
    }
}