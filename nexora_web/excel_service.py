"""Excel cleanup and PDF/table-to-Excel service page (online only, no address)."""

EXCEL_WHATSAPP = "https://wa.me/919353006448?text=Namaskara%21+I+found+Nexora%27s+Excel+and+PDF-to-Excel+page.+I%27d+like+help+with%3A%0AFile+type%3A%0AWhat+I+need%3A%0ADeadline%3A"

EXCEL_TITLE = "Excel cleanup & PDF to Excel conversion"
EXCEL_DESC = "Messy Excel sheet or table trapped in a PDF? Get a clean, usable Excel file through WhatsApp. Rs 199 per file, delivered within 24 hours. Fully online."
EXCEL_META = (
    '<link rel="canonical" href="https://nexora-web-q7rn.onrender.com/excel-service">'
    '<meta name="robots" content="index,follow">'
    '<meta property="og:title" content="Excel cleanup and PDF to Excel - Nexora">'
    '<meta property="og:description" content="Clean Excel files and PDF tables turned into Excel. Rs 199 per file, delivery within 24 hours.">'
    '<meta property="og:url" content="https://nexora-web-q7rn.onrender.com/excel-service">'
    '<meta property="og:type" content="website">'
)

EXCEL_BODY = """
<style>
.xs-hero{padding:56px 0 34px;background:linear-gradient(135deg,#faf5ff,#fff1f9)}
.xs-hero h1{font-size:clamp(32px,5vw,52px);line-height:1.12;margin:16px 0}
.xs-hero p{font-size:18px;max-width:700px;line-height:1.65}
.xs-label{font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:#7c3aed}
.xs-actions{display:flex;gap:12px;flex-wrap:wrap;margin:24px 0 12px}.xs-actions a{min-height:48px;display:inline-flex;align-items:center}
.xs-small{font-size:14px!important;color:#6b7280}
.xs-section{padding:36px 0}.xs-section h2{font-size:28px;margin:0 0 16px}
.xs-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.xs-box{background:white;border:1px solid #eee5f3;border-radius:16px;padding:24px}
.xs-box h3{margin:0 0 10px;font-size:19px}.xs-box p{line-height:1.65;margin:0;color:#5b5263}
.xs-ba{display:grid;grid-template-columns:1fr 1fr;gap:20px}
.xs-card{background:white;border:1px solid #eee5f3;border-radius:16px;padding:18px;overflow:hidden}
.xs-card h3{margin:0 0 4px;font-size:18px}.xs-card .cap{font-size:13px;color:#6b7280;margin:0 0 12px}
.xs-tag{display:inline-block;font-size:12px;font-weight:700;padding:3px 10px;border-radius:99px;margin-bottom:10px}
.xs-before .xs-tag{background:#fee2e2;color:#991b1b}.xs-after .xs-tag{background:#dcfce7;color:#166534}
.xs-wrap{overflow-x:auto}
table.xs-t{border-collapse:collapse;width:100%;font-size:13px;font-family:Arial,Helvetica,sans-serif;min-width:330px}
table.xs-t td,table.xs-t th{border:1px solid #d9d4e0;padding:5px 8px;text-align:left;white-space:nowrap}
table.xs-t th{background:#f3effa;font-weight:700}
.xs-before table.xs-t td{color:#444}
.xs-pdf{background:#fff;border:1px solid #d9d4e0;border-radius:8px;padding:14px;font-family:Georgia,serif;font-size:13px;line-height:1.9;color:#333}
.xs-pdf .row{display:flex;gap:18px;border-bottom:1px dotted #bbb}.xs-pdf .row span{flex:1}
.xs-pdf .row.h{font-weight:700;border-bottom:1px solid #333}
.xs-note{background:#faf5ff;border-radius:14px;padding:22px;line-height:1.7}
.xs-price{background:white;border:2px solid #c4b5fd;border-radius:18px;padding:26px;max-width:520px}
.xs-price strong{font-size:38px;color:#6d28d9}.xs-price ul{margin:12px 0 0;padding-left:20px;line-height:1.8;color:#5b5263}
.xs-faq details{border-bottom:1px solid #eee5f3;padding:16px 0}.xs-faq summary{font-weight:650;cursor:pointer}.xs-faq p{line-height:1.7;color:#5b5263}
@media(max-width:700px){.xs-grid,.xs-ba{grid-template-columns:1fr}.xs-hero{padding:30px 0}.xs-section{padding:26px 0}.xs-actions a{width:100%;justify-content:center}.xs-box{padding:20px}}
</style>
<section class="xs-hero"><div class="container">
<span class="xs-label">Nexora / Online document help</span>
<h1>Messy sheet or PDF table?<br>Get a clean Excel file.</h1>
<p>We tidy untidy Excel files and turn tables in PDFs into editable Excel sheets. Everything is handled online through WhatsApp. No shop visit or physical meeting needed.</p>
<div class="xs-actions"><a class="btn" href="__WHATSAPP__" rel="noopener noreferrer">Send your file on WhatsApp</a><a class="btn ghost" href="#samples">See illustrative samples</a></div>
<p class="xs-small">Rs 199 per file of reasonable size. Delivery within 24 hours. No payment is taken on this page.</p>
</div></section>

<section class="xs-section"><div class="container"><h2>What we can do</h2><div class="xs-grid">
<article class="xs-box"><h3>Excel cleanup</h3><p>Remove duplicate rows and blank rows, trim extra spaces, fix inconsistent dates, numbers and text, split or join columns, and make headers and formatting consistent.</p></article>
<article class="xs-box"><h3>PDF table to Excel</h3><p>Move a table from a text-based PDF into rows and columns you can sort, filter and calculate with. Each table is checked against the original.</p></article>
<article class="xs-box"><h3>Simple formatting and totals</h3><p>Add clear headers, column widths, number formats, and basic totals or filters where you ask for them, so the sheet is ready to use or print.</p></article>
</div></div></section>

<section class="xs-section" id="samples"><div class="container"><h2>Illustrative before and after</h2>
<p class="xs-small" style="margin-bottom:16px">These are made-up examples with fictional data, shown only to explain the kind of change. They are not customer files or past results.</p>
<div class="xs-ba" style="margin-bottom:20px">
<div class="xs-card xs-before"><span class="xs-tag">BEFORE (illustrative)</span><h3>Messy Excel sheet</h3><p class="cap">Mixed date formats, extra spaces, a duplicate row, a blank row.</p><div class="xs-wrap"><table class="xs-t">
<tr><td>item </td><td>  Qty</td><td>date</td><td>Amount</td></tr>
<tr><td>Pen box</td><td>10</td><td>5/1/2026</td><td>250 rs</td></tr>
<tr><td>pen box</td><td>10</td><td>5/1/2026</td><td>250 rs</td></tr>
<tr><td>&nbsp;</td><td></td><td></td><td></td></tr>
<tr><td>File  folder</td><td>four</td><td>06-Jan-26</td><td>Rs.120</td></tr>
<tr><td>Stapler</td><td>2</td><td>2026/01/07</td><td>180</td></tr>
</table></div></div>
<div class="xs-card xs-after"><span class="xs-tag">AFTER (illustrative)</span><h3>Clean Excel sheet</h3><p class="cap">One date format, numbers as numbers, duplicates and blanks removed.</p><div class="xs-wrap"><table class="xs-t">
<tr><th>Item</th><th>Qty</th><th>Date</th><th>Amount (Rs)</th></tr>
<tr><td>Pen box</td><td>10</td><td>05-Jan-2026</td><td>250</td></tr>
<tr><td>File folder</td><td>4</td><td>06-Jan-2026</td><td>120</td></tr>
<tr><td>Stapler</td><td>2</td><td>07-Jan-2026</td><td>180</td></tr>
<tr><th colspan="3">Total</th><th>550</th></tr>
</table></div></div></div>
<div class="xs-ba">
<div class="xs-card xs-before"><span class="xs-tag">BEFORE (illustrative)</span><h3>Table inside a PDF</h3><p class="cap">Text you cannot sort or calculate with.</p><div class="xs-pdf" aria-label="Illustrative PDF table">
<div class="row h"><span>Name</span><span>Dept</span><span>Marks</span></div>
<div class="row"><span>Asha R</span><span>Sales</span><span>78</span></div>
<div class="row"><span>Kiran M</span><span>Stores</span><span>64</span></div>
<div class="row"><span>Divya S</span><span>Sales</span><span>91</span></div></div></div>
<div class="xs-card xs-after"><span class="xs-tag">AFTER (illustrative)</span><h3>Editable Excel table</h3><p class="cap">Same rows, now in cells you can sort and filter.</p><div class="xs-wrap"><table class="xs-t">
<tr><th>Name</th><th>Dept</th><th>Marks</th></tr>
<tr><td>Asha R</td><td>Sales</td><td>78</td></tr>
<tr><td>Kiran M</td><td>Stores</td><td>64</td></tr>
<tr><td>Divya S</td><td>Sales</td><td>91</td></tr>
</table></div></div></div>
</div></section>

<section class="xs-section"><div class="container"><h2>From first message to final file</h2><div class="xs-grid">
<article class="xs-box"><h3>1. Send a sample</h3><p>Message on WhatsApp with what you need. A redacted or sample copy is enough for us to confirm if the job is a fit.</p></article>
<article class="xs-box"><h3>2. Confirm the scope</h3><p>We confirm what will be done, the file size and the format you want before work starts. Price is Rs 199 per file of reasonable size, delivered within 24 hours. Payment details are shared on WhatsApp.</p></article>
<article class="xs-box"><h3>3. Check your file</h3><p>Open the finished Excel file and check it against your original before relying on it. Tell us on WhatsApp if something in the agreed scope was missed.</p></article>
</div></div></section>

<section class="xs-section"><div class="container"><div class="xs-price"><span class="xs-label">Simple pricing</span><br><strong>Rs 199</strong> per file
<ul><li>Reasonable size: roughly up to 10 PDF pages or a few thousand rows. Bigger files are quoted first.</li><li>Delivery within 24 hours of confirming the scope.</li><li>Fully online through WhatsApp.</li><li>No payment is taken on this page.</li></ul></div></div></section>

<section class="xs-section"><div class="container"><div class="xs-note"><strong>What to know before you send a file.</strong><br>Scanned or blurry PDFs, photos of tables and handwritten pages are harder and may not convert accurately. We will tell you before starting if your file looks like this. We do not guarantee that a file will be free of every error, so please check important numbers against your original. Formulas and macros are not rebuilt unless agreed in advance. Remove Aadhaar/PAN numbers, bank details and other sensitive data before sending, and never send passwords or OTPs. This service is fully online and no address or meeting location is published here.</div></div></section>

<section class="xs-section"><div class="container xs-faq"><h2>Before you message</h2>
<details><summary>How much does it cost?</summary><p>Rs 199 per file of reasonable size, delivered within 24 hours. Larger or more complicated files are quoted on WhatsApp before any work starts. Nothing is charged automatically on this page.</p></details>
<details><summary>Do I need to meet someone?</summary><p>No. Requests and delivery are handled online through WhatsApp. No in-person appointments are offered.</p></details>
<details><summary>Can you convert a scanned PDF?</summary><p>Sometimes, but accuracy depends on the scan quality. Clear text-based PDFs work best. Send a sample page and we will tell you honestly if it is a good fit.</p></details>
<details><summary>Do you keep my file?</summary><p>Share only what is needed for the job. See our <a href="/privacy">privacy policy</a> for how data is handled.</p></details>
<details><summary>Can I do simple conversions myself?</summary><p>Yes. Nexora has free <a href="/">PDF tools</a> and <a href="/document-ai">Document AI</a>. Limits and any paid options are shown in the app.</p></details>
<div class="xs-actions"><a class="btn" href="__WHATSAPP__" rel="noopener noreferrer">Discuss your file on WhatsApp</a></div>
</div></section>
""".replace("__WHATSAPP__", EXCEL_WHATSAPP)
