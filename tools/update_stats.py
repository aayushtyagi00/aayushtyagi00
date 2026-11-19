"""Generate repository-hosted profile cards from public GitHub data. Standard library only."""
import json, os, re, urllib.request
from html.parser import HTMLParser
from html import escape
from collections import Counter
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path
USER='aayushtyagi00'
ROOT=Path(__file__).resolve().parents[1]
TODAY=datetime.now(ZoneInfo('Asia/Kolkata')).date()
def get(url):
    headers={'User-Agent': USER+'-profile-stats'}
    if url.startswith('https://api.github.com/') and os.getenv('GITHUB_TOKEN'):
        headers['Authorization']='Bearer '+os.environ['GITHUB_TOKEN']
    with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=45) as r:
        return r.read().decode()
def api(path):return json.loads(get('https://api.github.com/'+path))
repos=[]
for page in range(1,11):
    batch=api(f'users/{USER}/repos?per_page=100&page={page}')
    repos+=batch
    if len(batch)<100:break
owned=[r for r in repos if not r['fork']]
langs=Counter()
for r in owned:
    for lang,size in api('repos/'+r['full_name']+'/languages').items():langs[lang]+=size
class Calendar(HTMLParser):
    def __init__(self):super().__init__();self.days={};self.counts={};self.target=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'data-date' in a and 'id' in a:self.days[a['id']]=a['data-date']
        if tag=='tool-tip':self.target=a.get('for')
    def handle_data(self,text):
        if self.target and 'contribution' in text:
            m=re.match(r'\s*(\d[\d,]*) contributions? on ',text)
            if m:self.counts[self.target]=int(m[1].replace(',',''))
            elif text.strip().startswith('No contributions on '):self.counts[self.target]=0
    def handle_endtag(self,tag):
        if tag=='tool-tip':self.target=None
cal=Calendar();cal.feed(get(f'https://github.com/users/{USER}/contributions'))
if len(cal.days)<300 or len(cal.counts)<300:raise RuntimeError('Contribution calendar format changed; retaining previous cards.')
days={date:cal.counts[key] for key,date in cal.days.items() if key in cal.counts and date<=TODAY.isoformat()}
run=longest=0
for day,count in sorted(days.items()):
    run=run+1 if count else 0;longest=max(longest,run)
end=TODAY
if not days.get(end.isoformat(),0):end-=timedelta(days=1)
current=0
while days.get(end.isoformat(),0):current+=1;end-=timedelta(days=1)
updated=TODAY.isoformat()
BG='#11182d'
BORDER='#394b74'
PRIMARY='#78e3f6'
ACCENT='#c4b5fd'
WHITE='#eef4ff'
MUTED='#adbbd5'
def text(x,y,s,size=14,color=WHITE,weight=400,anchor='start'):
    return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" font-family="Segoe UI,Arial,sans-serif">{escape(str(s))}</text>'
def svg(w,h,body,label):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label)}"><rect x="1" y="1" width="{w-2}" height="{h-2}" rx="16" fill="{BG}" stroke="{BORDER}"/>{body}</svg>\n'
body=text(24,34,'GITHUB OVERVIEW',13,PRIMARY,600)
for i,(label,val) in enumerate([('Public repositories',len(repos)),('Stars earned',sum(r['stargazers_count'] for r in owned)),('Contributions · past year',sum(days.values()))]):
    x=24+165*i;body+=text(x,91,f'{val:,}',34,WHITE,700)+text(x,119,label,11,MUTED)
body+=text(24,159,'PUBLIC DATA · '+updated,10,MUTED)
(ROOT/'assets/github-stats.svg').write_text(svg(550,180,body,'Public GitHub statistics'),encoding='utf-8')
body=text(24,34,'TOP LANGUAGES',13,PRIMARY,600)
total=sum(langs.values()) or 1
colors=[PRIMARY,ACCENT,'#79e6c1','#fba6c4','#fbd38d']
x=24
for i,(lang,count) in enumerate(langs.most_common(5)):
    width=502*count/total
    body+=f'<rect x="{x:.2f}" y="55" width="{width:.2f}" height="9" fill="{colors[i]}"/>';x+=width
    col=i%3;row=i//3
    body+=text(24+168*col,94+row*27,f'{lang}  {count/total:.1%}',12,colors[i])
body+=text(24,159,'CODE BYTES · OWN PUBLIC REPOS · '+updated,10,MUTED)
(ROOT/'assets/top-languages.svg').write_text(svg(550,180,body,'Top languages by code bytes in own public repositories'),encoding='utf-8')
body=text(28,35,'CONTRIBUTION STREAK',13,PRIMARY,600)
for i,(label,val,color) in enumerate([('Contributions · past year',sum(days.values()),WHITE),('Current streak · days',current,PRIMARY),('Longest streak · past year',longest,ACCENT)]):
    x=183+367*i
    body+=text(x,110,f'{val:,}',43,color,700,'middle')+text(x,144,label,14,MUTED,400,'middle')
    if i<2:body+=f'<path d="M {367*(i+1)} 66 V 158" stroke="{BORDER}"/>'
body+=text(550,193,'PUBLIC CONTRIBUTION CALENDAR · '+updated+' · ASIA/KOLKATA',10,MUTED,400,'middle')
(ROOT/'assets/streak.svg').write_text(svg(1100,218,body,'Contribution totals and streaks over the public calendar window'),encoding='utf-8')
(ROOT/'assets/stats.json').write_text(json.dumps({'updated':updated,'public_repositories':len(repos),'stars_own_repos':sum(r['stargazers_count'] for r in owned),'contributions_calendar_window':sum(days.values()),'current_streak':current,'longest_streak_calendar_window':longest,'window_start':min(days),'window_end':max(days),'language_bytes':dict(langs)},indent=2)+'\n')
print((ROOT/'assets/stats.json').read_text())
