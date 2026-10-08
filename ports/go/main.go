// SmartPrompt - native Go port. Reproduces sf_smartprompt.core.lint exactly.
// Standard library only (RE2 + encoding/json).
package main

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
)

type rule struct {
	id, issue, fix string
	fires          func(string) bool
}

func mustNeg(p string) func(string) bool { r := regexp.MustCompile(p); return func(t string) bool { return !r.MatchString(t) } }
func mustPos(p string) func(string) bool { r := regexp.MustCompile(p); return func(t string) bool { return r.MatchString(t) } }

var rules = []rule{
	{"PROMPT-ROLE", "No role/persona set", "Open with a role: 'You are a <expert> ...'.", mustNeg(`(?i)\b(you are|act as|role:)\b`)},
	{"PROMPT-GOAL", "Vague or missing goal", "State one concrete verb+object.", mustNeg(`(?i)\b(write|summariz|analyz|list|compare|generate|fix|explain|classif)`)},
	{"PROMPT-FORMAT", "No output format", "Name the output shape.", mustNeg(`(?i)\b(json|markdown|table|bullet|list|format|schema)\b`)},
	{"PROMPT-CONSTRAINTS", "No constraints", "Add limits: length, tone, audience.", mustNeg(`(?i)\b(word|sentence|tone|audience|concise|under \d)`)},
	{"PROMPT-PII", "Secret/PII in prompt", "Remove the secret \u2014 see SmartPangolin.", mustPos(`(sk-[A-Za-z0-9]{12,}|AKIA[0-9A-Z]{12,})`)},
}
var weight = map[string]int{"PROMPT-PII": 35, "PROMPT-GOAL": 20, "PROMPT-ROLE": 12, "PROMPT-FORMAT": 12, "PROMPT-CONSTRAINTS": 10}

type Defect struct {
	Rule  string `json:"rule"`
	Issue string `json:"issue"`
	Fix   string `json:"fix"`
}
type Score struct {
	Name    string   `json:"name,omitempty"`
	Clarity int      `json:"clarity"`
	Defects []Defect `json:"defects"`
}

func lint(text string) Score {
	defects := []Defect{}
	total := 0
	for _, r := range rules {
		if r.fires(text) {
			defects = append(defects, Defect{r.id, r.issue, r.fix})
			w, ok := weight[r.id]
			if !ok {
				w = 6
			}
			total += w
		}
	}
	c := 100 - total
	if c < 0 {
		c = 0
	}
	return Score{Clarity: c, Defects: defects}
}

func main() {
	args := os.Args[1:]
	if len(args) >= 1 && args[0] == "--text" {
		t := ""
		if len(args) >= 2 {
			t = args[1]
		}
		b, _ := json.Marshal(lint(t))
		fmt.Println(string(b))
		return
	}
	vpath := filepath.Join("..", "conformance", "vectors.json")
	if len(args) >= 1 {
		vpath = args[0]
	}
	raw, _ := os.ReadFile(vpath)
	var v struct {
		Cases []struct{ Name, Text string } `json:"cases"`
	}
	json.Unmarshal(raw, &v)
	results := make([]Score, 0, len(v.Cases))
	for _, c := range v.Cases {
		s := lint(c.Text)
		s.Name = c.Name
		results = append(results, s)
	}
	b, _ := json.MarshalIndent(map[string]interface{}{"results": results}, "", "  ")
	fmt.Println(string(b))
}
