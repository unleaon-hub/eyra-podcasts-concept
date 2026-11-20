# 3:4 scenes for the Yandex Direct batch: the graded 16:9 scene gets taller walls from an AI outpaint
# (batch/ext/<id>-<v>-out.jpg, made from batch/ext/<id>-<v>-in.jpg). Only the NEW area above the frame comes
# from the outpaint; every original pixel (expert included) is the graded scene itself.
import cv2, numpy as np, json, re
EXT={'default':360,'asya':480}
geo=json.loads(open('batch/geo.js').read().split('window.GEO=',1)[1].strip().rstrip(';'))
orb=cv2.ORB_create(5000); bf=cv2.BFMatcher(cv2.NORM_HAMMING,crossCheck=True)
for e in 'mira kira asya eva sofia lera vera nika maya alisa'.split():
  for v in 'ab':
    k=f'{e}-{v}'; a=cv2.imread(f'batch/scenes/{k}.jpg'); o=cv2.imread(f'batch/ext/{k}-out.jpg')
    ka,da=orb.detectAndCompute(cv2.cvtColor(a,cv2.COLOR_BGR2GRAY),None)
    ko,do=orb.detectAndCompute(cv2.cvtColor(o,cv2.COLOR_BGR2GRAY),None)
    m=sorted(bf.match(do,da),key=lambda x:x.distance)[:800]
    M,inl=cv2.estimateAffinePartial2D(np.float32([ko[x.queryIdx].pt for x in m]),np.float32([ka[x.trainIdx].pt for x in m]),ransacReprojThreshold=4)
    X=EXT.get(e,EXT['default']); H=1080+X
    M2=M.copy(); M2[1,2]+=X
    w=cv2.warpAffine(o,M2,(1920,H),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
    cov=cv2.warpAffine(np.full(o.shape[:2],255,np.uint8),M2,(1920,H),flags=cv2.INTER_NEAREST)
    # columns not covered by the outpaint: replicate the nearest covered column
    cols=np.where(cov[max(0,X-200):X].min(0)>0)[0]; c0,c1=cols.min(),cols.max()
    w[:, :c0]=w[:, c0:c0+1]; w[:, c1+1:]=w[:, c1:c1+1]
    # low-frequency colour match of the extension to the scene (band just under the seam)
    band=slice(X+8,X+90)
    d=a[8:90].astype(np.float32).mean(0)-w[band].astype(np.float32).mean(0)   # per column
    d=cv2.GaussianBlur(d.reshape(1,1920,3),(0,0),sigmaX=25).reshape(1920,3)
    w=np.clip(w.astype(np.float32)+d[None],0,255)
    out=w.copy(); out[X:]=a
    # feather the seam over 70 px
    for i in range(70):
      t=i/69; out[X+i]=a[i]*t+w[X+i]*(1-t)
    cv2.imwrite(f'batch/scenes/{k}-3x4.jpg',out.astype(np.uint8),[cv2.IMWRITE_JPEG_QUALITY,95])
    gk=dict(geo[k]); gk['hcy']+=X; gk['top']+=X; gk['ext']=X; geo[k+'-3x4']=gk
    print(k,int(inl.sum()),'scale %.2f'%np.hypot(M[0,0],M[1,0]),'cover x',c0,c1,'ext',X)
s=open('batch/geo.js').read(); hdr=s.split('window.GEO=',1)[0]
open('batch/geo.js','w').write(hdr+'window.GEO='+json.dumps(geo)+';\n')
