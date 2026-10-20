class CalculatorConundrum {
    public String calculate(int operand1, int operand2, String operation) {
        int ans = 0;
        int exception = 0;

        if (operation == null)
            throw new IllegalArgumentException("Operation cannot be null");

        if (operation.equals(""))
            throw new IllegalArgumentException("Operation cannot be empty");
        
        switch (operation) {
            case "+" -> ans = operand1 + operand2;
            case "-" -> ans = operand1 - operand2;
            case "*" -> ans = operand1 * operand2;
            case "/" ->
                {
                    if (operand2 != 0)
                        ans = operand1 / operand2;
                    else
                        throw new IllegalOperationException("Division by zero is not allowed", new ArithmeticException("/ by zero"));
                }
            default -> exception = 1;        
        } 

        if (exception == 1)
            throw new IllegalOperationException("Operation '" + operation + "' does not exist");
        
        return Integer.toString(operand1) + " " + operation + " " + Integer.toString(operand2) + " = " + Integer.toString(ans);
}
}
