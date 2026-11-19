# Ken-Burns slideshow of all 10 scenes for the VK live cover: 1080x1920, 30 fps, static lockup on top
import subprocess,numpy as np
from PIL import Image
from live import bg,es,LY
FPS=30;D=2.9;X=0.6;CW,CH=1080,1920
B=[bg(e)[0] for e in es]
L=Image.open('lock-120.png').convert('RGBA');a=L.split()[3].point(lambda v:int(v*0.86));L.putalpha(a)
N=len(es);total=N*D-(N-1)*X;nf=int(round(total*FPS))
def kb(i,t):  # t in [0,1] within the slide's own span
  z0,z1=(1.0,1.07) if i%2==0 else (1.07,1.0)
  ease=t*t*(3-2*t);z=z0+(z1-z0)*ease
  dx=(1 if i%3==0 else -1 if i%3==1 else 0)*14*(ease-.5);dy=-10*(ease-.5)
  w,h=CW/z,CH/z;cx=CW/2+dx;cy=CH*0.52+dy
  x0=min(max(cx-w/2,0),CW-w);y0=min(max(cy-h/2,0),CH-h)
  return B[i].transform((CW,CH),Image.EXTENT,(x0,y0,x0+w,y0+h),Image.BICUBIC)
cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{CW}x{CH}','-r',str(FPS),'-i','-',
 '-f','lavfi','-i','anullsrc=r=48000:cl=stereo','-t',f'{nf/FPS:.3f}','-c:v','libx264','-preset','slow','-crf','21','-profile:v','high','-level','4.2','-pix_fmt','yuv420p',
 '-g','60','-c:a','aac','-b:a','128k','-shortest','-movflags','+faststart','live-cover.mp4']
p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
for f in range(nf):
  t=f/FPS;H=D-X;i=min(int(t//H),N-1)
  fr=kb(i,min((t-i*H)/D,1))
  if i>0 and t<(i-1)*H+D:  # crossfade from the previous slide
    k=(t-i*H)/X;k=k*k*(3-2*k)
    fr=Image.blend(kb(i-1,min((t-(i-1)*H)/D,1)),fr,k)
  if i==N-1 and t>i*H+D-X:  # seamless loop: fade back into the very first frame
    k=(t-(i*H+D-X))/X;k=min(1,k);k=k*k*(3-2*k);fr=Image.blend(fr,kb(0,0),k)
  fr=fr.convert('RGBA');fr.alpha_composite(L,((CW-L.width)//2,LY))
  p.stdin.write(fr.convert('RGB').tobytes())
p.stdin.close();p.wait();print('frames',nf,'dur',nf/FPS)
