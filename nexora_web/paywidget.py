"""Small reusable Razorpay checkout widget for pay-only pages (Excel service, Pro).

The widget stays hidden until /api/config reports payments_ready, so nothing
shows before payments are switched on.
"""

PAY_WIDGET = r"""
<div class="nxpay" id="nxpay___PID__" data-product="__PRODUCT__" hidden style="margin:22px 0;padding:20px;border:1px solid #ded4f6;border-radius:16px;background:#faf5ff">
<h3 style="margin:0 0 6px">__TITLE__</h3>
<p style="margin:0 0 12px;line-height:1.6">__TEXT__</p>
<button class="btn nxpay-btn" type="button">__BUTTON__</button>
<p class="nxpay-msg" role="status" style="margin:12px 0 0;font-size:15px"></p>
</div>
<script>
(function(){
var box=document.getElementById('nxpay___PID__');if(!box)return;
var product=box.getAttribute('data-product'),btn=box.querySelector('.nxpay-btn'),msg=box.querySelector('.nxpay-msg');
var DONE=__DONE__;
function say(s){msg.textContent=s}
function login(){location.href='/login?next='+encodeURIComponent(location.pathname)}
fetch('/api/config').then(function(r){return r.json()}).then(function(c){if(c.payments_ready){box.hidden=false;var pr=document.querySelectorAll('.nxpay-hide-when-ready');for(var i=0;i<pr.length;i++)pr[i].hidden=true}}).catch(function(){});
fetch('/api/purchases').then(function(r){return r.json()}).then(function(j){if(product==='pro_pass'&&j.pro){btn.hidden=true;msg.textContent='Nexora Pro is active on your account. Thank you!'}}).catch(function(){});
btn.onclick=function(){
btn.disabled=true;say('Starting secure checkout...');
fetch('/api/pay/order',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({product:product})}).then(function(r){return r.json()}).then(function(o){
btn.disabled=false;
if(o.login){login();return}
if(o.error){say(o.error);return}
var s=document.createElement('script');s.src='https://checkout.razorpay.com/v1/checkout.js';
s.onerror=function(){say('Checkout could not load. Please try again.')};
s.onload=function(){new Razorpay({key:o.key_id,amount:o.amount,currency:o.currency,order_id:o.order_id,name:'Nexora',description:o.name,prefill:{email:o.email},theme:{color:'#7c3aed'},handler:function(resp){
say('Verifying payment...');
fetch('/api/pay/verify',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(resp)}).then(function(r){return r.json()}).then(function(v){
if(v.ok){btn.hidden=true;msg.innerHTML=DONE.replace('__ORDER__',String(resp.razorpay_order_id).replace(/[^A-Za-z0-9_]/g,''))}
else say(v.error||'Payment could not be verified. Do not pay again until the payment status is checked.')
}).catch(function(){say('Verification interrupted. Do not pay again until the payment status is checked.')})
}}).open()};
document.body.append(s)
}).catch(function(){btn.disabled=false;say('Could not start checkout. Please try again.')})
};
})();
</script>
"""


def pay_widget(pid: str, product: str, title: str, text: str, button: str, done_html: str) -> str:
    import json
    return (PAY_WIDGET.replace("__PID__", pid).replace("__PRODUCT__", product)
            .replace("__TITLE__", title).replace("__TEXT__", text)
            .replace("__BUTTON__", button).replace("__DONE__", json.dumps(done_html)))


EXCEL_PAY = pay_widget(
    "excel", "excel_service", "Pay online for Excel cleanup - Rs 199 per file",
    "Pay securely by UPI or card through Razorpay, then send your file on WhatsApp with your order ID. Delivery within 24 hours of confirming the scope. You can also order on WhatsApp without paying here.",
    "Pay Rs 199",
    "Payment received. Your order ID is <strong>__ORDER__</strong>. Now <a href=\"https://wa.me/919353006448?text=Hi%2C+I+paid+Rs+199+for+Excel+cleanup.+Order+ID%3A+__ORDER__\" rel=\"noopener noreferrer\">send your file on WhatsApp</a> with this order ID.")

PRO_PAY = pay_widget(
    "pro", "pro_pass", "Get Nexora Pro for 30 days",
    "Unlimited jobs, bigger files and priority speed. First month Rs 99, then Rs 149 per 30 days. A one-time payment, no auto-renewal. Sign in when you are ready to pay.",
    "Get Pro",
    "Payment received. Nexora Pro is active on your account for 30 days. Thank you!")
