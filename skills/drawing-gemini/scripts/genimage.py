#!/usr/bin/env python3
# WHAT  One text-to-image call against ModelRouter, saved as a PNG. Three request shapes behind one
#       flag: OpenAI /images/generations (gpt-image, seedream), Gemini :generateContent with
#       responseModalities IMAGE, and a probe mode that reports which image models the key reaches.
# WHEN  2026-09-21, generating candidate paper figures beside the hand-drawn ones.
# USAGE set -a; . $CPFS_HOME/.secret; set +a
#       python3 genimage.py --prompt-file p.txt --out fig.png [--model mr.gpt-image-2] [--size 1536x1024]
#       python3 genimage.py --probe
import argparse, base64, json, os, sys, time, urllib.error, urllib.request

OPENAI = ("mr.gpt-image-2", "gpt-image-1.5", "mr.doubao-seedream-5-0-260128",
          "mr.doubao-seedream-4-5-251128", "doubao-seedream-4-5-251128")
GEMINI = ("mr.gemini-3-pro-image-preview", "mr.gemini-3.1-flash-image-preview",
          "mr.vertex_ai.gemini-3-pro-image-preview", "gemini-3-pro-image-preview")


def endpoints():
    base = os.environ["MODELROUTER_BASE_URL"].rstrip("/")   # KeyError is the right failure
    return base, base.split("/protocol/")[0], os.environ["MODELROUTER_API_KEY"]


def family_of(model):
    if model in GEMINI or "image-preview" in model:
        return "gemini"
    return "openai"


def post(url, body, headers, timeout):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json", **headers})
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, round(time.perf_counter() - t0, 1), r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, round(time.perf_counter() - t0, 1), e.read().decode("utf-8", "replace")
    except Exception as e:                                   # network, DNS, timeout
        return None, round(time.perf_counter() - t0, 1), repr(e)


def request_for(model, prompt, size, aspect, family):
    base, root, key = endpoints()
    if family == "gemini":
        return (f"{root}/protocol/vertex/v1beta/models/{model}:generateContent",
                {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
                 "generationConfig": {"responseModalities": ["IMAGE"],
                                      "imageConfig": {"aspectRatio": aspect, "imageSize": "2K"}}},
                {"x-goog-api-key": f"Bearer {key}"})
    return (f"{base}/images/generations",
            {"model": model, "prompt": prompt, "size": size, "n": 1},
            {"Authorization": f"Bearer {key}"})


def extract_png(family, raw):
    """The bytes of the first image in the reply, or None with the reason."""
    try:
        doc = json.loads(raw)
    except json.JSONDecodeError:
        return None, "reply was not JSON"
    if family == "gemini":
        for cand in doc.get("candidates", []):
            for part in cand.get("content", {}).get("parts", []):
                blob = part.get("inlineData", {}).get("data") or part.get("inline_data", {}).get("data")
                if blob:
                    return base64.b64decode(blob), None
        return None, "no inlineData part in the reply"
    for item in doc.get("data", []):
        if item.get("b64_json"):
            return base64.b64decode(item["b64_json"]), None
        if item.get("url"):
            with urllib.request.urlopen(item["url"], timeout=120) as r:
                return r.read(), None
    return None, "no data[] image in the reply"


def probe(timeout):
    p = "a plain white square with one black circle in the centre, flat vector, no text"
    for model in OPENAI + GEMINI:
        fam = family_of(model)
        url, body, hdr = request_for(model, p, "1024x1024", "1:1", fam)
        st, dt, raw = post(url, body, hdr, timeout)
        png, why = extract_png(fam, raw) if st == 200 else (None, raw[:110].replace("\n", " "))
        print(f"[{st}] {dt:>6}s {fam:<7} {model:<42} {'OK, ' + str(len(png)) + ' bytes' if png else why}")
        time.sleep(3)                                        # the key is rate limited, RPM 5


ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument("--model", default="mr.gpt-image-2")
ap.add_argument("--family", choices=("auto", "openai", "gemini"), default="auto")
ap.add_argument("--prompt"), ap.add_argument("--prompt-file")
ap.add_argument("--out", default="image.png")
ap.add_argument("--size", default="1536x1024", help="OpenAI family, pixels")
ap.add_argument("--aspect", default="3:2", help="Gemini family")
ap.add_argument("--timeout", type=float, default=300)
ap.add_argument("--probe", action="store_true")
a = ap.parse_args()

if a.probe:
    probe(a.timeout)
    raise SystemExit(0)

prompt = a.prompt or open(a.prompt_file).read()
fam = family_of(a.model) if a.family == "auto" else a.family
url, body, hdr = request_for(a.model, prompt, a.size, a.aspect, fam)
st, dt, raw = post(url, body, hdr, a.timeout)
if st != 200:
    print(f"[{st}] {a.model}: {raw[:400]}", file=sys.stderr)
    raise SystemExit(1)
png, why = extract_png(fam, raw)
if png is None:
    print(f"[{st}] {a.model}: {why}\n{raw[:400]}", file=sys.stderr)
    raise SystemExit(1)
open(a.out, "wb").write(png)
print(f"{a.out}  {len(png)} bytes  {dt}s  {a.model}")
