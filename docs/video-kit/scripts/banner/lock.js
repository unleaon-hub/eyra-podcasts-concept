// EYRA footer lockup: thin wordmark, tagline in tracked caps justified to the wordmark's ink edges
window.lockup=function(cv,cap,o={}){
 const ink=o.ink||'#20241f',mut=o.muted||'#57594f',WT=o.wordWeight||260,TT=o.tagWeight||450,tag=o.tag||'YOUR EXPERTS FOR EVERYDAY LIFE';
 const g=cv.getContext('2d');
 // find font size for requested cap height
 g.font=`${WT} 100px M`;const capR=g.measureText('E').actualBoundingBoxAscent/100;const fs=cap/capR;
 g.font=`${WT} ${fs}px M`;g.letterSpacing=(o.wordTrack??-0.03)*fs+'px';
 const m=g.measureText('EYRA');const L=m.actualBoundingBoxLeft,R=m.actualBoundingBoxRight,inkW=L+R; // ink box rel. to origin
 // tagline: pick size so tracking ~ .2em, then solve exact tracking to match ink width
 const n=tag.length;g.font=`${TT} 100px M`;g.letterSpacing='0px';let m0=g.measureText(tag);const w100=m0.actualBoundingBoxLeft+m0.actualBoundingBoxRight;
 let tfs=inkW/(w100/100+(o.tagTrack||0.2)*(n-1));if(o.tagSize)tfs=o.tagSize;
 g.font=`${TT} ${tfs}px M`;m0=g.measureText(tag);const w0=m0.actualBoundingBoxLeft+m0.actualBoundingBoxRight;const ls=(inkW-w0)/(n-1);
 g.letterSpacing=ls+'px';const mt=g.measureText(tag);const tcap=g.measureText('E').actualBoundingBoxAscent;
 const gap=o.gap||cap*0.17,pad=Math.ceil(fs*0.05);
 const W=Math.ceil(inkW)+2*pad,H=Math.ceil(cap+gap+tcap)+2*pad;const dpr=o.dpr||1;
 cv.width=W*dpr;cv.height=H*dpr;cv.style.width=W+'px';cv.style.height=H+'px';g.scale(dpr,dpr);
 g.font=`${WT} ${fs}px M`;g.letterSpacing=(o.wordTrack??-0.03)*fs+'px';g.fillStyle=ink;g.textBaseline='alphabetic';g.fillText('EYRA',pad+L,pad+cap);
 g.font=`${TT} ${tfs}px M`;g.letterSpacing=ls+'px';g.fillStyle=mut;g.fillText(tag,pad+mt.actualBoundingBoxLeft,pad+cap+gap+tcap);
 return {W,H,pad,inkW,cap,tcap,tfs,ls:ls/tfs,fs,tl:pad+mt.actualBoundingBoxLeft-mt.actualBoundingBoxLeft,check:[L,R,mt.actualBoundingBoxLeft,mt.actualBoundingBoxRight]}
};
