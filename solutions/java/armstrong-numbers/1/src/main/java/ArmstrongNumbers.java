class ArmstrongNumbers {

    boolean isArmstrongNumber(int numberToCheck) {
        int digits = 0;
        int temp = numberToCheck;
        int original = numberToCheck;
        int number;
        int sum = 0;
        
        while (temp != 0)
            {
                digits++;
                temp = temp / 10;
            }

        for (int i=0; i<digits; i++)
            {
                number = numberToCheck % 10;
                sum = sum + (int)Math.pow(number, digits);
                numberToCheck = numberToCheck / 10;
            }

        return sum == original;

    }

}
