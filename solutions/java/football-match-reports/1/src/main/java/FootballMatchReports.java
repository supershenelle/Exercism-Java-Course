public class FootballMatchReports {    
    public static String onField(int shirtNum) {
        String ans = " ";
        switch (shirtNum)
            {
                case 1:
                    ans = "goalie";
                    break;
                case 2:
                    ans = "left back";
                    break;
                case 3, 4:
                    ans = "center back";
                    break;
                case 5:
                    ans = "right back";
                    break;
                case 6, 7, 8:
                    ans = "midfielder";
                    break;
                case 9:
                    ans = "left wing";
                    break;
                case 10:
                    ans = "striker";
                    break;
                case 11:
                    ans = "right wing";
                    break;

                default:
                    ans = "invalid";
                    break;
            }
        return ans;
    }
}
