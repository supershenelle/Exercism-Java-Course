public class CarsAssemble {

    public double productionRatePerHour(int speed) {
        int prod = speed * 221;
        double success = 1;

        if (speed >= 5 && speed <=8)
            success = 0.9;

        else if (speed == 9)
            success = 0.8;

        else if (speed == 10)
            success = 0.77;

        return prod * success;
    }

    public int workingItemsPerMinute(int speed) {
        return (int) productionRatePerHour(speed) / 60;
    }
}
