"""SEO layer: canonical, titles, JSON-LD, hub, about, sitemap, related links, FAQs.
Installed by main.py after payfix. Post-processes HTML responses; never touches /api, /auth, /buy, payments."""
import html as _h
import io
import json
import re

BASE = "https://nexora-web-q7rn.onrender.com"
LASTMOD = "2026-10-02"
_DONE = {"v": False}

PDF_GROUPS = [
    ["merge", "split", "organize", "rotate", "crop", "page-numbers"],
    ["compress", "grayscale", "repair"],
    ["pdf-to-word", "pdf-to-ppt", "pdf-to-excel", "pdf-to-jpg", "pdf-to-txt", "pdf-to-markdown", "extract-images"],
    ["word-to-pdf", "ppt-to-pdf", "excel-to-pdf", "jpg-to-pdf", "html-to-pdf", "scan-to-pdf"],
    ["edit", "sign", "watermark", "protect", "unlock", "redact", "ocr", "compare"],
]
PDF_TITLES = {
    "merge": ("Merge PDF Online Free - Combine PDF Files | Nexora", "Merge PDF files online for free. Combine several PDFs into one document in the order you choose. No sign-up."),
    "split": ("Split PDF Online Free - Extract Pages from PDF | Nexora", "Split a PDF online for free. Extract a page range or split into separate files. No sign-up."),
    "compress": ("Compress PDF Online Free - Reduce PDF File Size | Nexora", "Compress PDF files online for free and reduce file size for email or forms. No sign-up."),
    "pdf-to-word": ("PDF to Word Converter Online Free - PDF to DOCX | Nexora", "Convert PDF to an editable Word (DOCX) file online for free. No sign-up."),
    "word-to-pdf": ("Word to PDF Converter Online Free - DOC to PDF | Nexora", "Convert Word DOC and DOCX files to PDF online for free. No sign-up."),
    "jpg-to-pdf": ("JPG to PDF Converter Online Free - Images to PDF | Nexora", "Convert JPG and PNG images to a PDF online for free. No sign-up."),
    "pdf-to-jpg": ("PDF to JPG Converter Online Free - PDF Pages to Images | Nexora", "Convert PDF pages to JPG images online for free. No sign-up."),
}
STUDENT_LINKS = [("/students", "Student Calculators"), ("/vtu-sgpa-calculator", "VTU SGPA Calculator"),
                 ("/vtu-cgpa-calculator", "VTU CGPA Calculator"), ("/cgpa-to-percentage-calculator", "CGPA to Percentage"),
                 ("/students/gpa-calculator", "GPA Calculator"), ("/students/percentage-calculator", "Percentage Calculator"),
                 ("/students/attendance-calculator", "Attendance Calculator"), ("/students/cgpa-percentage-converter", "CGPA Percentage Converter")]
FOOT_LINKS = [("/pdf", "Free PDF Tools"), ("/pdf/merge", "Merge PDF"), ("/pdf/compress", "Compress PDF"), ("/pdf/split", "Split PDF"),
              ("/pdf/pdf-to-word", "PDF to Word"), ("/students", "Student Calculators"), ("/vtu-sgpa-calculator", "VTU SGPA Calculator"),
              ("/vtu-cgpa-calculator", "VTU CGPA Calculator"), ("/cgpa-to-percentage-calculator", "CGPA to Percentage"),
              ("/resume-builder", "Resume Builder"), ("/pro", "Pro"), ("/about", "About")]
META = {
    "/": ("Free PDF Tools & Student Calculators Online | Nexora",
          "Nexora has free PDF tools (merge, split, compress, convert) and student calculators (VTU SGPA, CGPA, percentage, attendance), plus resume and HR tools."),
    "/students": ("Student Calculators - CGPA, Percentage, Attendance | Nexora",
                  "Free student calculators: CGPA, SGPA, percentage, attendance, final marks needed, and more. Quick to use, no sign-up."),
    "/vtu-sgpa-calculator": ("VTU SGPA Calculator 2026 - Free Semester SGPA Calculator | Nexora",
                             "Calculate your VTU SGPA from credits and grade points, then see an estimated percentage. Free, no sign-up."),
    "/vtu-cgpa-calculator": ("VTU CGPA Calculator 2026 - CGPA to Percentage | Nexora",
                             "Calculate VTU CGPA across semesters and convert it to an estimated percentage. Free, no sign-up."),
    "/cgpa-to-percentage-calculator": ("CGPA to Percentage Calculator (VTU Formula) | Nexora",
                                       "Convert CGPA to percentage and percentage to CGPA using the VTU formula or a simple x10 method. Free."),
    "/pdf": ("Free PDF Tools - Merge, Split, Compress, Convert | Nexora",
             "Free online PDF tools: merge, split, compress, convert PDF to Word, Excel, PowerPoint and JPG, edit, sign, protect and more. No sign-up."),
    "/about": ("About Nexora - Free PDF, Student and Career Tools | Nexora",
               "What Nexora is, what is free, what is paid, and how to contact us."),
}
H1 = {
    "/vtu-sgpa-calculator": "VTU SGPA Calculator 2026",
    "/vtu-cgpa-calculator": "VTU CGPA Calculator 2026",
    "/students": "Student Calculators - CGPA, Percentage, Attendance",
}
INTRO = {
    "/": "Nexora offers free PDF tools (merge, split, compress, convert) and student calculators (VTU SGPA, CGPA to percentage, attendance), plus resume and HR tools. Most tools need no sign-up.",
    "/vtu-sgpa-calculator": "Use this VTU SGPA calculator to work out your semester SGPA from each subject's credits and grade points. Results are estimates; check your university circular for the official figure.",
    "/vtu-cgpa-calculator": "Enter your semester SGPAs and credits to get your VTU CGPA and an estimated percentage. Check your university circular for the official conversion for your scheme.",
    "/cgpa-to-percentage-calculator": "Convert CGPA to percentage (or back) with the VTU formula or a simple x10 method. Use the method your college or employer asks for.",
    "/students": "Free calculators for students: CGPA and SGPA, percentage, attendance, final marks needed, and exam planning tools. Pick one below.",
}
EXTRA_FAQ = {
    "/vtu-sgpa-calculator": [
        ("What is SGPA?", "SGPA is your semester grade point average: total of credits x grade points divided by total credits for that semester."),
        ("Is the result official?", "No. It is an estimate for your own planning. Your official result is the one on your marks card or university portal."),
    ],
    "/vtu-cgpa-calculator": [
        ("What is the VTU CGPA to percentage formula?", "The formula commonly used for VTU is (CGPA - 0.75) x 10. Check your university circular for the scheme you are in."),
        ("Do I need every semester to get CGPA?", "Enter the semesters you have completed. CGPA is the credit-weighted average of those semesters."),
    ],
    "/cgpa-to-percentage-calculator": [
        ("How do I convert CGPA to percentage?", "With the VTU formula, percentage = (CGPA - 0.75) x 10. A simple alternative is CGPA x 10."),
        ("Which method should I use?", "Use the method your university, college or employer specifies. If none is given, ask them or check the official circular."),
        ("Is this calculator free?", "Yes. It is free to use and needs no sign-up."),
    ],
}
GENERIC_CALC_FAQ = [
    ("Is this calculator free?", "Yes. It is free to use and needs no sign-up."),
    ("Is the result official?", "No. Results are estimates for your own planning. Check your college or university rules for the official method."),
]
ABOUT_BODY = """<section class="page-hero"><div class="container"><h1>About Nexora</h1>
<p>Nexora is a set of online tools for documents, students and careers.</p></div></section>
<section class="section"><div class="container">
<div class="card"><h2 style="margin-top:0">What you can do here</h2>
<p>Use <a href="/pdf">free PDF tools</a> (merge, split, compress, convert and more), <a href="/students">student calculators</a> such as the
<a href="/vtu-sgpa-calculator">VTU SGPA calculator</a>, <a href="/vtu-cgpa-calculator">VTU CGPA calculator</a> and
<a href="/cgpa-to-percentage-calculator">CGPA to percentage</a>, plus <a href="/resume-builder">resume</a> and <a href="/hr-career">HR and career</a> tools.</p></div>
<div class="card" style="margin-top:16px"><h2 style="margin-top:0">Free and paid</h2>
<p>The PDF tools and student calculators are free to use without signing up. Paid options are the <a href="/resume-service">online resume formatting service</a>,
the <a href="/excel-service">Excel cleanup and PDF to Excel service</a>, and <a href="/pro">Nexora Pro</a>. Prices are shown on each page before you pay.</p></div>
<div class="card" style="margin-top:16px"><h2 style="margin-top:0">Your files</h2>
<p>PDF tool pages state how files are handled. See the <a href="/privacy">privacy policy</a> and <a href="/terms">terms</a> for details.</p></div>
<div class="card" style="margin-top:16px"><h2 style="margin-top:0">Contact</h2>
<p>For the paid services or questions, message us on WhatsApp: 9353006448.</p></div>
</div></section>"""


def _esc(s):
    return _h.escape(s, quote=True)


def _ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False).replace("</", "<\\/") + "</script>"


def install(g):
    if _DONE["v"]:
        return
    _DONE["v"] = True
    app = g["app"]
    specs = g["PDF_TOOL_SPECS"]
    order = list(g["PDF_TOOL_ORDER"])
    careers = list(g["CAREER_TOOLS"].keys())
    pagefn = g["page"]
    from fastapi import Request
    from fastapi.responses import HTMLResponse, Response

    def pdf_meta(slug):
        sp = specs[slug]
        if slug in PDF_TITLES:
            return PDF_TITLES[slug]
        return (f"{sp['title']} Online Free - No Sign-up | Nexora",
                f"{sp['title']} online for free. {sp['desc']} No sign-up.")

    def pdf_faq(slug):
        sp = specs[slug]
        t = sp["title"]
        acc = sp["accept"].replace(",", ", ")
        return [
            (f"How do I use {t}?", f"Choose your file ({acc}), set any options shown, then run the tool and download the result."),
            (f"Is {t} free?", f"Yes. {t} is free to use on Nexora and needs no sign-up."),
            ("Are my files stored?", "Nexora's PDF tools process files in memory and do not store them, as stated on the tool page."),
            ("Which files can I upload?", f"This tool accepts {acc}" + (". You can add several files." if sp["multiple"] else ".")),
        ]

    def route_front(paths):
        rs = app.router.routes
        mine = [r for r in rs if getattr(r, "path", None) in paths]
        for r in mine:
            rs.remove(r)
        rs[0:0] = mine

    # ---- pages
    @app.get("/pdf", response_class=HTMLResponse)
    async def pdf_hub():
        cards = "".join(
            f'<a class="card card-link" href="/pdf/{s}"><h3>{_esc(specs[s]["title"])}</h3><p>{_esc(specs[s]["desc"])}</p>'
            f'<p style="margin-top:12px"><strong style="color:var(--accent)">Open &rarr;</strong></p></a>' for s in order)
        body = ('<section class="page-hero"><div class="container"><span class="tag live">PDF Tools</span>'
                '<h1 style="margin-top:12px">Free PDF Tools - Merge, Split, Compress, Convert</h1>'
                f'<p>{len(order)} free online PDF tools. Merge PDF files, split pages, compress size, convert PDF to Word, Excel, PowerPoint or JPG, and more. No sign-up.</p></div></section>'
                f'<section class="section"><div class="container"><div class="grid">{cards}</div></div></section>')
        return pagefn("Free PDF Tools - Merge, Split, Compress, Convert", META["/pdf"][1], "/pdf", body)

    @app.get("/about", response_class=HTMLResponse)
    async def about():
        return pagefn("About Nexora", META["/about"][1], "/about", ABOUT_BODY)

    @app.get("/og-image.png")
    async def og_image():
        if "png" not in _DONE:
            from PIL import Image, ImageDraw, ImageFont
            im = Image.new("RGB", (1200, 630), (124, 58, 237))
            d = ImageDraw.Draw(im)
            def font(sz):
                for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",):
                    try:
                        return ImageFont.truetype(p, sz)
                    except Exception:
                        pass
                return ImageFont.load_default()
            d.text((80, 190), "Nexora", font=font(110), fill="white")
            d.text((80, 340), "Free PDF Tools & Student Calculators", font=font(48), fill="white")
            d.text((80, 410), "Merge, split, compress, convert. CGPA, SGPA, percentage.", font=font(32), fill=(233, 225, 255))
            b = io.BytesIO()
            im.save(b, "PNG")
            _DONE["png"] = b.getvalue()
        return Response(_DONE["png"], media_type="image/png", headers={"Cache-Control": "public, max-age=86400"})

    old_sitemap = None
    for r in app.router.routes:
        if getattr(r, "path", None) == "/sitemap.xml":
            old_sitemap = r.endpoint

    @app.get("/sitemap.xml")
    async def sitemap2():
        resp = await old_sitemap()
        locs = re.findall(r"<loc>https?://[^/]+([^<]*)</loc>", resp.body.decode())
        paths = ["/", "/pdf", "/about", "/pro"] + locs + ["/pdf/" + s for s in order] + ["/career/" + c for c in careers]
        paths = [p for p in dict.fromkeys(paths) if not p.startswith(("/api", "/auth", "/buy", "/pay-thanks"))]
        urls = "".join(f"<url><loc>{BASE}{p}</loc><lastmod>{LASTMOD}</lastmod></url>" for p in paths)
        return Response('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + urls + "</urlset>", media_type="application/xml")

    app.router.routes[:] = [r for r in app.router.routes if getattr(r, "endpoint", None) is not old_sitemap]
    route_front({"/pdf", "/about", "/og-image.png", "/sitemap.xml"})

    # ---- post-processor
    def related_block(path):
        links = None
        head = "Related tools"
        if path.startswith("/pdf/"):
            slug = path[5:]
            grp = next((gr for gr in PDF_GROUPS if slug in gr), [])
            rel = [s for s in grp if s != slug and s in specs][:5]
            for s in ("merge", "compress", "split"):
                if len(rel) < 6 and s != slug and s not in rel:
                    rel.append(s)
            links = [(f"/pdf/{s}", specs[s]["title"]) for s in rel] + [("/pdf", "All PDF tools")]
        elif path.startswith("/students") or path in ("/vtu-sgpa-calculator", "/vtu-cgpa-calculator", "/cgpa-to-percentage-calculator"):
            links = [(h, t) for h, t in STUDENT_LINKS if h != path]
            head = "More student calculators"
        if not links:
            return ""
        a = "".join(f'<a class="btn ghost" href="{h}">{_esc(t)}</a>' for h, t in links)
        return f'<section class="section"><div class="container"><div class="card"><h2 style="margin-top:0">{head}</h2><div style="display:flex;flex-wrap:wrap;gap:10px">{a}</div></div></div></section>'

    FAQ_RE = re.compile(r"<h3[^>]*>([^<]+)</h3><p>([^<]*)</p>")

    def process(path, doc):
        if "</head>" not in doc or "nx-seo" in doc[:6000]:
            return doc
        # title
        m = re.search(r"<title>(.*?)</title>", doc, re.S)
        title = m.group(1) if m else "Nexora"
        title = re.sub(r"(\s*[|-]\s*Nexora)+\s*$", "", title).strip() + " | Nexora" if not title.endswith("| Nexora") or title.count("Nexora") > 1 else title
        title = re.sub(r"( \| Nexora)( - Nexora)+$", r"\1", title)
        desc_m = re.search(r'<meta name="description" content="([^"]*)"', doc)
        desc = desc_m.group(1) if desc_m else ""
        if path.startswith("/pdf/") and path[5:] in specs:
            title, desc = pdf_meta(path[5:])
        elif path in META:
            title, desc = META[path]
        title, desc = _esc(title) if "&" not in title else title, desc
        title = title.replace("&amp;amp;", "&amp;")
        doc = re.sub(r"<title>.*?</title>", lambda _: f"<title>{title}</title>", doc, count=1, flags=re.S)
        if desc_m:
            doc = doc.replace(desc_m.group(0), f'<meta name="description" content="{desc}"', 1)
        else:
            doc = doc.replace("</title>", f'</title>\n<meta name="description" content="{_esc(desc)}">', 1)
        doc = re.sub(r'<meta property="og:title" content="[^"]*">', lambda _: f'<meta property="og:title" content="{title}">', doc)
        doc = re.sub(r'<meta property="og:description" content="[^"]*">', lambda _: f'<meta property="og:description" content="{desc}">', doc)
        # h1
        if path in H1:
            doc = re.sub(r"(<h1[^>]*>)(.*?)(</h1>)", lambda mm: mm.group(1) + _esc(H1[path]) + mm.group(3), doc, count=1, flags=re.S)
        elif path.startswith("/pdf/") and path[5:] in specs:
            doc = re.sub(r"(<h1[^>]*>)(.*?)(</h1>)", lambda mm: mm.group(1) + _esc(pdf_meta(path[5:])[0].split(" | ")[0]) + mm.group(3), doc, count=1, flags=re.S)
        # head extras
        url = BASE + (path if path != "/" else "/")
        head = ["<!-- nx-seo -->"]
        if 'rel="canonical"' not in doc:
            head.append(f'<link rel="canonical" href="{url}">')
        if 'property="og:url"' not in doc:
            head.append(f'<meta property="og:url" content="{url}">')
        img = BASE + "/og-image.png"
        head.append(f'<meta property="og:image" content="{img}"><meta name="twitter:card" content="summary_large_image">'
                    f'<meta name="twitter:title" content="{title}"><meta name="twitter:description" content="{desc}"><meta name="twitter:image" content="{img}">')
        # JSON-LD
        ld = []
        if path == "/":
            ld.append({"@context": "https://schema.org", "@type": "WebSite", "name": "Nexora", "url": BASE + "/"})
            ld.append({"@context": "https://schema.org", "@type": "Organization", "name": "Nexora", "url": BASE + "/", "logo": BASE + "/og-image.png"})
        crumbs = [("Home", "/")]
        if path.startswith("/pdf/"):
            crumbs += [("PDF Tools", "/pdf"), (specs.get(path[5:], {}).get("title", "PDF tool"), path)]
        elif path.startswith("/students/"):
            crumbs += [("Student Calculators", "/students"), (re.sub(r" \| Nexora$", "", title), path)]
        elif path != "/":
            crumbs += [(re.sub(r" \| Nexora$", "", title), path)]
        if path != "/":
            ld.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": re.sub(r"<[^>]+>", "", _h.unescape(n)), "item": BASE + p} for i, (n, p) in enumerate(crumbs)]})
        if path.startswith("/pdf/") and path[5:] in specs:
            sp = specs[path[5:]]
            ld.append({"@context": "https://schema.org", "@type": "SoftwareApplication", "name": sp["title"], "description": sp["desc"],
                       "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any (web browser)", "url": url,
                       "offers": {"@type": "Offer", "price": "0", "priceCurrency": "INR"}})
        # FAQ
        faq_items, extra_html = [], ""
        is_calc = path.startswith("/students") and path != "/students" or path in EXTRA_FAQ or path.endswith("-calculator")
        existing = FAQ_RE.findall(doc[doc.find("Common questions"):]) if "Common questions" in doc else []
        if path.startswith("/pdf/") and path[5:] in specs:
            faq_items = pdf_faq(path[5:])
            extra_html = '<section class="section"><div class="container"><div class="card"><h2 style="margin-top:0">About this tool</h2><p>' + _esc(
                f"{specs[path[5:]]['title']}: {specs[path[5:]]['desc']} Free and no sign-up.") + "</p><h2>Common questions</h2>" + "".join(
                f"<h3 style='margin:18px 0 6px'>{_esc(q)}</h3><p>{_esc(a)}</p>" for q, a in faq_items) + "</div></div></section>"
        elif is_calc or existing:
            faq_items = [(_h.unescape(q), _h.unescape(a)) for q, a in existing]
            have = {q for q, _ in faq_items}
            more = [x for x in EXTRA_FAQ.get(path, GENERIC_CALC_FAQ if is_calc else []) if x[0] not in have]
            need = max(0, 4 - len(faq_items)) if len(faq_items) < 3 else 0
            more = more[:need] if need else []
            if more:
                add = "".join(f"<h3 style='margin:18px 0 6px'>{_esc(q)}</h3><p>{_esc(a)}</p>" for q, a in more)
                last = None
                for last in FAQ_RE.finditer(doc, doc.find("Common questions")) if existing else []:
                    pass
                if last is not None:
                    doc = doc[:last.end()] + add + doc[last.end():]
                else:
                    extra_html = '<section class="section"><div class="container"><div class="card"><h2 style="margin-top:0">Common questions</h2>' + add + "</div></div></section>"
                faq_items += more
        if faq_items:
            ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq_items]})
        head.extend(_ld(o) for o in ld)
        doc = doc.replace("</head>", "".join(head) + "</head>", 1)
        # nav + body blocks
        if 'href="/pdf"' not in doc.split("</nav>")[0]:
            doc = doc.replace('<a href="/students">Students</a>', '<a href="/students">Students</a><a href="/pdf">PDF Tools</a>', 1)
        intro = INTRO.get(path)
        if intro:
            blk = f'<section class="section" style="padding-bottom:0"><div class="container"><p style="max-width:780px">{_esc(intro)}</p></div></section>'
            i = doc.find("</section>", doc.find("<h1"))
            if i > 0:
                doc = doc[:i + 10] + blk + doc[i + 10:]
        tail = extra_html + related_block(path)
        if tail:
            doc = doc.replace("</main>", tail + "</main>", 1)
        foot = '<div class="container" style="padding:14px 0;font-size:14px;display:flex;flex-wrap:wrap;gap:6px 16px"><strong>Popular:</strong>' + "".join(
            f'<a href="{h}">{_esc(t)}</a>' for h, t in FOOT_LINKS) + "</div>"
        doc = doc.replace("</footer>", foot + "</footer>", 1)
        return doc

    @app.middleware("http")
    async def seo_mw(request: Request, call_next):
        resp = await call_next(request)
        p = request.url.path
        if (request.method != "GET" or resp.status_code != 200 or p.startswith(("/api", "/auth", "/buy", "/pay-thanks", "/og-image"))
                or "text/html" not in resp.headers.get("content-type", "")):
            return resp
        body = b"".join([c async for c in resp.body_iterator])
        try:
            out = process(p.rstrip("/") or "/", body.decode("utf-8")).encode("utf-8")
        except Exception as e:  # never break a page for SEO
            print("SEO_ERR", p, repr(e))
            out = body
        h = {k: v for k, v in resp.headers.items() if k.lower() not in ("content-length", "content-type")}
        return Response(out, status_code=200, headers=h, media_type="text/html")
