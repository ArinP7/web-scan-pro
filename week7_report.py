import json
import os
from collections import Counter
import dominate
import dominate.tags as t
from datetime import datetime
import matplotlib.pyplot as plt

def load_findings(results_dir):
    findings = []
    for filename in os.listdir(results_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(results_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                # If data is a list of dicts, extend findings
                if isinstance(data, list):
                    findings.extend(data)
                else:
                    # If data is a single string or dict, append it
                    findings.append(data)
    return findings

def severity_level(severity):
    # Normalize severity to Low, Medium, High
    sev = severity.lower()
    if sev in ["low", "medium", "high"]:
        return sev.capitalize()
    # Default to Low if unknown
    return "Low"

def generate_summary(findings):
    severity_counts = Counter()
    type_counts = Counter()
    for f in findings:
        # Check if f is a dict, else skip or handle accordingly
        if isinstance(f, dict):
            severity_counts[severity_level(f.get("severity", "Low"))] += 1
            type_counts[f.get("type", "Unknown")] += 1
        else:
            # If f is a string or other type, skip or handle default
            severity_counts["Low"] += 1
            type_counts["Unknown"] += 1
    return severity_counts, type_counts

def plot_bar_chart(counter, title, filename):
    labels = list(counter.keys())
    values = list(counter.values())
    plt.figure(figsize=(6,4))
    plt.bar(labels, values, color='skyblue')
    plt.title(title)
    plt.xlabel('Category')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

def save_report(findings, outfile):
    severity_counts, type_counts = generate_summary(findings)
    # Generate charts
    plot_bar_chart(severity_counts, "Vulnerabilities by Severity", "severity_chart.png")
    plot_bar_chart(type_counts, "Vulnerabilities by Type", "type_chart.png")

    doc = dominate.document(title="Week 7 Security Report")
    with doc:
        t.h1("Week 7 Security Report")
        t.p(f"Generated on {datetime.now():%Y-%m-%d %H:%M}")
        t.h2("Summary")
        with t.div():
            t.h3("Vulnerabilities by Severity")
            t.img(src="severity_chart.png", width=400)
            t.h3("Vulnerabilities by Type")
            t.img(src="type_chart.png", width=400)
        t.h2("Detailed Findings")
        if not findings:
            t.p("No vulnerabilities found.")
        else:
            for f in findings:
                if isinstance(f, dict):
                    with t.div(style="margin:20px 0; border:1px solid #ccc; padding:10px;"):
                        t.h3(f"{f.get('type', 'Unknown')} - {f.get('url', 'N/A')}")
                        t.p(f"Severity: {severity_level(f.get('severity', 'Low'))}")
                        t.p(f"Affected Endpoint: {f.get('url', 'N/A')}")
                        t.p(f"Suggested Mitigation: {f.get('mitigation', 'N/A')}")
                        if f.get("screenshot"):
                            t.img(src=f["screenshot"], width=400)
                else:
                    with t.div(style="margin:20px 0; border:1px solid #ccc; padding:10px;"):
                        t.h3(str(f))
    with open(outfile, "w", encoding="utf-8") as f:
        f.write(str(doc))

if __name__ == "__main__":
    results_dir = "results"
    output_file = "reports/week7_security_report.html"
    findings = load_findings(results_dir)
    save_report(findings, output_file)
    print(f"Week 7 security report generated: {output_file}")
