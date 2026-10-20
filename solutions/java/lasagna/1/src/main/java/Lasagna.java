public class Lasagna {
    int minutes = 40;
    // TODO: define the 'expectedMinutesInOven()' method
    public int expectedMinutesInOven()
    {
        return minutes;
    }

    // TODO: define the 'remainingMinutesInOven()' method
    public int remainingMinutesInOven(int actualmins)
    {
        return minutes - actualmins;
    }

    // TODO: define the 'preparationTimeInMinutes()' method
    public int preparationTimeInMinutes(int layers)
    {
        return layers * 2;
    }

    // TODO: define the 'totalTimeInMinutes()' method
    public int totalTimeInMinutes(int layers, int actualmins)
    {
        int prep = preparationTimeInMinutes(layers);
        return prep + actualmins;
    }
}
