#!/usr/bin/env python3
"""Director's sheet: the Gate 2/3 review instrument.

  build     plan.json -> a self-contained HTML sheet (cast lock, per-scene purpose / audience-learns / coverage /
            dialogue / continuity, previs frames, approve / needs-changes + notes per scene).
  decisions decisions.json (+ plan.json) -> a markdown retake/rewrite list for the production.

Usage:
  python3 director_sheet.py build --plan v3/sheet/plan.json --out v3/sheet/sheet.html \
      --images v3/previs v2/refs            # dirs of images; keys = file stem (previs_s01.jpg, cast_channa.jpg ...)
  python3 director_sheet.py decisions --plan v3/sheet/plan.json --decisions v3/sheet/decisions.json

Plan schema (JSON): {title, title_native?, draft?, spine, aspect, acts:{"1":"Act one — …"},
  cast:[{id,name,idstr,image?,new?}],
  scenes:[{id,n,act,title,slug,dur,purpose,learns,shift,cast:[ids],
           shots:[{size,action,sec,angle?}], dialogue:[{kind:"line"|"narr",who,native,en}], cont, previs?, frame?, v2?}]}
  shots[].angle = camera-angle dials, e.g. "seated eye · level · 3/4 left" (reference/camera-angles.md).
Publishing: in Claude Code, publish the HTML with the Artifact tool and `capabilities: {db: {}}`; decisions land in the
artifact db, collection `reviews`, one doc per scene id -> read them with read_db and save as decisions.json.
Outside Claude Code the reviewer presses "Copy decisions as JSON" and sends the text back; save it as decisions.json.
"""
import argparse, base64, json, os, sys, mimetypes

def load_images(dirs):
    imgs={}
    for d in dirs or []:
        if not os.path.isdir(d): continue
        for f in sorted(os.listdir(d)):
            stem,ext=os.path.splitext(f)
            if ext.lower() not in (".jpg",".jpeg",".png",".webp"): continue
            mime=mimetypes.guess_type(f)[0] or "image/jpeg"
            imgs[stem]="data:%s;base64,%s"%(mime,base64.b64encode(open(os.path.join(d,f),"rb").read()).decode())
    return imgs

def build(a):
    plan=json.load(open(a.plan))
    imgs=load_images(a.images)
    tpl=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"templates","director_sheet.html")).read()
    html=tpl.replace("{{TITLE}}",plan.get("title","Director's Sheet")+" Director's Sheet")
    html=html.replace("/*__DATA__*/","const IMAGES="+json.dumps(imgs)+";\nconst PLAN="+json.dumps(plan,ensure_ascii=False)+";")
    open(a.out,"w").write(html)
    missing=[c["id"] for c in plan["cast"] if c.get("image") and c["image"] not in imgs]
    print(f"wrote {a.out} ({len(html)//1024} KB): {len(plan['scenes'])} scenes, {len(plan['cast'])} cast, {len(imgs)} images embedded"+(f"; cast images not found: {missing}" if missing else ""))

def decisions(a):
    plan=json.load(open(a.plan)); dec=json.load(open(a.decisions))
    rows=dec.get("decisions") if isinstance(dec,dict) else dec
    by={ (r.get("id") or r.get("doc_id")): r for r in rows }
    out=["# Decisions — "+plan.get("title",""),""]
    counts={"approved":0,"changes":0,"pending":0}
    for s in plan["scenes"]:
        r=by.get(s["id"],{}); st=r.get("status","pending"); counts[st if st in counts else "pending"]+=1
        mark={"approved":"✅","changes":"↺"}.get(st,"·")
        out.append(f"{mark} **{s['n']:02d} {s['title']}** — {st}"+(f" — _{r.get('reviewer')}_" if r.get("reviewer") else ""))
        if r.get("notes"): out.append(f"   > {r['notes'].strip()}")
    out.insert(2,f"{counts['approved']} approved · {counts['changes']} need changes · {counts['pending']} pending. "+("**Gate 3 open — every scene approved.**" if counts["approved"]==len(plan["scenes"]) else "Gate 3 closed until every scene is approved."))
    print("\n".join(out))

if __name__=="__main__":
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest="cmd",required=True)
    b=sub.add_parser("build"); b.add_argument("--plan",required=True); b.add_argument("--out",required=True); b.add_argument("--images",nargs="*")
    d=sub.add_parser("decisions"); d.add_argument("--plan",required=True); d.add_argument("--decisions",required=True)
    a=ap.parse_args(); {"build":build,"decisions":decisions}[a.cmd](a)
