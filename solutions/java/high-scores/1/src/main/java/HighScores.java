import java.util.List;
import java.util.Collections;
import java.util.ArrayList;

class HighScores {
    private final List<Integer> scores;

    public HighScores(List<Integer> highScores) {
        this.scores = highScores;
    }

    List<Integer> scores() {
        return scores;
    }

    Integer latest() {
        return scores.get(scores.size() - 1);
    }

    Integer personalBest() {
        return Collections.max(scores);
    }

    List<Integer> personalTopThree() {
        List<Integer> sorted = new ArrayList<>(scores);       
        Collections.sort(sorted, Collections.reverseOrder()); 

        int limit = Math.min(3, sorted.size());        
        return sorted.subList(0, limit);
    }

}
