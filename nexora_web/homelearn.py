"""Homepage learning-first block for Nexora."""

_CSS = """<style>
.hl-hero{display:grid;grid-template-columns:1fr;color:#fff}
.hl-half{padding:30px 20px 36px;display:flex;align-items:center;justify-content:center}
.hl-hl{background:linear-gradient(135deg,#7c3aed 0%,#db2777 100%)}
.hl-hr{background:linear-gradient(135deg,#2563eb 0%,#7c3aed 100%)}
.hl-half .hl-wrap{max-width:640px;width:100%}
@media (min-width:860px){.hl-hero{grid-template-columns:1fr 1fr}.hl-half{padding:38px 28px 44px}}
.hl-wrap{display:flex;flex-wrap:wrap;align-items:center;gap:22px;justify-content:space-between}
.hl-copy{flex:1 1 330px;min-width:0}
.hl-hero h1{margin:0 0 10px;font-size:clamp(28px,6vw,44px);line-height:1.12;color:#fff}
.hl-sub{font-size:18px;font-weight:600;margin:0 0 6px;opacity:.97}
.hl-sub2{font-size:16px;margin:0 0 18px;opacity:.92}
.hl-btns{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:16px}
.hl-btn{display:inline-block;text-decoration:none;font-weight:700;border-radius:999px;padding:12px 22px;font-size:16px}
.hl-b1{background:#fff;color:#7c3aed;box-shadow:0 6px 18px rgba(0,0,0,.18)}
.hl-b1b{background:#fff;color:#2563eb;box-shadow:0 6px 18px rgba(0,0,0,.18)}
.hl-b2{background:rgba(255,255,255,.18);color:#fff;border:2px solid rgba(255,255,255,.85)}
.hl-trust{display:flex;flex-wrap:wrap;gap:8px 16px;font-size:14px;font-weight:600;opacity:.96}
.hl-av{flex:0 1 250px;display:flex;flex-direction:column;align-items:center;gap:10px;margin:0 auto}
.hl-bubble{background:#fff;color:#4c1d95;font-weight:700;border-radius:18px;padding:10px 16px;font-size:16px;text-align:center;min-width:190px;position:relative;box-shadow:0 8px 22px rgba(0,0,0,.2);transition:opacity .3s}
.hl-bubbleb{color:#1e3a8a}
.hl-bubbleb:after{border-top-color:#fff}
.hl-bubble:after{content:"";position:absolute;left:50%;bottom:-9px;margin-left:-9px;border:9px solid transparent;border-bottom:0;border-top-color:#fff}
.hl-face{width:170px;height:170px;animation:hlf 3.2s ease-in-out infinite}
@keyframes hlf{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
.hl-blink{animation:hlb 4s infinite;transform-origin:center}
@keyframes hlb{0%,92%,100%{transform:scaleY(1)}95%{transform:scaleY(.1)}}
.hl-hear{background:#fff;color:#7c3aed;border:0;border-radius:999px;font-weight:700;font-size:15px;padding:10px 20px;cursor:pointer;box-shadow:0 6px 16px rgba(0,0,0,.18)}
.hl-name{font-size:13px;opacity:.9;margin-top:-4px}
.hl-cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:16px;margin-top:-22px;position:relative}
.hl-card{display:block;text-decoration:none;color:#fff;border-radius:20px;padding:20px;box-shadow:0 10px 26px rgba(0,0,0,.14)}
.hl-card .e{font-size:34px;line-height:1}
.hl-card h3{margin:10px 0 4px;font-size:21px;color:#fff}
.hl-card p{margin:0 0 12px;font-size:15px;opacity:.96}
.hl-card span{display:inline-block;background:rgba(255,255,255,.25);border-radius:999px;padding:6px 14px;font-weight:700;font-size:14px}
.hl-c1{background:linear-gradient(135deg,#8b5cf6,#6366f1)}
.hl-c2{background:linear-gradient(135deg,#ec4899,#f43f5e)}
.hl-c3{background:linear-gradient(135deg,#f59e0b,#ef4444)}
.hl-pdfh{margin:0 0 6px}
.hl-chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}
.hl-chips a{background:#f3effd;color:#6d28d9;border-radius:999px;padding:7px 14px;font-weight:600;font-size:14px;text-decoration:none}
.hl-sl{margin:18px 0 0;position:relative}
.hl-track{display:flex;overflow-x:auto;scroll-snap-type:x mandatory;-webkit-overflow-scrolling:touch;scrollbar-width:none}
.hl-track::-webkit-scrollbar{display:none}
.hl-slide{flex:0 0 78%;margin-right:12px;scroll-snap-align:start;box-sizing:border-box;color:#fff;text-decoration:none;padding:20px 18px 30px;min-height:170px;display:block;border-radius:18px}
@media (min-width:600px){.hl-slide{flex-basis:calc(50% - 6px)}}
@media (min-width:900px){.hl-slide{flex-basis:calc(33.333% - 8px)}}
.hl-slide .e{font-size:32px;line-height:1}
.hl-slide h3{margin:8px 0 6px;font-size:20px;color:#fff}
.hl-slide p{margin:0 0 12px;font-size:15px;opacity:.96}
.hl-slide span{display:inline-block;background:rgba(255,255,255,.25);border-radius:999px;padding:6px 14px;font-weight:700;font-size:14px}
.hl-s1{background:linear-gradient(135deg,#7c3aed,#db2777)}
.hl-s2{background:linear-gradient(135deg,#2563eb,#7c3aed)}
.hl-s3{background:linear-gradient(135deg,#f59e0b,#ef4444)}
.hl-s4{background:linear-gradient(135deg,#0d9488,#2563eb)}
.hl-s5{background:linear-gradient(135deg,#4f46e5,#0ea5e9)}
.hl-s6{background:linear-gradient(135deg,#be185d,#7c3aed)}
.hl-s7{background:linear-gradient(135deg,#059669,#0d9488)}
.hl-s8{background:linear-gradient(135deg,#ea580c,#db2777)}
.hl-s9{background:linear-gradient(135deg,#2563eb,#0891b2)}
.hl-s10{background:linear-gradient(135deg,#7c3aed,#2563eb)}
.hl-s11{background:linear-gradient(135deg,#d97706,#be185d)}
.hl-s12{background:linear-gradient(135deg,#475569,#7c3aed)}
.hl-robot{width:150px;height:150px;animation:hlf 3.2s ease-in-out infinite}
.hl-dots{display:flex;justify-content:center;gap:7px;margin-top:12px}
.hl-dots i{width:8px;height:8px;border-radius:50%;background:#d6cdee;display:block}
.hl-dots i.on{background:#7c3aed;width:20px;border-radius:8px}
@media (prefers-reduced-motion:reduce){.hl-face,.hl-blink,.hl-robot{animation:none}}
</style>"""

_AVATAR = """<svg class="hl-face" viewBox="0 0 200 200" role="img" aria-label="Anaya, your AI teacher">
<circle cx="100" cy="100" r="96" fill="#fff" opacity=".22"/>
<path d="M36 110c-4-54 30-84 64-84s68 30 64 84c-4 40-12 62-12 62H48s-8-22-12-62z" fill="#3b1d0f"/>
<rect x="84" y="140" width="32" height="30" rx="10" fill="#e8a37c"/>
<path d="M50 200c4-30 26-42 50-42s46 12 50 42z" fill="#facc15"/>
<ellipse cx="100" cy="102" rx="46" ry="54" fill="#f2b48c"/>
<path d="M54 98c0-38 20-56 46-56s46 18 46 56c-12-20-30-30-46-30s-34 10-46 30z" fill="#3b1d0f"/>
<g class="hl-blink"><ellipse cx="82" cy="108" rx="6" ry="8" fill="#2b1608"/><ellipse cx="118" cy="108" rx="6" ry="8" fill="#2b1608"/>
<circle cx="84" cy="105" r="2" fill="#fff"/><circle cx="120" cy="105" r="2" fill="#fff"/></g>
<path d="M70 94q12-8 24-2M106 92q12-6 24 2" stroke="#3b1d0f" stroke-width="3" fill="none" stroke-linecap="round"/>
<circle cx="70" cy="126" r="7" fill="#f472b6" opacity=".45"/><circle cx="130" cy="126" r="7" fill="#f472b6" opacity=".45"/>
<path d="M84 130q16 16 32 0" stroke="#b91c1c" stroke-width="4" fill="#fff" stroke-linecap="round" stroke-linejoin="round"/>
<circle cx="100" cy="124" r="2.2" fill="#d4a017" opacity="0"/>
</svg>"""

_ROBOT = """<svg class="hl-robot" viewBox="0 0 200 200" role="img" aria-label="AI guide robot">
<circle cx="100" cy="100" r="96" fill="#fff" opacity=".22"/>
<line x1="100" y1="34" x2="100" y2="52" stroke="#fff" stroke-width="5" stroke-linecap="round"/><circle cx="100" cy="30" r="7" fill="#fbbf24"/>
<rect x="46" y="52" width="108" height="92" rx="26" fill="#fff"/>
<rect x="30" y="86" width="14" height="28" rx="7" fill="#c7d2fe"/><rect x="156" y="86" width="14" height="28" rx="7" fill="#c7d2fe"/>
<g class="hl-blink"><circle cx="78" cy="94" r="13" fill="#2563eb"/><circle cx="122" cy="94" r="13" fill="#2563eb"/>
<circle cx="82" cy="90" r="4" fill="#fff"/><circle cx="126" cy="90" r="4" fill="#fff"/></g>
<path d="M78 120q22 16 44 0" stroke="#7c3aed" stroke-width="5" fill="none" stroke-linecap="round"/>
<rect x="70" y="148" width="60" height="34" rx="14" fill="#c7d2fe"/><text x="100" y="172" text-anchor="middle" font-family="Arial,sans-serif" font-weight="800" font-size="20" fill="#4338ca">AI</text>
</svg>"""

_JS = """<script>
(function(){
var G=[["Hello! I am Anaya. Let's learn English!","en-IN"],["ನಮಸ್ಕಾರ! ನಾನು ಅನಾಯಾ. ಇಂಗ್ಲಿಷ್ ಕಲಿಯೋಣ!","kn-IN"],["नमस्ते! मैं अनाया हूँ। आइए अंग्रेज़ी सीखें!","hi-IN"]];
var i=0,b=document.getElementById("hlBubble");
if(!b)return;
setInterval(function(){i=(i+1)%G.length;b.style.opacity=0;setTimeout(function(){b.textContent=G[i][0];b.style.opacity=1},250)},3200);
var h=document.getElementById("hlHear");
h.addEventListener("click",function(){
 if(!("speechSynthesis" in window)){location.href="/english";return}
 try{speechSynthesis.cancel();var u=new SpeechSynthesisUtterance(G[i][0]);u.lang=G[i][1];u.rate=.9;
 var vs=speechSynthesis.getVoices();for(var k=0;k<vs.length;k++){if(vs[k].lang&&vs[k].lang.replace("_","-").indexOf(G[i][1].slice(0,2))===0){u.voice=vs[k];break}}
 speechSynthesis.speak(u)}catch(e){location.href="/english"}
});
})();
</script>"""


_SLIDES = """<section class="section" style="padding-bottom:0"><div class="container"><div class="hl-sl" id="hlSl">
<div class="hl-track" id="hlTrack">
 <a class="hl-slide hl-s1" href="/english"><div class="e">&#128483;&#65039;</div><h3>Learn English with an AI teacher</h3><p>Spoken English practice in Kannada + English. Free to start.</p><span>Start learning &rarr;</span></a>
 <a class="hl-slide hl-s2" href="/ai"><div class="e">&#129302;</div><h3>Learn AI from A to Z</h3><p>Simple lessons for beginners in Kannada, Hindi and English.</p><span>Explore AI &rarr;</span></a>
 <a class="hl-slide hl-s3" href="/english#/kids"><div class="e">&#129490;</div><h3>Kids Zone</h3><p>Fun, safe lessons for children with an Ask your teacher box.</p><span>Open Kids Zone &rarr;</span></a>
 <a class="hl-slide hl-s4" href="/pdf"><div class="e">&#128196;</div><h3>Free PDF tools</h3><p>Merge, split, compress, convert and edit PDFs in seconds.</p><span>Open PDF tools &rarr;</span></a>
 <a class="hl-slide hl-s5" href="/document-ai"><div class="e">&#128269;</div><h3>Document AI</h3><p>Summarize documents, ask questions and pull out data.</p><span>Try Document AI &rarr;</span></a>
 <a class="hl-slide hl-s6" href="/hr-career"><div class="e">&#128188;</div><h3>HR &amp; Career AI</h3><p>Resume, ATS, JD and cover letter tools in one place.</p><span>Open HR &amp; Career &rarr;</span></a>
 <a class="hl-slide hl-s7" href="/resume-builder"><div class="e">&#128221;</div><h3>Resume Builder</h3><p>Professional CV, ready to download. Just &#8377;99.</p><span>Build my resume &rarr;</span></a>
 <a class="hl-slide hl-s8" href="/jd-builder"><div class="e">&#127919;</div><h3>JD Builder</h3><p>Write a clear job description for hiring. Just &#8377;99.</p><span>Build a JD &rarr;</span></a>
 <a class="hl-slide hl-s9" href="/students"><div class="e">&#127891;</div><h3>Student tools</h3><p>SGPA and CGPA calculators, attendance, study planner and more.</p><span>Open Students hub &rarr;</span></a>
 <a class="hl-slide hl-s10" href="/hr/calculators"><div class="e">&#129518;</div><h3>Salary &amp; CTC calculators</h3><p>CTC, salary, increment, gratuity and notice period.</p><span>Calculate now &rarr;</span></a>
 <a class="hl-slide hl-s11" href="/hr/documents"><div class="e">&#128193;</div><h3>HR letter templates</h3><p>Ready-to-use HR letters and documents for work.</p><span>See templates &rarr;</span></a>
 <a class="hl-slide hl-s12" href="/pro"><div class="e">&#11088;</div><h3>Nexora Pro</h3><p>Unlimited use of every tool. &#8377;99 first month.</p><span>See Pro &rarr;</span></a>
</div>
<div class="hl-dots" id="hlDots"><i class="on"></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div>
</div></div></section>"""

_SLJS = """<script>
(function(){
var t=document.getElementById("hlTrack"),d=document.getElementById("hlDots");
if(!t||!d)return;
var S=t.children,D=d.children,n=S.length,i=0,hold=0;
function w(){return S.length>1?S[1].offsetLeft-S[0].offsetLeft:t.clientWidth}
function mark(){var k=Math.round(t.scrollLeft/(w()||1));if(k<0)k=0;if(k>=n)k=n-1;i=k;for(var j=0;j<D.length;j++)D[j].className=j===k?"on":""}
t.addEventListener("scroll",mark,{passive:true});
function pause(){hold=Date.now()+8000}
t.addEventListener("touchstart",pause,{passive:true});
t.addEventListener("mouseenter",pause);
t.addEventListener("pointerdown",pause);
var mq=window.matchMedia&&matchMedia("(min-width:900px) and (hover:hover)");
if(!mq||!mq.matches)return;
if(matchMedia("(prefers-reduced-motion:reduce)").matches)return;
setInterval(function(){
 if(document.hidden||Date.now()<hold)return;
 var max=t.scrollWidth-t.clientWidth,x=t.scrollLeft+w();
 if(x>max+2)x=0;
 t.scrollTo({left:x,behavior:"smooth"})
},4500);
})();
</script>"""


def block() -> str:
    return f"""{_CSS}
<section class="hl-hero">
 <div class="hl-half hl-hl"><div class="hl-wrap">
  <div class="hl-copy">
   <h2 class="hl-h" style="margin:0 0 10px;font-size:clamp(26px,5vw,38px);line-height:1.12;color:#fff">Learn English with your own talking AI teacher</h2>
   <p class="hl-sub">Kannada + English &nbsp;|&nbsp; Hindi + English</p>
   <p class="hl-sub2">Short lessons, quizzes, streaks and rewards. Ask your teacher anything.</p>
   <div class="hl-btns"><a class="hl-btn hl-b1" href="/english">Start learning free</a></div>
   <div class="hl-trust"><span>&#10003; No sign-up</span><span>&#10003; Safe for kids</span></div>
  </div>
  <div class="hl-av">
   <div class="hl-bubble" id="hlBubble" aria-live="polite">Hello! I am Anaya. Let's learn English!</div>
   {_AVATAR}
   <button class="hl-hear" id="hlHear" type="button">&#128266; Hear Anaya</button>
   <div class="hl-name">Anaya, your AI teacher</div>
  </div>
 </div></div>
 <div class="hl-half hl-hr"><div class="hl-wrap">
  <div class="hl-copy">
   <h2 class="hl-h" style="margin:0 0 10px;font-size:clamp(26px,5vw,38px);line-height:1.12;color:#fff">Learn AI from A to Z</h2>
   <p class="hl-sub">Kannada &nbsp;|&nbsp; Hindi &nbsp;|&nbsp; English</p>
   <p class="hl-sub2">Simple lessons for beginners. Use AI for study, jobs and daily life, step by step.</p>
   <div class="hl-btns"><a class="hl-btn hl-b1b" href="/ai">Start AI free</a></div>
   <div class="hl-trust"><span>&#10003; No sign-up</span><span>&#10003; Free to start</span></div>
  </div>
  <div class="hl-av">
   <div class="hl-bubble hl-bubbleb">Hi! Let's learn AI together!</div>
   {_ROBOT}
   <div class="hl-name">Your AI A-to-Z guide</div>
  </div>
 </div></div>
</section>
{_SLIDES}
<section class="section" style="padding-bottom:0"><div class="container">
 <h2 class="hl-pdfh">Free PDF, document &amp; career tools</h2>
 <p style="margin:0;color:#6b7280">Merge, split and compress PDFs, summarize documents, build resumes and more.</p>
 <div class="hl-chips"><a href="/pdf">All PDF tools</a><a href="/pdf/merge">Merge PDF</a><a href="/pdf/compress">Compress PDF</a><a href="/document-ai">Document AI</a><a href="/resume-builder">Resume Builder</a><a href="/students">Student tools</a></div>
</div></section>
{_JS}
{_SLJS}"""
