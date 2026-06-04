public class Lasagna {
    int minutes = 40;
    public int expectedMinutesInOven()
    {
        return minutes;
    }

    public int remainingMinutesInOven(int actualmins)
    {
        return expectedMinutesInOven() - actualmins;
    }

    public int preparationTimeInMinutes(int layers)
    {
        return layers * 2;
    }

    public int totalTimeInMinutes(int layers, int actualmins)
    {
        int prep = preparationTimeInMinutes(layers);
        return prep + actualmins;
    }
}
