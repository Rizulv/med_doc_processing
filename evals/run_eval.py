import argparse, json, re, requests

DOC_TYPES = [
    "COMPLETE BLOOD COUNT",
    "BASIC METABOLIC PANEL",
    "X-RAY",
    "CT",
    "CLINICAL NOTE",
]

def norm_code(c: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", c.upper())

def score_codes(pred, gold):
    pset = {norm_code(x.get("code","")) for x in pred if isinstance(x, dict)}
    gset = {norm_code(x) for x in gold}
    tp = len(pset & gset)
    fp = len(pset - gset)
    fn = len(gset - pset)
    precision = tp / (tp + fp) if (tp+fp)>0 else 0.0
    recall    = tp / (tp + fn) if (tp+fn)>0 else 0.0
    f1 = 2*precision*recall/(precision+recall) if (precision+recall)>0 else 0.0
    return precision, recall, f1

def coverage(summary: str, facts):
    s = (summary or "").lower()
    got = sum(1 for f in facts if f.lower() in s)
    return got / len(facts) if facts else 0.0

def post(base, path, payload):
    r = requests.post(base.rstrip("/") + path, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default="http://127.0.0.1:8000")
    ap.add_argument("--dataset", default="evals/datasets/synthetic_v1.json")
    ap.add_argument("--mode", choices=["with_hint","classify_only"], default="with_hint")
    args = ap.parse_args()

    data = json.load(open(args.dataset, "r", encoding="utf-8"))

    cls_correct = cls_total = 0
    pr_sum = rc_sum = f1_sum = cov_sum = 0.0
    n = 0

    for item in data:
        text = item["text"]
        gold = item["gold"]
        gold_type = gold["document_type"]

        if args.mode == "classify_only":
            resp_cls = post(args.base_url, "/classify", {"document_text": text})
            pred_type = resp_cls.get("document_type","")
            cls_correct += int(pred_type == gold_type)
            cls_total += 1
        else:
            pred_type = item["document_type"]  # as if user selected it

        # codes
        payload = {"document_text": text}
        if args.mode == "with_hint":
            payload["document_type"] = pred_type
        resp_codes = post(args.base_url, "/extract-codes", payload)
        p, r, f1 = score_codes(resp_codes.get("codes", []), gold["icd10_codes"])
        pr_sum += p; rc_sum += r; f1_sum += f1

        # summary
        payload = {"document_text": text, "codes": resp_codes.get("codes", [])}
        if args.mode == "with_hint":
            payload["document_type"] = pred_type
        resp_sum = post(args.base_url, "/summarize", payload)
        cov_sum += coverage(resp_sum.get("summary",""), gold["summary_facts"])

        n += 1

    print("\n=== EVAL RESULTS ===")
    if cls_total:
        print(f"Classification accuracy: {cls_correct/cls_total:.2f}  ({cls_correct}/{cls_total})")
    print(f"Codes  P/R/F1: {pr_sum/n:.2f} / {rc_sum/n:.2f} / {f1_sum/n:.2f}")
    print(f"Summary coverage: {cov_sum/n:.2f}")
    print(f"Items: {n} | Mode: {args.mode}")

if __name__ == "__main__":
    main()
