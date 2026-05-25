import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

class AppointmentScheduler {
    public LocalDateTime schedule(String appointmentDateDescription) {
        DateTimeFormatter format = DateTimeFormatter.ofPattern("M/d/yyyy HH:mm:ss");
        return LocalDateTime.parse(appointmentDateDescription, format);
    }

    public boolean hasPassed(LocalDateTime appointmentDate) {
        LocalDateTime present = LocalDateTime.now();
        return appointmentDate.isBefore(present);
    }

    public boolean isAfternoonAppointment(LocalDateTime appointmentDate) {
        return appointmentDate.getHour() >= 12 && appointmentDate.getHour() < 18;
    }

    public String getDescription(LocalDateTime appointmentDate) {
        DateTimeFormatter format1 = DateTimeFormatter.ofPattern("EEEE, MMMM d, yyyy,");
        DateTimeFormatter format2 = DateTimeFormatter.ofPattern("h:mm a");
        return "You have an appointment on " + format1.format(appointmentDate) + " at " + format2.format(appointmentDate) + ".";
    }

    public LocalDate getAnniversaryDate() {
        LocalDateTime present = LocalDateTime.now();
        DateTimeFormatter format = DateTimeFormatter.ofPattern("yyyy, M, d");
        LocalDate anniv = LocalDate.of(present.getYear(), 9, 15);
        return anniv;
    }
}
