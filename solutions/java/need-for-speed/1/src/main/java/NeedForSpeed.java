class NeedForSpeed {
    private int speed;
    private int batteryDrain;
    private int meters;
    private int batteryCharge = 100;
    
    public NeedForSpeed(int speed, int batteryDrain) {
        this.speed = speed;
        this.batteryDrain = batteryDrain;
    }

    public boolean batteryDrained() {
        return batteryCharge < batteryDrain;
    }

    public int distanceDriven() {
        return meters;
    }

    public void drive() {
        if (batteryCharge >= batteryDrain)
        {
            this.meters += speed;
            this.batteryCharge -= batteryDrain;
        }
    }

    public static NeedForSpeed nitro() {
        return new NeedForSpeed(50, 4);
    }
}

class RaceTrack {
    private int distance;
    
    RaceTrack(int distance) {
        this.distance = distance;
    }

    public boolean canFinishRace(NeedForSpeed car) {
        while (!car.batteryDrained()) {
        car.drive();
        }
        return car.distanceDriven() >= distance;
    }
}
