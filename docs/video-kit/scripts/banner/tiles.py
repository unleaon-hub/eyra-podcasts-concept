# Expert tiles with consistent face framing: face (YuNet box) = 36% of tile height, face centre at 43% from top.
import json
from PIL import Image, ImageFilter
import os
O=os.path.dirname(os.path.abspath(__file__))+'/';W=O+'../template/work/'
F=json.load(open(O+'faces.json'));AR=104/134
for e,(x,y,w,h) in F.items():
  im=Image.open(W+e+'-16x9-up.jpg').convert('RGB')
  ch=h/0.36; cw=ch*AR; cx=x+w/2; cy=y+h/2
  x0=round(cx-cw/2); y0=round(cy-0.43*ch); cw=round(cw); ch=round(ch)
  x0=max(0,min(1920-cw,x0))
  t=Image.new('RGB',(cw,ch))
  if y0<0:
    pad=-y0; strip=im.crop((x0,0,x0+cw,6)).resize((cw,pad),Image.BILINEAR).filter(ImageFilter.GaussianBlur(8))
    t.paste(strip,(0,0)); t.paste(im.crop((x0,0,x0+cw,ch-pad)),(0,pad))
  else: t.paste(im.crop((x0,y0,x0+cw,min(1080,y0+ch))),(0,0))
  t.resize((464,598),Image.LANCZOS).save(O+f't-{e}.jpg',quality=94); print(e,x0,y0,cw,ch)
