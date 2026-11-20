import cv2, numpy as np, sys
cx,cy,ax,ay=[int(v) for v in sys.argv[1:5]]
A=cv2.imread('../template/work/asya-16x9-up.jpg'); B=cv2.imread('scenes-f/asya-16x9-up.jpg'); M=np.load('/tmp/asyaM.npy')
Aw=cv2.warpAffine(A,M,(1920,1080),flags=cv2.INTER_LANCZOS4)
m=np.zeros((1080,1920),np.float32);cv2.ellipse(m,(cx,cy),(ax,ay),0,0,360,1,-1);m=cv2.GaussianBlur(m,(0,0),16)[...,None]
sel=m[...,0]>.5;Af=Aw.astype(np.float32);Bf=B.astype(np.float32)
for c in range(3):
    a=Af[...,c][sel];b=Bf[...,c][sel];Af[...,c]=(Af[...,c]-a.mean())*(0.5+0.5*b.std()/a.std())+b.mean()
out=np.clip(Bf*(1-m)+Af*m,0,255).astype('uint8');cv2.imwrite('/tmp/asya-fix.jpg',out,[cv2.IMWRITE_JPEG_QUALITY,95])
d=320;s=np.hstack([cv2.resize(x[cy-d:cy+d,cx-d:cx+d],(480,480)) for x in (Aw,B,out)]);cv2.imwrite('/workspace/asya-fix-cmp.jpg',s)
