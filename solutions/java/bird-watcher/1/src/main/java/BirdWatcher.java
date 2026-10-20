
class BirdWatcher {
    private final int[] birdsPerDay;

    public BirdWatcher(int[] birdsPerDay) {
        this.birdsPerDay = birdsPerDay.clone();
    }

    public int[] getLastWeek() {
        return new int[] {0, 2, 5, 3, 7, 8, 4};
    }

    public int getToday() {
        return birdsPerDay[birdsPerDay.length-1];
    }

    public void incrementTodaysCount() {
        birdsPerDay[birdsPerDay.length-1] += 1;
    }

    public boolean hasDayWithoutBirds() {
        boolean bool = false;
        for (int i=0; i<birdsPerDay.length; i++)
            {
                if (birdsPerDay[i] == 0)
                    bool = true;
            }
        return bool;
    }

    public int getCountForFirstDays(int numberOfDays) {
        int count = 0;

        if (numberOfDays > birdsPerDay.length)
            numberOfDays = birdsPerDay.length;
        
        for (int i=1; i<numberOfDays; i++)
            {
                count += birdsPerDay[i];
            }
        return count;
    }

    public int getBusyDays() {
        int count = 0;

        for (int i=0; i<birdsPerDay.length; i++)
            {
                if (birdsPerDay[i]>=5)
                    count++;
            }
        return count;
    }
}
