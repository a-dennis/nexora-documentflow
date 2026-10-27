PILOT_HTML='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Nexora Publisher - private pilot</title><style>\n*{box-sizing:border-box}body{font:16px/1.5 system-ui;margin:0;background:#f5f7fb;color:#14213d}main{max-width:650px;margin:auto;padding:24px 18px}section{background:white;border:1px solid #dfe4ec;border-radius:12px;padding:18px;margin:20px 0}h1{font-size:28px}h2{font-size:20px}label{display:block;font-weight:600;margin:16px 0 6px}input,textarea,select{width:100%;font:inherit;padding:12px;border:1px solid #8994a6;border-radius:6px;min-height:48px}textarea{min-height:120px}button{font:600 16px system-ui;padding:14px;min-height:48px;width:100%;border:0;border-radius:8px;background:#14213d;color:white;margin-top:16px}button:disabled{background:#dfe4eb;color:#536174}.note{background:#fff4d6;padding:14px;border-radius:8px}.sub{color:#536174;font-size:14px}.data{white-space:pre-wrap;overflow-wrap:anywhere}#err{color:#a52222}video{max-width:100%}</style>\n<main><p class="sub">NEXORA / OWNER-ONLY PILOT</p><h1>Upload once. Review before posting.</h1><p class="note">__TRIAL_NOTICE__ Facebook and Instagram are not connected. They will not receive your video.</p><section><h2>Video and details</h2><form id="draft"><label for="video">MP4 video</label><input id="video" name="video" type="file" accept="video/mp4" required><p class="sub">Pilot cap: 20 MiB, 3-90 seconds, H.264 MP4. One Private trial upload. Up to 5 reviews. Use a small clip you have rights to upload.</p><label for="title">Title</label><input id="title" name="title" maxlength="100" required><label for="caption">Description</label><textarea id="caption" name="caption" maxlength="2000"></textarea><label for="made_for_kids">Is this made for kids?</label><select id="made_for_kids" name="made_for_kids" required><option value="">Choose the audience</option><option value="no">No, not made for kids</option><option value="yes">Yes, made for kids</option></select><p class="sub">Destination: Nexora Facts &amp; Cinema. Visibility: Private. Other viewers cannot watch a private video unless you share access through YouTube.</p><button id="save">Review before upload</button></form><p id="err" role="alert"></p></section><section id="review" hidden><h2>Review the exact post</h2><div id="details" class="data"></div><p class="sub">Posting sends the reviewed title, description and video to YouTube. This is not a public post.</p><label><input id="consent" type="checkbox" style="width:auto;min-height:auto"> I confirm this exact video and these details may be uploaded to Nexora Facts &amp; Cinema as Private.</label><button id="publish" disabled>Confirm private YouTube upload</button><button id="check" type="button">Check upload status</button><p id="status" role="status"></p><a id="studio" hidden target="_blank" rel="noopener noreferrer">Open YouTube Studio to check processing</a></section><p class="sub">Video is not kept after the upload attempt. Uncertain outcomes are never retried automatically. Keep the original video on your phone. Private videos stay on YouTube until you delete them there. Review metadata is erased after 7 days; minimal upload-status records remain to prevent duplicates.</p></main>\n<script>\nconst postingEnabled=__POSTING_ENABLED__;let key=crypto.randomUUID(),job,token;const $=s=>document.getElementById(s);async function api(url,options={}){const r=await fetch(url,{credentials:\'same-origin\',...options});const b=await r.json().catch(()=>({detail:\'Unexpected server response. Check before retrying.\'}));if(!r.ok)throw Error(b.detail||\'Request failed\');return b}function show(d){job=d.id;token=d.review_token;$(\'details\').textContent=`${d.title}\\n\\n${d.caption}\\n\\nChannel: ${d.channel}\\nVisibility: ${d.privacy}\\nMade for kids: ${d.made_for_kids?\'Yes\':\'No\'}\\nFile size: ${d.size} bytes\\nFile SHA-256: ${d.sha256}`;$(\'review\').hidden=false;$(\'consent\').checked=false;$(\'publish\').disabled=true;history.replaceState(null,\'\',\'#\'+job)}$(\'draft\').onsubmit=async e=>{e.preventDefault();$(\'err\').textContent=\'\';$(\'save\').disabled=true;try{const f=$(\'video\').files[0];if(!f||f.size>20*1024*1024)throw Error(\'Choose an MP4 below 20 MiB.\');const hash=[...new Uint8Array(await crypto.subtle.digest(\'SHA-256\',await f.arrayBuffer()))].map(b=>b.toString(16).padStart(2,\'0\')).join(\'\');show(await api(\'/publisher/review\',{method:\'POST\',headers:{\'Content-Type\':\'application/json\'},body:JSON.stringify({request_key:crypto.randomUUID(),title:$(\'title\').value,caption:$(\'caption\').value,sha256:hash,size:f.size,made_for_kids:$(\'made_for_kids\').value===\'yes\'})}));$(\'review\').scrollIntoView({behavior:\'smooth\'})}catch(e){$(\'err\').textContent=e.message}finally{$(\'save\').disabled=false}};let locked=false;$(\'consent\').onchange=()=>{$(\'publish\').disabled=!postingEnabled||!$(\'consent\').checked||locked};$(\'check\').onclick=async()=>{if(job){try{result(await api(\'/publisher/jobs/\'+job))}catch(e){$(\'status\').textContent=e.message}}};$(\'publish\').onclick=async()=>{if(!$(\'consent\').checked||locked)return;locked=true;const f=$(\'video\').files[0];if(!f){$(\'status\').textContent=\'Select the same reviewed video above before confirming.\';locked=false;return}$(\'publish\').disabled=true;$(\'status\').textContent=\'Sending. Do not tap again.\';const data=new FormData();data.append(\'video\',f);data.append(\'review_token\',token);data.append(\'confirm_private\',\'yes\');try{result(await api(\'/publisher/jobs/\'+job+\'/publish\',{method:\'POST\',body:data}))}catch(e){$(\'status\').textContent=e.message+\' Check status before trying anything again.\'}};function result(r){if(r.youtube.state!==\'ready\'){locked=true;$(\'publish\').disabled=true}const s=r.youtube,id=s.result&&s.result.remote_id;$(\'status\').textContent=s.state===\'done\'?\'YouTube accepted the upload. Check processing and Private visibility in Studio.\':s.state===\'needs_check\'?\'Outcome needs checking. No automatic retry.\':\'Not sent yet.\';if(id&&/^[a-zA-Z0-9_-]{11}$/.test(id)){$(\'studio\').href=\'https://studio.youtube.com/video/\'+id+\'/edit\';$(\'studio\').hidden=false}}if(/^#[0-9a-f-]{36}$/.test(location.hash)){api(\'/publisher/jobs/\'+location.hash.slice(1)).then(r=>{show(r.draft);result(r);if(r.youtube.state!==\'ready\')$(\'publish\').disabled=true}).catch(e=>$(\'err\').textContent=e.message)}\n</script></html>'
DECODER_CODE='"""Decoder worker. No network protocols, max 20 MiB input; process timeout by caller."""\nimport av,json,sys\nwith av.open(sys.argv[1],options={\'protocol_whitelist\':\'file,pipe\'}) as c:\n v=next((s for s in c.streams if s.type==\'video\'),None);a=next((s for s in c.streams if s.type==\'audio\'),None)\n if not v or v.codec_context.name!=\'h264\':raise ValueError(\'Use H.264 MP4\')\n if a and a.codec_context.name!=\'aac\':raise ValueError(\'Use AAC audio\')\n duration=float(c.duration or 0)/av.time_base\n if not 3<=duration<=90:raise ValueError(\'Use 3-90 seconds\')\n if v.codec_context.width>1920 or v.codec_context.height>1920:raise ValueError(\'Use up to 1920 pixels per side\')\n v.codec_context.thread_count=1\n frame=next(c.decode(v),None)\n if frame is None:raise ValueError(\'Cannot decode video\')\n print(json.dumps({\'duration\':duration,\'width\':v.codec_context.width,\'height\':v.codec_context.height,\'audio\':bool(a)}))\n'

"""Publishing coordinator. Ledger must atomically persist claim before any remote write.
No auto retry of a started target. A crash/timeout requires reconciliation by an operator.
"""
from dataclasses import dataclass
from typing import Protocol

class NotConnected(Exception): pass
class NeedsCheck(Exception): pass
class Rejected(Exception): pass
@dataclass(frozen=True)
class Post:
    id: str
    title: str
    caption: str
    file_path: str
    targets: tuple[str, ...]
    youtube_privacy: str = 'private'
    media_url: str | None = None

class Ledger(Protocol):
    def claim(self, post_id: str, platform: str) -> bool: ...
    def block_if_ready(self, post_id: str, platform: str) -> None: ...
    def finish(self, post_id: str, platform: str, state: str, result: dict) -> None: ...

class Publisher:
    def __init__(self, ledger, connectors):
        self.ledger, self.connectors = ledger, connectors
    def run(self, post):
        for platform in post.targets:
            connector = self.connectors.get(platform)
            if connector is None:
                # Not connected targets stay blocked; never claim or simulate success.
                self.ledger.block_if_ready(post.id, platform)
                continue
            if not self.ledger.claim(post.id, platform):
                continue
            try:
                result = connector.publish(post)
                if not result.get('remote_id'):
                    raise NeedsCheck('Platform response lacked a post id.')
                # accepted != playable/processed. Verification is a separate read.
                self.ledger.finish(post.id, platform, 'accepted', result)
            except Rejected:
                self.ledger.finish(post.id, platform, 'failed', {'message':'Platform rejected this attempt. Review before retrying.'})
            except Exception:
                # Never persist raw provider exception text: it may contain credentials.
                self.ledger.finish(post.id, platform, 'needs_check', {'message':'Outcome uncertain. Check platform before retrying.'})

"""Real HTTP connector implementations, not deployed or Meta-tested.
Credentials are injected server-side only. No token in URL or returned result.
"""
import json, mimetypes, os, urllib.parse, urllib.request, urllib.error

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*a,**kw): return None

class HTTP:
    def call(self, method, url, token, body=None, content_type='application/json', headers=None):
        data = json.dumps(body).encode() if isinstance(body,dict) and content_type=='application/json' else body
        hs={'Authorization':'Bearer '+token,'Content-Type':content_type,**(headers or {})}
        req=urllib.request.Request(url,data,hs,method=method)
        try:
            with urllib.request.build_opener(NoRedirect()).open(req,timeout=60) as r:
                b=r.read()
                return (json.loads(b) if b else {}),dict(r.headers)
        except urllib.error.HTTPError as e:
            # 5xx may have committed. Explicit 4xx is rejected, no automatic retry either.
            if e.code>=500: raise NeedsCheck('Server outcome unknown') from None
            raise Rejected('Platform rejected request') from None
        except Exception:
            raise NeedsCheck('Transport outcome unknown') from None

class YouTube:
    def __init__(self, token_provider, http=None):
        self.token_provider,self.http=token_provider,http or HTTP()
    def publish(self,p):
        if p.youtube_privacy not in ('private','unlisted','public'): raise Rejected('Invalid privacy')
        token=self.token_provider()
        size=os.path.getsize(p.file_path)
        meta={'snippet':{'title':p.title,'description':p.caption},'status':{'privacyStatus':p.youtube_privacy}}
        if hasattr(self,'made_for_kids'): meta['status']['selfDeclaredMadeForKids']=self.made_for_kids
        _,headers=self.http.call('POST','https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status',token,meta,headers={'X-Upload-Content-Type':'video/mp4','X-Upload-Content-Length':str(size)})
        location=next((v for k,v in headers.items() if k.lower()=='location'),None)
        # Never send token to untrusted upload origin, including redirect responses.
        if not location or urllib.parse.urlsplit(location).hostname!='www.googleapis.com': raise NeedsCheck('Unexpected upload origin')
        with open(p.file_path,'rb') as f:
            result,_=self.http.call('PUT',location,token,f.read(),'video/mp4')
        return {'remote_id':result.get('id'),'privacy':result.get('status',{}).get('privacyStatus')}

"""Immutable Storage ledger for an owner-only pilot.
Create-only writes arbitrate claims. A claim is NEVER removed/reused to retry a post.
A missing result after a claim is Needs check. Results, not claims, determine completion.
"""
import json,re,urllib.error,urllib.request,uuid
class Unknown(Exception):pass
class ObjectLedger:
 def __init__(self,url,key,bucket='nexora-publisher-ledger'):
  self.base=url.rstrip('/')+'/storage/v1/object/'+bucket+'/'
  self.headers={'apikey':key,'Authorization':'Bearer '+key,'Content-Type':'application/json','x-upsert':'false'}
 def path(self,job,platform,phase,kind):
  uuid.UUID(job)
  if platform not in ('youtube','instagram','facebook'):raise ValueError('bad platform')
  if not re.fullmatch('[a-z_]{1,32}',phase):raise ValueError('bad phase')
  return f'{job}/{platform}/{phase}-{kind}.json'
 def create(self,path,data):
  try:
   req=urllib.request.Request(self.base+path,json.dumps(data).encode(),self.headers,method='POST')
   with urllib.request.urlopen(req,timeout=15):return True
  except urllib.error.HTTPError as e:
   # Only exact object-exists error counts as a lost arbitration.
   try:d=json.load(e)
   except:d={}
   if e.code in (400,409) and (d.get('error')=='Duplicate' or str(d.get('statusCode'))=='409'):return False
   raise Unknown('Storage write failed') from None
  except Exception:raise Unknown('Claim outcome uncertain') from None
 def read_object(self,path):
  try:
   with urllib.request.urlopen(urllib.request.Request(self.base+path,headers=self.headers),timeout=15) as r:return json.load(r)
  except urllib.error.HTTPError as e:
   try:d=json.load(e)
   except:d={}
   if str(d.get('statusCode'))=='404' or e.code==404:return None
   raise Unknown('Cannot read ledger') from None
 def claim(self,job,platform,phase):
  return self.create(self.path(job,platform,phase,'claim'),{'claimed':True})
 def finish(self,job,platform,phase,state,result):
  if state not in ('done','needs_check','failed'):raise ValueError('Bad result')
  if not self.create(self.path(job,platform,phase,'result'),{'state':state,'result':result}):raise Unknown('Result already recorded')
 def read(self,job,platform,phase):
  r=self.read_object(self.path(job,platform,phase,'result'))
  if r:return r
  c=self.read_object(self.path(job,platform,phase,'claim'))
  return {'state':'needs_check' if c else 'ready','result':{}}

import json,subprocess,sys
from pathlib import Path
MAX_BYTES=49*1024*1024

def inspect_video(path):
 with open(path,'rb') as f:header=f.read(32)
 if len(header)<12 or header[4:8]!=b'ftyp':raise ValueError('Use a real MP4 video.')
 try:
  p=subprocess.run([sys.executable,'-c',DECODER_CODE,str(path)],capture_output=True,timeout=15,check=True)
  return json.loads(p.stdout)
 except Exception:raise ValueError('Use a valid H.264 MP4, 3-90 seconds, up to 1920 pixels per side and AAC audio.') from None

"""No persisted video. Review metadata request, then confirmed multipart publish.
Only durable private JSON job/claim/result objects. Meta disabled.
"""
import hashlib,hmac,json,os,tempfile,time,uuid
from pathlib import Path
from fastapi import APIRouter,Request,Form,File,UploadFile,HTTPException
from fastapi.responses import HTMLResponse
CAP=20*1024*1024
class Immediate:
 def __init__(self,current_user,url,key,origin,token_provider,review_secret):
  if len(review_secret)<32:raise ValueError('Secure review secret required')
  self.user=current_user;self.origin=origin;self.token_provider=token_provider;self.secret=review_secret.encode();self.ledger=ObjectLedger(url,key)
  self.router=APIRouter(prefix='/publisher')
  for path,func,method in [('',self.page,'GET'),('/review',self.review,'POST'),('/jobs/{job_id}',self.status,'GET'),('/jobs/{job_id}/publish',self.publish,'POST')]:self.router.add_api_route(path,func,methods=[method])
 def owner(self,r,write=False):
  u=self.user(r)
  if not u:raise HTTPException(401,'Sign in with your Nexora business Google account.')
  if u.get('email','').lower()!=os.environ.get('PUBLISHER_OWNER_EMAIL','').lower() or not u.get('email_confirmed_at'):raise HTTPException(403,'Owner-only private pilot.')
  if write and r.headers.get('origin')!=self.origin:raise HTTPException(403,'Origin rejected')
  return u['id']
 def jobkey(self,j):
  try:uuid.UUID(j)
  except ValueError:raise HTTPException(404,'Not found') from None
  return j+'/job.json'
 def job(self,j,owner):
  data=self.ledger.read_object(self.jobkey(j))
  if not data or data.get('owner')!=owner:raise HTTPException(404,'Not found')
  return data
 def sign(self,data):return hmac.new(self.secret,json.dumps(data,sort_keys=True,separators=(',',':')).encode(),hashlib.sha256).hexdigest()
 def trial(self):
  try:
   d=json.loads(os.environ.get('PUBLISHER_OWNER_TRIAL','{}'));uuid.UUID(d['id'])
   if not isinstance(d['expires'],int) or not time.time()<d['expires']<=time.time()+3700:return None
   return d
  except Exception:return None
 def trial_enabled(self):
  return os.environ.get('PUBLISHER_YOUTUBE_ENABLED')=='true' and self.trial() is not None
 def page(self,request:Request):
  self.owner(request)
  return HTMLResponse(PILOT_HTML.replace('__POSTING_ENABLED__', 'true' if self.trial_enabled() else 'false').replace('__TRIAL_NOTICE__', 'One owner-confirmed Private YouTube upload is available for this short trial. Review first, then confirm the exact file and details. No public posting.' if self.trial_enabled() else 'YouTube posting is OFF. Review only. No video will be sent.'),headers={'Cache-Control':'no-store','X-Frame-Options':'DENY','Referrer-Policy':'no-referrer','X-Content-Type-Options':'nosniff'})
 async def review(self,request:Request):
  owner=self.owner(request,True)
  if int(request.headers.get('content-length','999999'))>8192:raise HTTPException(413,'Review too large')
  try:
   d=await request.json();uuid.UUID(d['request_key'])
   if set(d)!={'request_key','title','caption','sha256','size','made_for_kids'}:raise ValueError()
   if not isinstance(d['title'],str) or not d['title'].strip() or len(d['title'])>100:raise ValueError()
   if not isinstance(d['caption'],str) or len(d['caption'])>2000:raise ValueError()
   if not isinstance(d['made_for_kids'],bool) or not isinstance(d['size'],int) or not 0<d['size']<=CAP:raise ValueError()
   if len(d['sha256'])!=64 or any(c not in '0123456789abcdef' for c in d['sha256']):raise ValueError()
  except Exception:raise HTTPException(400,'Check the video and post details.') from None
  trial=self.trial() if self.trial_enabled() else None
  if trial:
   if self.ledger.read_object('trial-'+trial['id']+'/upload.json'):raise HTTPException(429,'Your trial upload was already started. Check its status; do not retry.')
   slot=None
   for n in range(5):
    candidate='trial-'+trial['id']+'/review-'+str(n)+'.json'
    existing=self.ledger.read_object(candidate)
    if existing and existing.get('request_key')==d['request_key']:return self.response(self.job(existing['job_id'],owner))
    if not existing:slot=candidate;break
   if slot is None:raise HTTPException(429,'Trial review limit reached. Nothing sent.')
  else:
   day=time.strftime('%Y-%m-%d',time.gmtime());slot=f'owner-{owner}/{day}.json'
  old=self.ledger.read_object(slot)
  if old:
   if old.get('request_key')==d['request_key']:return self.response(self.job(old['job_id'],owner))
   raise HTTPException(429,'Private pilot limit: one new video per day.')
  jid=str(uuid.uuid4());data={**d,'id':jid,'owner':owner,'privacy':'private','channel':'Nexora Facts & Cinema','expires':int(time.time())+3600,'created':int(time.time()),'trial_id':trial['id'] if trial else None}
  if not self.ledger.create(slot,{'request_key':d['request_key'],'job_id':jid}):raise HTTPException(409,'A draft was just created. Check status.')
  if not self.ledger.create(self.jobkey(jid),data):raise HTTPException(409,'Job already exists.')
  return self.response(data)
 def response(self,j):return {k:v for k,v in j.items() if k not in ('owner','request_key')}|{'review_token':self.sign(j)}
 def status(self,request:Request,job_id:str):
  owner=self.owner(request);j=self.job(job_id,owner)
  youtube=self.ledger.read(job_id,'youtube','insert')
  if j.get('trial_id'):
   upload=self.ledger.read_object('trial-'+j['trial_id']+'/upload.json')
   if upload and youtube['state']=='ready':youtube={'state':'needs_check','result':{}}
  return {'draft':self.response(j),'youtube':youtube,'facebook':{'state':'not_connected'},'instagram':{'state':'not_connected'}}
 def publish(self,request:Request,job_id:str,review_token:str=Form(...),confirm_private:str=Form(...),video:UploadFile=File(...)):
  owner=self.owner(request,True);j=self.job(job_id,owner)
  if confirm_private!='yes':raise HTTPException(400,'Confirm the exact Private upload first. Nothing sent.')
  if not self.trial_enabled():raise HTTPException(503,'Trial is closed. Nothing sent.')
  if not hmac.compare_digest(review_token,self.sign(j)):raise HTTPException(409,'Review changed.')
  if time.time()>j['expires']:raise HTTPException(410,'Review expired. Nothing sent.')
  if j.get('trial_id')!=self.trial()['id']:raise HTTPException(403,'Review is not part of this trial. Nothing sent.')
  if j.get('privacy')!='private' or j.get('channel')!='Nexora Facts & Cinema':raise HTTPException(403,'Destination changed. Nothing sent.')
  length=request.headers.get('content-length','')
  if not length.isdigit() or int(length)>CAP+1024*1024:raise HTTPException(413,'Use an MP4 under 20 MiB.')
  if video.content_type!='video/mp4':raise HTTPException(400,'Use MP4.')
  path=None
  try:
   with tempfile.NamedTemporaryFile(suffix='.mp4',delete=False) as f:
    path=f.name;sha=hashlib.sha256();size=0
    while chunk:=video.file.read(1024*1024):
     size+=len(chunk)
     if size>CAP:raise HTTPException(413,'Video too large.')
     sha.update(chunk);f.write(chunk)
   if sha.hexdigest()!=j['sha256'] or size!=j['size']:raise HTTPException(409,'Video differs from the reviewed file. Nothing sent.')
   try:inspect_video(path)
   except ValueError as e:raise HTTPException(400,str(e)) from None
   # Validate the expiring access token before consuming the trial attempt.
   try:token=self.token_provider()
   except Exception:raise HTTPException(503,'YouTube connection needs renewal. Nothing sent.') from None
   trial=self.trial()
   if not trial:raise HTTPException(503,'Trial closed before upload. Nothing sent.')
   if not self.ledger.create('trial-'+trial['id']+'/upload.json',{'job_id':job_id,'owner':owner,'created':int(time.time())}):
    if self.ledger.read(job_id,'youtube','insert')['state']!='ready':return self.status(request,job_id)
    raise HTTPException(409,'Another trial upload was already started. Check status.')
   if not self.ledger.claim(job_id,'youtube','insert'):return self.status(request,job_id)
   connector=YouTube(lambda:token);connector.made_for_kids=j['made_for_kids']
   try:
    result=connector.publish(Post(job_id,j['title'],j['caption'],path,('youtube',),'private'))
    if not result.get('remote_id'):raise RuntimeError()
    self.ledger.finish(job_id,'youtube','insert','done',result)
   except Exception:
    try:self.ledger.finish(job_id,'youtube','insert','needs_check',{})
    except Exception:pass
   return self.status(request,job_id)
  finally:
   if path:Path(path).unlink(missing_ok=True)
   video.file.close()

"""ASGI guard before multipart parsing. Reject unauthorized/oversize publisher writes.
Only /publisher paths affected. Existing site's behavior is untouched.
"""
import json,asyncio
from starlette.requests import Request
class Guard:
 def __init__(self,app,pilot,cap=21*1024*1024):self.app,self.pilot,self.cap=app,pilot,cap
 async def __call__(self,scope,receive,send):
  if scope['type']=='http':
   auth_request=Request(scope)
   if scope.get('path')=='/login' and auth_request.query_params.get('next')=='/publisher' and scope['method']=='GET':
    body=b'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Sign in to Nexora Publisher</title><main style="font:18px/1.5 system-ui;max-width:520px;margin:50px auto;padding:22px"><p>NEXORA / OWNER-ONLY PILOT</p><h1>Sign in to Publisher</h1><p>Use your Nexora business Google account. After sign-in, you will return to the video-and-details form automatically.</p><p><a href="/auth/google?next=%2Fpublisher" style="display:block;padding:16px;background:#14213d;color:white;border-radius:8px;text-align:center">Continue with Google</a></p><p>Private YouTube trial only when enabled. You must review and confirm before any upload. Facebook and Instagram are not connected.</p></main></html>'
    if auth_request.query_params.get('err'):body=body.replace(b'<p>Use your',b'<p style="color:#a52222">Sign-in did not finish. Nothing was uploaded.</p><p>Use your')
    await send({'type':'http.response.start','status':200,'headers':[(b'content-type',b'text/html; charset=utf-8'),(b'cache-control',b'no-store'),(b'x-frame-options',b'DENY')]});await send({'type':'http.response.body','body':body});return
   google_start=scope.get('path')=='/auth/google' and scope['method']=='GET'
   publisher_start=google_start and auth_request.query_params.get('next')=='/publisher'
   publisher_callback=scope.get('path')=='/auth/callback' and auth_request.cookies.get('nx_publisher_return')=='/publisher'
   if google_start or publisher_callback:
    async def auth_send(m):
     if m['type']=='http.response.start':
      headers=list(m.get('headers',[]));location=next((v for k,v in headers if k.lower()==b'location'),b'')
      if publisher_callback and m['status'] in (302,303,307):
       destination=b'/publisher' if location==b'/' else b'/login?next=%2Fpublisher&err=1'
       headers=[(k,v) for k,v in headers if k.lower()!=b'location']+[(b'location',destination)]
      cookie=(b'nx_publisher_return="/publisher"; HttpOnly; Max-Age=600; Path=/; SameSite=lax; Secure' if publisher_start else b'nx_publisher_return=""; HttpOnly; Max-Age=0; Path=/; SameSite=lax; Secure')
      m['headers']=headers+[(b'set-cookie',cookie),(b'cache-control',b'no-store')]
     await send(m)
    return await self.app(scope,receive,auth_send)
  if scope['type']!='http' or not scope.get('path','').startswith('/publisher'):
   return await self.app(scope,receive,send)
  async def reject(status,text):
   body=json.dumps({'detail':text}).encode();await send({'type':'http.response.start','status':status,'headers':[(b'content-type',b'application/json'),(b'cache-control',b'no-store')]});await send({'type':'http.response.body','body':body})
  r=Request(scope)
  try:await asyncio.to_thread(self.pilot.owner,r,scope['method']=='POST')
  except Exception as e:
   if getattr(e,'status_code',0)==401 and scope['method']=='GET' and scope.get('path')=='/publisher':
    body=b'<!doctype html><meta name="viewport" content="width=device-width,initial-scale=1"><title>Nexora Publisher</title><main style="font:18px/1.5 system-ui;max-width:520px;margin:60px auto;padding:20px"><h1>Nexora Publisher</h1><p>Private owner-only pilot. Sign in with your Nexora business account, then return here.</p><p><a href="/login?next=%2Fpublisher">Sign in to Nexora</a></p><p>Facebook and Instagram are not connected. Posting is not enabled.</p></main>'
    await send({'type':'http.response.start','status':401,'headers':[(b'content-type',b'text/html; charset=utf-8'),(b'cache-control',b'no-store'),(b'x-frame-options',b'DENY')]});await send({'type':'http.response.body','body':body});return
   return await reject(getattr(e,'status_code',503),getattr(e,'detail','Private publisher unavailable.'))
  if scope['method']=='POST':
   n=r.headers.get('content-length','')
   if not n.isdigit() or int(n)>self.cap:return await reject(413,'Use a video below 20 MiB.')
  consumed=0
  async def bounded_receive():
   nonlocal consumed
   m=await receive()
   if m['type']=='http.request':
    consumed+=len(m.get('body',b''))
    if consumed>self.cap:raise RuntimeError('Body cap exceeded')
   return m
  async def safe_send(m):
   if m['type']=='http.response.start':m['headers']=list(m.get('headers',[]))+[(b'cache-control',b'no-store'),(b'x-content-type-options',b'nosniff'),(b'x-frame-options',b'DENY'),(b'referrer-policy',b'no-referrer')]
   await send(m)
  await self.app(scope,bounded_receive,safe_send)

"""Opt-in installation. Existing app unchanged unless PUBLISHER_PILOT_ENABLED=true.
Secrets stay in server environment. Scope: one verified owner, YouTube Private only.
"""
import os,json,urllib.parse,urllib.request

def attach(app,current_user):
 if os.environ.get('PUBLISHER_PILOT_ENABLED')!='true':return
 required=['SUPABASE_URL','SUPABASE_SERVICE_KEY','SITE_URL','PUBLISHER_REVIEW_SECRET','PUBLISHER_OWNER_EMAIL']
 if any(not os.environ.get(k) for k in required):raise RuntimeError('Publisher config incomplete')
 def token():
  try:
   if time.time()>=int(os.environ['PUBLISHER_ACCESS_EXPIRES'])-60:raise RuntimeError()
   return os.environ['PUBLISHER_YT_ACCESS_TOKEN']
  except Exception:raise RuntimeError('YouTube trial connection expired') from None

 p=Immediate(current_user,os.environ['SUPABASE_URL'],os.environ['SUPABASE_SERVICE_KEY'],os.environ['SITE_URL'].rstrip('/'),token,os.environ['PUBLISHER_REVIEW_SECRET'])
 start=len(app.router.routes)
 for route in p.router.routes:app.add_api_route(route.path,route.endpoint,methods=list(route.methods))
 added=app.router.routes[start:];del app.router.routes[start:];app.router.routes[0:0]=added
 app.add_middleware(Guard,pilot=p)
