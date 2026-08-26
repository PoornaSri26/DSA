class Solution {
    public String shortestBeautifulSubstring(String s, int k) {
        int n = s.length();
        int left = 0;
        int ones = 0;

        String ans = "";

        for (int right = 0; right < n; right++) {
            if (s.charAt(right) == '1') {
                ones++;
            }

            if (ones == k) {
                // Remove leading zeroes.
                while (left <= right && s.charAt(left) == '0') {
                    left++;
                }

                String curr = s.substring(left, right + 1);

                // Update if shorter or same length but lexicographically smaller.
                if (ans.equals("") ||
                    curr.length() < ans.length() ||
                    (curr.length() == ans.length() && curr.compareTo(ans) < 0)) {
                    ans = curr;
                }

                // Remove the first '1' to search for the next window.
                left++;
                ones--;
            }
        }

        return ans;
    }
}