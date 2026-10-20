public class LogLine {

    private String logLine;
    private String temp;
    private String message;
    
    public LogLine(String logLine) {
        this.logLine = logLine;
    }
    
    public LogLevel getLogLevel() {
        String temp = logLine.substring(1,4);
        return switch (temp) {
            case "TRC" -> LogLevel.TRACE;
            case "DBG" -> LogLevel.DEBUG;
            case "INF" -> LogLevel.INFO;
            case "WRN" -> LogLevel.WARNING;
            case "ERR" -> LogLevel.ERROR;
            case "FTL" -> LogLevel.FATAL;
                default -> LogLevel.UNKNOWN;
        };
    }

    public String getOutputForShortLog() {
        String temp = logLine.substring(1,4);
        String message = logLine.substring(logLine.indexOf(" ")+1);
        
        String number = switch (temp) {
            case "TRC" -> "1:";
            case "DBG" -> "2:";
            case "INF" -> "4:";
            case "WRN" -> "5:";
            case "ERR" -> "6:";
            case "FTL" -> "42:";
            default    -> "0:";
        };
        return number + message;
    }
}
