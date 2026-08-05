import java.nio.file.*;
import java.util.*;
import java.util.regex.*;

/*
 * SmartPrompt - native Java port. Reproduces smartprompt.core.lint exactly
 * (rule IDs, issue/fix strings, ordering, weights, clarity score). JDK-only.
 *   javac SmartPrompt.java && java SmartPrompt [vectors.json]
 */
public class SmartPrompt {

    record Rule(String id, String issue, Pattern re, boolean positive, String fix) {}
    static final List<Rule> RULES = List.of(
        new Rule("PROMPT-ROLE", "No role/persona set",
            Pattern.compile("\\b(you are|act as|role:)\\b", Pattern.CASE_INSENSITIVE), false,
            "Open with a role: 'You are a <expert> ...'."),
        new Rule("PROMPT-GOAL", "Vague or missing goal",
            Pattern.compile("\\b(write|summariz|analyz|list|compare|generate|fix|explain|classif)", Pattern.CASE_INSENSITIVE), false,
            "State one concrete verb+object."),
        new Rule("PROMPT-FORMAT", "No output format",
            Pattern.compile("\\b(json|markdown|table|bullet|list|format|schema)\\b", Pattern.CASE_INSENSITIVE), false,
            "Name the output shape."),
        new Rule("PROMPT-CONSTRAINTS", "No constraints",
            Pattern.compile("\\b(word|sentence|tone|audience|concise|under \\d)", Pattern.CASE_INSENSITIVE), false,
            "Add limits: length, tone, audience."),
        new Rule("PROMPT-PII", "Secret/PII in prompt",
            Pattern.compile("(sk-[A-Za-z0-9]{12,}|AKIA[0-9A-Z]{12,})"), true,
            "Remove the secret \u2014 see SmartPangolin."));
    static final Map<String, Integer> WEIGHT = Map.of(
        "PROMPT-PII", 35, "PROMPT-GOAL", 20, "PROMPT-ROLE", 12, "PROMPT-FORMAT", 12, "PROMPT-CONSTRAINTS", 10);

    record Defect(String rule, String issue, String fix) {}
    record Score(int clarity, List<Defect> defects) {}

    static Score lint(String text) {
        List<Defect> defects = new ArrayList<>();
        int total = 0;
        for (Rule r : RULES) {
            boolean m = r.re().matcher(text).find();
            if (r.positive() ? m : !m) {
                defects.add(new Defect(r.id(), r.issue(), r.fix()));
                total += WEIGHT.getOrDefault(r.id(), 6);
            }
        }
        return new Score(Math.max(0, 100 - total), defects);
    }

    static String esc(String s) {
        StringBuilder b = new StringBuilder();
        for (char c : s.toCharArray()) switch (c) {
            case '"' -> b.append("\\\"");
            case '\\' -> b.append("\\\\");
            case '\n' -> b.append("\\n");
            case '\r' -> b.append("\\r");
            case '\t' -> b.append("\\t");
            default -> b.append(c);
        }
        return b.toString();
    }

    static String scoreJson(String name, Score s) {
        StringBuilder b = new StringBuilder("{");
        if (name != null) b.append("\"name\":\"").append(esc(name)).append("\",");
        b.append("\"clarity\":").append(s.clarity()).append(",\"defects\":[");
        for (int i = 0; i < s.defects().size(); i++) {
            Defect d = s.defects().get(i);
            if (i > 0) b.append(",");
            b.append("{\"rule\":\"").append(esc(d.rule())).append("\",\"issue\":\"").append(esc(d.issue()))
             .append("\",\"fix\":\"").append(esc(d.fix())).append("\"}");
        }
        return b.append("]}").toString();
    }

    public static void main(String[] args) throws Exception {
        if (args.length >= 1 && args[0].equals("--text")) {
            System.out.println(scoreJson(null, lint(args.length >= 2 ? args[1] : "")));
            return;
        }
        String vpath = args.length >= 1 ? args[0]
            : Paths.get(System.getProperty("user.dir"), "..", "conformance", "vectors.json").toString();
        Json j = new Json(Files.readString(Paths.get(vpath)));
        Map<String, Object> root = j.parseObject();
        @SuppressWarnings("unchecked")
        List<Object> cases = (List<Object>) root.get("cases");
        StringBuilder out = new StringBuilder("{\"results\":[");
        for (int i = 0; i < cases.size(); i++) {
            @SuppressWarnings("unchecked")
            Map<String, Object> c = (Map<String, Object>) cases.get(i);
            if (i > 0) out.append(",");
            out.append(scoreJson((String) c.get("name"), lint((String) c.getOrDefault("text", ""))));
        }
        System.out.println(out.append("]}"));
    }

    static class Json {
        final String s; int i;
        Json(String s) { this.s = s; }
        void ws() { while (i < s.length() && Character.isWhitespace(s.charAt(i))) i++; }
        Map<String, Object> parseObject() { ws(); return (Map<String, Object>) value(); }
        Object value() {
            ws(); char c = s.charAt(i);
            return switch (c) {
                case '{' -> obj(); case '[' -> arr(); case '"' -> str();
                case 't', 'f' -> bool(); case 'n' -> nul(); default -> num();
            };
        }
        Map<String, Object> obj() {
            Map<String, Object> m = new LinkedHashMap<>(); i++; ws();
            if (s.charAt(i) == '}') { i++; return m; }
            while (true) { ws(); String k = str(); ws(); i++; m.put(k, value()); ws();
                if (s.charAt(i) == ',') { i++; continue; } i++; break; }
            return m;
        }
        List<Object> arr() {
            List<Object> a = new ArrayList<>(); i++; ws();
            if (s.charAt(i) == ']') { i++; return a; }
            while (true) { a.add(value()); ws(); if (s.charAt(i) == ',') { i++; continue; } i++; break; }
            return a;
        }
        String str() {
            StringBuilder b = new StringBuilder(); i++;
            while (true) { char c = s.charAt(i++);
                if (c == '"') break;
                if (c == '\\') { char e = s.charAt(i++); switch (e) {
                    case '"' -> b.append('"'); case '\\' -> b.append('\\'); case '/' -> b.append('/');
                    case 'n' -> b.append('\n'); case 'r' -> b.append('\r'); case 't' -> b.append('\t');
                    case 'b' -> b.append('\b'); case 'f' -> b.append('\f');
                    case 'u' -> { b.append((char) Integer.parseInt(s.substring(i, i + 4), 16)); i += 4; }
                    default -> b.append(e); } }
                else b.append(c); }
            return b.toString();
        }
        Object bool() { if (s.startsWith("true", i)) { i += 4; return Boolean.TRUE; } i += 5; return Boolean.FALSE; }
        Object nul() { i += 4; return null; }
        Object num() { int st = i; while (i < s.length() && "+-.eE0123456789".indexOf(s.charAt(i)) >= 0) i++;
            return Double.parseDouble(s.substring(st, i)); }
    }
}
