class Darts {
    int score(double xOfDart, double yOfDart) {
        double distance = Math.sqrt(xOfDart * xOfDart + yOfDart * yOfDart);

        if (distance <= 1) return 10;
        if (distance <= 5) return 5;
        if (distance <= 10) return 1;
        return 0;
    }
}