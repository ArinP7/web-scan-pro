import dominate, dominate.tags as t, json
from datetime import datetime

def save_report(findings, outfile, module):
    doc = dominate.document(title=f"{module} Report")
    with doc:
        t.h1(f"{module} Scan – {datetime.now():%Y-%m-%d %H:%M}")
        if not findings:
            t.p("No vulnerabilities.")
        else:
            for f in findings:
                with t.div(style="margin:20px 0"):
                    t.h3(f"{f['type']} – {f['url']}")
                    t.pre(json.dumps(f, indent=2))
                    if f.get("screenshot"):
                        t.img(src=f["screenshot"], width=400)
    open(outfile, "w", encoding="utf-8").write(str(doc))
