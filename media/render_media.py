"""Render editable, deterministic illustrations for Using AI Better.
Run with bundled Python; imageio-ffmpeg is installed in ../.media-tools.
"""
from pathlib import Path
import sys, math, csv, json, subprocess
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '.media-tools'))
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

OUT = Path(__file__).resolve().parent
W,H = 1280,800
BG='#0b1220'; PANEL='#121f32'; BORDER='#293b53'; FG='#eff5ff'; MUTED='#a9bad1'
COLORS=['#69d5eb','#a89aff','#f5bf71','#7ee2b0','#f08bb4','#9bc6ff']
FONT=Path('C:/Windows/Fonts')
def font(size,bold=False):
    return ImageFont.truetype(str(FONT / ('segoeuib.ttf' if bold else 'segoeui.ttf')),size)
def text(d,xy,s,size=20,fill=FG,bold=False): d.text(xy,s,font=font(size,bold),fill=fill)
def box(d,rect,fill=PANEL,outline=None,r=16): d.rounded_rectangle(rect,radius=r,fill=fill,outline=outline,width=2)
def line(d,a,b,fill=BORDER,width=3): d.line([a,b],fill=fill,width=width)
def packet(d,a,b,p,c):
    x=a[0]+(b[0]-a[0])*p;y=a[1]+(b[1]-a[1])*p
    box(d,(x-8,y-6,x+8,y+6),c,r=3)
def eased(x): return (1-math.cos(math.pi*max(0,min(1,x))))/2

MODELS=['GPT-6-Astra','GPT-6.1-Sol','Claude Sonnet5.5','Claude Opus5.5','Qwen3.8-27B (self-hosted)','Kimi K3 (self-hosted)']
PROJECTS=['Research & planning','Data analysis','Software development','Training & evaluation','Prototyping','Reports & presentations']
VALUES=[[400,260,240,200,0,0],[320,300,280,200,0,0],[180,240,260,120,0,0],[160,120,180,140,0,0],[0,0,0,0,180,120],[60,60,40,40,0,0]]
DAYS=[430,590,520,680,760,610,510]

def arrow(d,a,b,color=BORDER,animate=False,p=0):
    line(d,a,b,color,3)
    direction=1 if b[0]>a[0] else -1
    d.polygon([b,(b[0]-direction*10,b[1]-6),(b[0]-direction*10,b[1]+6)],fill=color)
    if animate:
        for k in range(4):packet(d,a,b,(p*2+k/4)%1,color)

def frame(t):
    im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
    stage=min(4,int(t//8));p=(t%8)/8
    titles=['01  Build and plan','02  Push code; process, train and evaluate',
            '03  Collect .claude and .codex usage logs','04  Accumulate daily statistics','05  Analyze the week']
    subtitles=['Linux edits code and runs tests while Windows handles knowledge work.',
      'Tested code moves to cloud GPUs. Datasets and checkpoints stay in the cloud.',
      'Linux pulls cloud logs over SSH; Windows gathers Linux and its own local logs.',
      'At 00:15 Seoul, close the previous day by project and model.',
      'Monday 08:00 Seoul: combine seven days, verify progress and suggest savings.']
    text(d,(48,22),'USING AI BETTER',17,COLORS[0],True)
    text(d,(48,55),titles[stage],32,bold=True)
    text(d,(48,108),subtitles[stage],20,MUTED)
    text(d,(1060,25),'ILLUSTRATIVE',16,MUTED)
    # Three active work surfaces stay visible throughout the explanation.
    for x,title,sub,c in [(48,'Linux development','Code + tests + deployment',COLORS[1]),
                           (457,'Cloud GPU cluster','Data processing + train / eval',COLORS[0]),
                           (866,'Windows command center','Planning + slides + mail + analysis',COLORS[2])]:
        box(d,(x,158,x+366,450),outline=BORDER)
        text(d,(x+18,172),title,24,bold=True)
        text(d,(x+18,208),sub,17,MUTED)
        line(d,(x+18,242),(x+348,242),BORDER,1)
    # Linux: code appears line by line, followed by a real-looking test transcript.
    code=['def evaluate(model, dataset):','    predictions = model(dataset)','    return score(predictions)']
    reveal=int(p*5)+1 if stage==0 else 3
    for j,s in enumerate(code):
        if j<reveal:text(d,(66,255+j*25),s,17,COLORS[1])
    text(d,(66,335),'$ pytest tests/ -q',18)
    status='Running tests ...' if stage==0 and p<.55 else '12 passed in 2.4s'
    text(d,(66,362),status,18,COLORS[3] if 'passed' in status else MUTED)
    text(d,(66,391),'$ git push origin main',17,MUTED)
    text(d,(66,421),'~/.claude/   ~/.codex/',18,COLORS[1])
    # Cloud: dataset shards visibly process, training advances, evaluation finishes.
    text(d,(475,255),'Dataset shards -> preprocessing',18)
    cloud_p=p if stage==1 else (1 if stage>1 else 0)
    for j in range(12):
        x=475+j*27
        box(d,(x,289,x+20,308),COLORS[0] if cloud_p>(j+1)/14 else BORDER,r=3)
    text(d,(475,322),f'Train  epoch {min(3,int(cloud_p*3)+1)}/3',18)
    box(d,(475,351,804,363),BG,r=4)
    box(d,(475,351,476+int(328*cloud_p),363),COLORS[0],r=4)
    eval_s='Eval queued' if cloud_p<.6 else ('Eval running ...' if cloud_p<.88 else 'Eval complete | accuracy 0.91')
    text(d,(475,377),eval_s,17,COLORS[3] if cloud_p>=.88 else MUTED)
    text(d,(475,421),'~/.claude/   ~/.codex/',18,COLORS[0])
    # Windows cycles through actual work representations every two seconds.
    activity=int((t%8)//2)
    tab_names=['Plan','Slides','Mail','Analyze']
    for j,name in enumerate(tab_names):
        text(d,(884+j*82,253),name,17,COLORS[2] if j==activity else MUTED,j==activity)
    if activity==0:
        text(d,(884,285),'PROJECT PLAN',17,bold=True)
        for j,s in enumerate(['Define scope','Review milestones','Schedule next experiment']):
            text(d,(884,313+j*29),('[x] ' if j<2 else '[ ] ')+s,17,COLORS[3] if j<2 else FG)
    elif activity==1:
        box(d,(884,289,1214,401),BG,r=6)
        text(d,(899,300),'Quarterly results',20,bold=True)
        for j,v in enumerate([26,43,58,70]):
            d.rectangle((903+j*34,387-v,923+j*34,387),fill=COLORS[2])
        text(d,(1061,341),'Slide 4 / 8',17,MUTED)
        text(d,(1061,370),'Saving ...',17,COLORS[3])
    elif activity==2:
        text(d,(884,291),'INBOX  <-  Feedback received',17)
        text(d,(884,325),'SENT   ->  Project update sent',17,COLORS[3])
        line(d,(884,357),(1213,357),BORDER,1)
        text(d,(884,374),'Reply linked to project evidence',16,MUTED)
    else:
        text(d,(884,287),'DASHBOARD REVIEW',17,bold=True)
        points=[(886,380),(937,361),(988,370),(1039,331),(1090,340),(1141,312),(1204,300)]
        d.line(points,fill=COLORS[2],width=3)
        for x,y in points:d.ellipse((x-3,y-3,x+3,y+3),fill=COLORS[2])
        text(d,(884,389),'Compare usage, progress and spend',16,MUTED)
    text(d,(884,421),'%USERPROFILE%: .claude / .codex',17,COLORS[2])
    # Direction labels explicitly distinguish deployment from returning logs.
    if stage<=1:
        text(d,(199,459),'Tested code -> SSH / GitHub Actions -> cloud',17,MUTED)
        arrow(d,(230,489),(640,489),COLORS[1],stage==1,p)
    else:
        text(d,(199,459),'Cloud usage logs -> Linux relay  /  SSH',17,MUTED)
        arrow(d,(640,489),(230,489),COLORS[0],stage==2,p)
    text(d,(672,498),'Linux logs + cloud logs -> Windows  /  SSH',17,MUTED)
    arrow(d,(230,525),(1050,525),COLORS[0] if stage>=2 else BORDER,stage==2,p)
    box(d,(48,551,1232,731))
    if stage==0:
        text(d,(70,566),'Every task leaves progress evidence',23,bold=True)
        text(d,(70,608),'Linux: code diff + test results       Cloud: job manifest + metrics',21)
        text(d,(70,646),'Windows: plan + slide deck + mail receipts + dashboard findings',21)
        text(d,(70,691),'Shown work is a simulation; the animation does not execute code or send email.',17,MUTED)
    elif stage==1:
        text(d,(70,566),'One project ID connects local work and cloud runs',23,bold=True)
        text(d,(70,608),'Commit -> deploy -> process data -> train -> evaluate -> record outcome',21)
        text(d,(70,646),'GPU runtime and dataset training tokens remain separate from agent tokens.',20,MUTED)
        text(d,(70,691),'Example metric only. Large datasets and checkpoints remain in cloud storage.',17,MUTED)
    elif stage==2:
        text(d,(70,566),'Read local agent usage logs; preserve source and project identity',23,bold=True)
        text(d,(70,609),'.claude + .codex -> versioned parser -> sealed usage bundle -> SSH collection',21)
        text(d,(70,650),'Verify checksum -> deduplicate -> commit ledger -> acknowledge receipt',21)
        text(d,(70,691),'Read supported usage records only; exclude credentials. Fields depend on client/version.',17,MUTED)
    elif stage==3:
        text(d,(70,566),'Previous-day ledger  /  tokens by project',23,bold=True)
        f=eased(p*1.7)
        for j,(name,v) in enumerate(zip(['Research','Data analysis','Software','Train / eval','Prototyping','Reports'],[180,180,90,40,20,10])):
            x=70+(j//3)*425;y=607+(j%3)*31;text(d,(x,y),name,17)
            box(d,(x+120,y+4,x+310,y+23),BG,r=4)
            box(d,(x+120,y+4,x+121+int(v/180*190*f),y+23),COLORS[j],r=4)
            text(d,(x+320,y),f'{int(v*f)}k',17)
        text(d,(955,615),f'{sum(int(v*f) for v in [180,180,90,40,20,10])}k tokens',28,COLORS[0],True)
        text(d,(955,660),'Daily total',18,MUTED)
        text(d,(70,705),'Late data revises totals; offline sources stay visibly incomplete.',16,MUTED)
    else:
        text(d,(70,566),'Previous Monday-Sunday  /  weekly review',23,bold=True)
        for j,(day,v) in enumerate(zip(['M','T','W','T','F','S','S'],DAYS)):
            f=eased(p*10-j)
            x=77+j*66;bh=int(v/760*83*f)
            box(d,(x,700-bh,x+38,700),COLORS[0],r=3)
            text(d,(x+10,704),day,15,MUTED)
        subtotal=sum(v*eased(p*10-j) for j,v in enumerate(DAYS))
        text(d,(599,605),f'{subtotal/1000:.2f}M tokens',28,COLORS[0],True)
        text(d,(599,644),'GPT-6-Astra / 6.1-Sol | Sonnet5.5 / Opus5.5',19)
        text(d,(599,676),'Prototyping: Qwen3.8-27B + Kimi K3',19)
        text(d,(599,703),'Self-hosted models | progress + optimization review',16,MUTED)
    text(d,(48,749),'Illustrative usage | API charges, subscription allocations and cloud costs stay separate.',17,MUTED)
    for j in range(5):line(d,(48+j*241,788),(269+j*241,788),COLORS[0] if j<=stage else BORDER,4)
    return im

def diagram():
    im=Image.new('RGB',(1600,1150),BG);d=ImageDraw.Draw(im)
    text(d,(64,38),'PROJECT TOKEN DISTRIBUTION',20,COLORS[0],True)
    text(d,(64,76),'Which models power each project?',44,bold=True)
    text(d,(64,140),'Illustrative week  |  4.10 million agent tokens  |  Input + output, cache counted once',23,MUTED)
    text(d,(64,188),'GPT / CLAUDE',17,MUTED,True)
    text(d,(64,272),'PROTOTYPING / SELF-HOSTED',17,MUTED,True)
    for i,(m,c) in enumerate(zip(MODELS,COLORS)):
        x=64+i*377 if i<4 else 64+(i-4)*750
        y=229 if i<4 else 313
        box(d,(x,y,x+18,y+18),c,r=4);text(d,(x+29,y-8),m,23)
    left=388;right=1450;top=385;scale=(right-left)/1100
    for tick in [0,200,400,600,800,1000,1100]:
        x=left+tick*scale;line(d,(x,top-12),(x,top+560),BORDER,1)
        text(d,(x-18,top+582),f'{tick:,}k',19,MUTED)
    for i,(name,vals) in enumerate(zip(PROJECTS,VALUES)):
        y=top+i*96;text(d,(64,y+12),name,23,bold=True)
        x=left
        for v,c in zip(vals,COLORS):
            end=x+v*scale
            if v:d.rectangle((x,y,end,y+60),fill=c)
            if v>=40:
                s=f'{v}k';tw=d.textbbox((0,0),s,font=font(18,True))[2]
                text(d,((x+end-tw)/2,y+18),s,18,BG,True)
            x=end
        text(d,(x+15,y+17),f'{sum(vals):,}k',22,bold=True)
    text(d,(left,top+624),'Agent tokens per project (thousands)',21,MUTED)
    text(d,(64,1073),'Illustrative allocation | Input + output; cache counted once',21,MUTED)
    text(d,(64,1110),'Prototyping uses self-hosted Qwen and Kimi. GPU costs and dataset training tokens are separate.',21,MUTED)
    im.save(OUT/'project-token-distribution.png')
    with (OUT/'example-token-data.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.writer(f);writer.writerow(['project']+MODELS+['total_tokens'])
        for name,values in zip(PROJECTS,VALUES):writer.writerow([name]+[v*1000 for v in values]+[sum(values)*1000])
    return im

if __name__=='__main__':
    diagram()
    fps=15;seconds=40
    writer=imageio_ffmpeg.write_frames(str(OUT/'logging-daily-weekly.mp4'),(W,H),fps=fps,codec='libx264',pix_fmt_in='rgb24',pix_fmt_out='yuv420p',quality=8,output_params=['-movflags','+faststart'])
    writer.send(None)
    previews=[]
    for i in range(fps*seconds):
        im=frame(i/fps);writer.send(im.tobytes())
        if i in [90,210,330,450,570]: previews.append(im.copy())
    writer.close()
    # GIF supplies a portable infinite-loop version; MP4 loops in its HTML player.
    gif_frames=[frame(i/5).resize((960,600)).quantize(colors=96) for i in range(seconds*5)]
    gif_frames[0].save(OUT/'logging-daily-weekly.gif',save_all=True,append_images=gif_frames[1:],duration=200,loop=0,optimize=False)
    frame(0).save(OUT/'animation-poster.png')
    contact=Image.new('RGB',(1280,1200),BG)
    for i,im in enumerate(previews):contact.paste(im.resize((640,400)),((i%2)*640,(i//2)*400))
    contact.save(OUT/'animation-storyboard.png')
    print(json.dumps({'duration_seconds':seconds,'fps':fps,'total_example_tokens':sum(map(sum,VALUES))*1000,'files':[p.name for p in OUT.iterdir()]},indent=2))
