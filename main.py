import asyncio, json, os, secrets, signal, string, subprocess, time
from pathlib import Path
from typing import Any
import psutil
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'; UPLOAD_DIR = DATA_DIR / 'uploads'; LOG_DIR = DATA_DIR / 'logs'; STATE_FILE = DATA_DIR / 'state.json'
for p in (DATA_DIR, UPLOAD_DIR, LOG_DIR): p.mkdir(parents=True, exist_ok=True)

API_ID=os.getenv('API_ID','36371827'); API_HASH=os.getenv('API_HASH','4b33c6649f49006c2954c1635e448574'); BOT_TOKEN=os.getenv('BOT_TOKEN','8269981439:AAHawY-6QKlG6DxgUw1SwlDBZHo-XZyEWxY')
OWNER_IDS={int(x) for x in os.getenv('OWNER_IDS','8780206093').split(',') if x.strip()}
ADMIN_IDS={int(x) for x in os.getenv('ADMIN_IDS','8780206093,7363967303').split(',') if x.strip()}
DEFAULT_PLAN=os.getenv('DEFAULT_PLAN','free'); MAX_RAM_MB=int(os.getenv('MAX_RAM_MB','1024'))
PLAN_LIMITS={'free':int(os.getenv('PLAN_FREE_LIMIT','1')),'plus':int(os.getenv('PLAN_PLUS_LIMIT','3')),'pro':int(os.getenv('PLAN_PRO_LIMIT','6'))}
VALID_PLANS=list(PLAN_LIMITS.keys()); BOT_BRAND='JUNE'

app=Client('private_hosting_bot', api_id=int(API_ID), api_hash=API_HASH, bot_token=BOT_TOKEN)
STATE: dict[str, Any]={'jobs':{},'plans':{},'keys':{},'key_builder':{}}

def now_ts()->int: return int(time.time())
def save_state()->None: STATE_FILE.write_text(json.dumps(STATE,indent=2),encoding='utf-8')
def load_state()->None:
    global STATE
    if STATE_FILE.exists():
        try: STATE=json.loads(STATE_FILE.read_text(encoding='utf-8'))
        except Exception: STATE={'jobs':{},'plans':{},'keys':{},'key_builder':{}}
    for k,v in {'jobs':{},'plans':{},'keys':{},'key_builder':{}}.items(): STATE.setdefault(k,v)
    save_state()
def is_admin(uid:int)->bool: return uid in OWNER_IDS or uid in ADMIN_IDS

def get_plan(uid:int)->str:
    if uid in OWNER_IDS: return 'owner'
    e=STATE['plans'].get(str(uid))
    if not e: return DEFAULT_PLAN
    if isinstance(e,str): return e
    if e.get('expires_at') and now_ts()>e['expires_at']:
        STATE['plans'].pop(str(uid),None); save_state(); return DEFAULT_PLAN
    return e.get('plan',DEFAULT_PLAN)

def plan_text(uid:int)->str:
    e=STATE['plans'].get(str(uid))
    if isinstance(e,dict) and e.get('expires_at'):
        return f"{e['plan'].title()} ({max(0,(e['expires_at']-now_ts())//86400)}d left)"
    return get_plan(uid).title()

def user_limit(uid:int)->int: return 10**9 if uid in OWNER_IDS else PLAN_LIMITS.get(get_plan(uid),1)
def sanitize(name:str)->str: return ''.join(ch for ch in name if ch.isalnum() or ch in '._-')
def file_path(uid:int,f:str)->Path: return UPLOAD_DIR/f"{uid}_{sanitize(f)}"
def log_paths(jid:str)->tuple[Path,Path]: s=jid.replace(':','_'); return LOG_DIR/f'{s}.out.log', LOG_DIR/f'{s}.err.log'
def make_job_id(uid:int,f:str)->str: return f"{uid}:{sanitize(f)}"
def is_running(pid:int|None)->bool: return bool(pid and psutil.pid_exists(pid))
def launch_cmd(lang:str,p:Path)->list[str]: return ['python3',str(p)] if lang=='python' else ['node',f'--max-old-space-size={MAX_RAM_MB}',str(p)]

async def stop_job(jid:str)->str:
    j=STATE['jobs'].get(jid); 
    if not j: return 'missing'
    pid=j.get('pid')
    if not is_running(pid): j['status']='offline'; j['pid']=None; save_state(); return 'already_offline'
    try:
        os.killpg(os.getpgid(pid), signal.SIGTERM); await asyncio.sleep(1)
        if is_running(pid): os.killpg(os.getpgid(pid), signal.SIGKILL)
    except Exception: pass
    j['status']='offline'; j['pid']=None; j['updated_at']=now_ts(); save_state(); return 'stopped'

def start_job(jid:str)->str:
    j=STATE['jobs'].get(jid)
    if not j: return 'missing'
    p=file_path(j['owner_id'],j['file_name'])
    if not p.exists(): return 'file_missing'
    if is_running(j.get('pid')): j['status']='online'; return 'already_running'
    out,err=log_paths(jid)
    with open(out,'ab') as o, open(err,'ab') as e:
        proc=subprocess.Popen(launch_cmd(j['language'],p),stdout=o,stderr=e,preexec_fn=os.setsid)
    j['pid']=proc.pid; j['status']='online'; j['updated_at']=now_ts(); save_state(); return 'started'

def refresh_status(j:dict[str,Any])->None:
    if j.get('status')=='online' and not is_running(j.get('pid')): j['status']='offline'; j['pid']=None

def tail_logs(jid:str,limit:int=25)->str:
    out,err=log_paths(jid); parts=[]
    for p,t in ((err,'ERR'),(out,'OUT')):
        if p.exists():
            lines=p.read_text(encoding='utf-8',errors='ignore').splitlines()[-limit:]
            if lines: parts.append(f'[{t}]\n'+'\n'.join(lines))
    return ('\n\n'.join(parts)[:3500]) or 'No logs yet.'

def parse_import_error(t:str)->str|None:
    for ln in t.splitlines()[-30:]:
        if 'ModuleNotFoundError' in ln or 'Cannot find module' in ln: return ln.strip()
    return None

def generate_key(plan:str,days:int,creator:int)->str:
    alpha=string.ascii_uppercase+string.digits
    while True:
        suffix=''.join(secrets.choice(alpha) for _ in range(8)); day='LIFETIME' if days==-1 else str(days)
        code=f'{BOT_BRAND}-{plan.upper()}-{day}-{suffix}'
        if code not in STATE['keys']: break
    STATE['keys'][code]={'plan':plan,'days':days,'created_by':creator,'created_at':now_ts(),'redeemed_by':None,'redeemed_at':None}; save_state(); return code

def redeem_key(uid:int,code:str)->tuple[bool,str]:
    i=STATE['keys'].get(code)
    if not i: return False,'Invalid key.'
    if i.get('redeemed_by'): return False,'Key already redeemed.'
    i['redeemed_by']=uid; i['redeemed_at']=now_ts(); plan=i['plan']; days=i['days']
    STATE['plans'][str(uid)]={'plan':plan,'expires_at':None if days==-1 else now_ts()+days*86400,'source':code}; save_state()
    return True,f"Redeemed {plan.upper()} ({'LIFETIME' if days==-1 else str(days)+' days'})"

def main_menu()->InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton('📢 Updates Channel',url='https://t.me')],
        [InlineKeyboardButton('📤 Upload File',callback_data='menu_upload'),InlineKeyboardButton('🗂 Check Files',callback_data='menu_files')],
        [InlineKeyboardButton('⚡ Bot Speed',callback_data='menu_speed'),InlineKeyboardButton('📊 Statistics',callback_data='menu_stats')],
        [InlineKeyboardButton('📞 Contact Owner',callback_data='menu_contact'),InlineKeyboardButton('🧩 Manual Install',callback_data='menu_install')],
        [InlineKeyboardButton('❓ Help',callback_data='menu_help')],
    ])

def file_menu(jid:str)->InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton('📊 Status',callback_data=f'status|{jid}'),InlineKeyboardButton('📜 Logs',callback_data=f'logs|{jid}')],
        [InlineKeyboardButton('🔄 Restart',callback_data=f'restart|{jid}'),InlineKeyboardButton('⏸ Stop',callback_data=f'stop|{jid}')],
        [InlineKeyboardButton('🗑 Delete',callback_data=f'delete|{jid}')],
    ])

def key_plan_menu()->InlineKeyboardMarkup: return InlineKeyboardMarkup([[InlineKeyboardButton(f'🔑 {p.upper()}',callback_data=f'kplan|{p}')] for p in VALID_PLANS])
def key_day_menu(plan:str)->InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton('1',callback_data=f'kday|{plan}|1'),InlineKeyboardButton('3',callback_data=f'kday|{plan}|3'),InlineKeyboardButton('7',callback_data=f'kday|{plan}|7')],
        [InlineKeyboardButton('15',callback_data=f'kday|{plan}|15'),InlineKeyboardButton('30',callback_data=f'kday|{plan}|30'),InlineKeyboardButton('LIFETIME',callback_data=f'kday|{plan}|-1')],
    ])

def job_card(jid:str)->str:
    j=STATE['jobs'][jid]; refresh_status(j); save_state(); e='🟢' if j['status']=='online' else '🔴'
    return f"{e} **{j['file_name']}**\n🧠 Runtime: `{j['language']}`\n📦 Plan: `{j['plan']}`\n📶 Status: `{j['status']}`\n🆔 PID: `{j.get('pid')}`\n⏱ Updated: `{j.get('updated_at',j.get('created_at'))}`"

def list_jobs(uid:int)->list[str]: return list(STATE['jobs'].keys()) if is_admin(uid) else [k for k,v in STATE['jobs'].items() if v['owner_id']==uid]

@app.on_message(filters.command('start') & filters.private)
async def start(_,m:Message):
    uid=m.from_user.id; uploaded=len([x for x in STATE['jobs'].values() if x['owner_id']==uid]); lim='∞' if uid in OWNER_IDS else str(user_limit(uid))
    txt=(f"**Welcome, — {m.from_user.first_name}!**\n\n👤 **User Information**\n• Your User ID: `{uid}`\n• Your Status: `{plan_text(uid)} User`\n• Files Uploaded: `{uploaded} / {lim}`\n\n☁️ **Service Description**\n• Host & run Python (.py) or JS (.js) scripts\n• Upload single scripts\n• Manual module installation guidance\n\n🧭 **Usage Instruction**\nUse buttons or type commands.")
    await m.reply(txt, reply_markup=main_menu())

@app.on_message(filters.command('setplan') & filters.private)
async def setplan(_,m:Message):
    if not is_admin(m.from_user.id): return await m.reply('⛔ Admin only command.')
    p=m.text.split();
    if len(p)!=3 or p[2] not in PLAN_LIMITS: return await m.reply('Usage: /setplan <user_id> <free|plus|pro>')
    STATE['plans'][p[1]]={'plan':p[2],'expires_at':None,'source':'manual'}; save_state(); await m.reply(f"✅ Plan set for `{p[1]}` -> `{p[2]}`")

@app.on_message(filters.command('key') & filters.private)
async def key(_,m:Message):
    if not is_admin(m.from_user.id): return await m.reply('⛔ Admin only command.')
    await m.reply('Select plan to generate keys:', reply_markup=key_plan_menu())

@app.on_message(filters.command('redeem') & filters.private)
async def redeem(_,m:Message):
    p=m.text.split(maxsplit=1)
    if len(p)<2: return await m.reply('Usage: /redeem JUNE-PLAN-DAYS-XXXXXXXX')
    ok,msg=redeem_key(m.from_user.id,p[1].strip().upper()); await m.reply(('✅ ' if ok else '❌ ')+msg)

@app.on_message(filters.command(['myfiles','files']) & filters.private)
async def myfiles(_,m:Message):
    jobs=list_jobs(m.from_user.id)
    if not jobs: return await m.reply('📭 No uploaded files yet.')
    for jid in jobs: await m.reply(job_card(jid), reply_markup=file_menu(jid))

@app.on_message(filters.private & filters.text)
async def key_count_input(_,m:Message):
    uid=str(m.from_user.id); flow=STATE['key_builder'].get(uid)
    if not flow or flow.get('step')!='count': return
    if not m.text.isdigit(): return await m.reply('Send a number, e.g. 1 or 5')
    count=int(m.text)
    if count<1 or count>100: return await m.reply('Count must be between 1 and 100')
    codes=[generate_key(flow['plan'],flow['days'],m.from_user.id) for _ in range(count)]
    STATE['key_builder'].pop(uid,None); save_state(); await m.reply('✅ Generated keys:\n\n'+'\n'.join(codes))

@app.on_message(filters.private & filters.document)
async def upload(_,m:Message):
    uid=m.from_user.id; d=m.document
    if not d or not d.file_name: return
    if not d.file_name.endswith(('.py','.js')): return await m.reply('❌ Only `.py` and `.js` files are supported.')
    if len([j for j in STATE['jobs'].values() if j['owner_id']==uid])>=user_limit(uid): return await m.reply('🚫 Upload limit reached for your plan.')
    lang='python' if d.file_name.endswith('.py') else 'node'; safe=sanitize(d.file_name)
    if not safe: return await m.reply('❌ Invalid filename.')
    path=file_path(uid,safe); await m.download(file_name=str(path)); jid=make_job_id(uid,safe)
    STATE['jobs'][jid]={'owner_id':uid,'file_name':safe,'language':lang,'plan':get_plan(uid),'status':'offline','pid':None,'created_at':now_ts(),'updated_at':now_ts()}; save_state()
    start_job(jid); await asyncio.sleep(2); refresh_status(STATE['jobs'][jid]); save_state()
    if STATE['jobs'][jid]['status']!='online':
        log=tail_logs(jid,20); hint=parse_import_error(log); await stop_job(jid); del STATE['jobs'][jid]; path.unlink(missing_ok=True); save_state()
        msg=f"❌ Upload failed while starting `{safe}`.\n\n```\n{log}\n```" + (f"\n\n💡 Possible dependency issue: `{hint}`" if hint else '')
        return await m.reply(msg)
    await m.reply(f"✅ Uploaded and running: `{safe}`", reply_markup=file_menu(jid))

@app.on_callback_query()
async def callbacks(_,cq):
    data=cq.data; uid=cq.from_user.id
    if data.startswith('menu_'):
        mp={'menu_upload':'📤 Send a `.py` or `.js` file directly in this chat.','menu_files':'🗂 Use /myfiles to view and manage uploaded files.','menu_speed':'⚡ Running on your VPS performance.','menu_stats':f"📊 Total files hosted: {len(STATE['jobs'])}", 'menu_contact':'📞 Contact owner via your configured support channel.','menu_install':'🧩 Install missing dependencies on VPS then re-upload.','menu_help':'❓ Commands: /start /myfiles /key /redeem /setplan'}
        return await cq.answer(mp.get(data,'OK'),show_alert=True)
    if data.startswith('kplan|'):
        if not is_admin(uid): return await cq.answer('Admin only',show_alert=True)
        plan=data.split('|',1)[1]; return await cq.message.edit_text(f'Select duration for {plan.upper()}:', reply_markup=key_day_menu(plan))
    if data.startswith('kday|'):
        if not is_admin(uid): return await cq.answer('Admin only',show_alert=True)
        _,plan,days=data.split('|',2); STATE['key_builder'][str(uid)]={'plan':plan,'days':int(days),'step':'count'}; save_state()
        return await cq.message.edit_text(f"Plan `{plan}` for `{'LIFETIME' if int(days)==-1 else days+' days'}` selected.\nNow send count (1-100).")
    if '|' not in data: return await cq.answer('Invalid action',show_alert=True)
    action,jid=data.split('|',1)
    if jid not in STATE['jobs']: return await cq.answer('Job not found',show_alert=True)
    j=STATE['jobs'][jid]
    if uid!=j['owner_id'] and not is_admin(uid): return await cq.answer('Not allowed',show_alert=True)
    if action=='status': await cq.message.edit_text(job_card(jid),reply_markup=file_menu(jid)); return await cq.answer('Refreshed')
    if action=='logs': await cq.message.reply(f"📜 Logs for `{j['file_name']}`\n```\n{tail_logs(jid,30)}\n```"); return await cq.answer('Latest logs sent')
    if action=='restart':
        await stop_job(jid)
        res=start_job(jid)
        await cq.message.edit_text(job_card(jid),reply_markup=file_menu(jid))
        return await cq.answer(f'Restart: {res}')
    if action=='stop': res=await stop_job(jid); await cq.message.edit_text(job_card(jid),reply_markup=file_menu(jid)); return await cq.answer(res)
    if action=='delete': await stop_job(jid); file_path(j['owner_id'],j['file_name']).unlink(missing_ok=True); del STATE['jobs'][jid]; save_state(); await cq.message.edit_text('🗑 File deleted.'); return await cq.answer('Deleted')

if __name__=='__main__':
    load_state(); print('Bot starting...'); app.run()
