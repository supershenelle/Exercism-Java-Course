class ProductionRemoteControlCar implements RemoteControlCar, Comparable<ProductionRemoteControlCar> {
    private int distance = 0;
    private int numberOfVictories = 0;
    
    public void drive() {
        distance = distance + 10;
    }

    public int getDistanceTravelled() {
        return distance;
    }

    public int getNumberOfVictories() {
        return numberOfVictories;
    }

    public void setNumberOfVictories(int numberOfVictories) {
        this.numberOfVictories = numberOfVictories;
    }

    @Override
    public int compareTo(ProductionRemoteControlCar other) {
        return Integer.compare(other.getNumberOfVictories(), this.numberOfVictories);
    }
}
