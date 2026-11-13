/* EYRA voice orb v2 — one round button, no text.
   idle → connecting → listening ⇄ speaking; in a call the orb itself ends it.
   Engine API: window.eyraVoice.{listening(), speaking(), level(0…1), idle(), error(reason), state(), sound(on)}
   Events on window: eyra-voice-start, eyra-voice-end {detail:{by}}, eyra-voice-error {detail:{reason}} */
(()=>{const fab=document.getElementById('voice-fab');if(!fab)return;
const btn=fab.querySelector('.vf-btn'),live=fab.querySelector('.vf-sr');
const A={idle:'Голосовой консультант EYRA: начать разговор',connecting:'Подключение. Нажмите, чтобы отменить',listening:'Говорите, консультант слушает. Нажмите, чтобы завершить',speaking:'Консультант отвечает. Нажмите, чтобы завершить'};
const SAY={connecting:'Подключаю консультанта',listening:'Слушаю',speaking:'Консультант отвечает',idle:'Разговор завершён'};
const ERR={'mic-denied':'Разрешите доступ к микрофону',network:'Не удалось подключиться. Попробуйте ещё раз'};
const rm=matchMedia('(prefers-reduced-motion: reduce)');
let armT,errT,ptr='mouse';
const emit=(n,d)=>window.dispatchEvent(new CustomEvent(n,{detail:d}));
const say=t=>{live.textContent='';requestAnimationFrame(()=>live.textContent=t)};
const set=(s,quiet)=>{const prev=fab.dataset.state;fab.dataset.state=s;fab.classList.toggle('in-call',s!=='idle');btn.setAttribute('aria-label',A[s]);
  btn.title=s==='idle'?'Голосовой консультант':'Завершить разговор';if(!quiet&&prev!==s)say(SAY[s]);
  if(s==='idle'){fab.classList.remove('is-armed','hold');fab.style.setProperty('--vf-lvl',0)}};

/* ── optional sounds: off by default. On with data-sound="on" on #voice-fab or eyraVoice.sound(true).
   Never plays with prefers-reduced-motion, when muted (localStorage eyraVoiceMute=1) or while page audio plays. */
let ac;const soundOn=()=>fab.dataset.sound==='on'&&!rm.matches&&localStorage.getItem('eyraVoiceMute')!=='1'&&![...document.querySelectorAll('audio,video')].some(m=>!m.paused&&!m.muted);
const chime=(up)=>{if(!soundOn())return;try{ac=ac||new (window.AudioContext||window.webkitAudioContext)();const t=ac.currentTime;
  (up?[587.33,880]:[880,587.33]).forEach((f,i)=>{const o=ac.createOscillator(),g=ac.createGain();o.type='sine';o.frequency.value=f;
    const s=t+i*.09;g.gain.setValueAtTime(0,s);g.gain.linearRampToValueAtTime(.035,s+.015);g.gain.exponentialRampToValueAtTime(.0001,s+.16);
    o.connect(g).connect(ac.destination);o.start(s);o.stop(s+.18)})}catch(e){}};

const start=(pointer=true)=>{clearTimeout(errT);fab.classList.remove('is-err-net','is-blink');set('connecting');if(pointer)fab.classList.add('hold');chime(true);emit('eyra-voice-start')};
const end=(by='user')=>{clearTimeout(armT);if(fab.dataset.state==='idle')return;set('idle');chime(false);emit('eyra-voice-end',{by})};
/* errors: no red. mic-denied → one soft blink back to idle; network → arc dims, then idle */
const error=(reason='network')=>{clearTimeout(armT);clearTimeout(errT);const msg=ERR[reason]||ERR.network;
  const finish=()=>{fab.classList.remove('is-err-net');set('idle',true);say(msg)};
  emit('eyra-voice-error',{reason});
  if(reason==='mic-denied'){finish();fab.classList.remove('is-blink');void fab.offsetWidth;fab.classList.add('is-blink');errT=setTimeout(()=>fab.classList.remove('is-blink'),700)}
  else{fab.dataset.state='connecting';fab.classList.add('is-err-net');errT=setTimeout(finish,rm.matches?0:650)}};

btn.addEventListener('pointerleave',()=>fab.classList.remove('hold'));btn.addEventListener('blur',()=>fab.classList.remove('hold'));
btn.addEventListener('pointerdown',e=>{ptr=e.pointerType||'mouse'});
btn.addEventListener('click',e=>{
  if(fab.classList.contains('is-err-net'))return;
  if(fab.dataset.state==='idle'){ptr='mouse';start(e.detail>0);return} // keyboard (detail 0): no hold, focus shows × at once
  // touch has no hover: first tap shows ×, second tap within 3 s ends (no accidental hang-ups)
  if(ptr==='touch'&&!fab.classList.contains('is-armed')){fab.classList.add('is-armed');clearTimeout(armT);armT=setTimeout(()=>fab.classList.remove('is-armed'),3000);ptr='mouse';return}
  ptr='mouse';end('user')});
addEventListener('keydown',e=>{if(e.key==='Escape'&&fab.classList.contains('in-call'))end('user')});

/* light footer → darker ripples; step aside where the footer fills the bottom-right (not during a call) */
const foot=document.querySelector('footer');
if(foot){new IntersectionObserver(([e])=>fab.classList.toggle('on-paper',e.isIntersecting&&e.boundingClientRect.top<innerHeight-80),{threshold:[0,.1,.2]}).observe(foot);
  new IntersectionObserver(([e])=>fab.classList.toggle('at-footer',e.isIntersecting),{rootMargin:'0px 0px -120px 0px'}).observe(foot)}

/* bottom bars (mini-player etc.): marker = .mini-player or [data-mini-player] or [data-bottom-bar].
   While a marked bar is visible the orb sits 12 px above its top edge. */
const BARS='[data-mini-player],.mini-player,[data-bottom-bar]';let raf;
const syncBars=()=>{cancelAnimationFrame(raf);raf=requestAnimationFrame(()=>{let top=innerHeight;
  for(const el of document.querySelectorAll(BARS)){if(el.hidden||!el.getClientRects().length)continue;const r=el.getBoundingClientRect();if(r.height&&r.bottom>innerHeight-40&&r.top>innerHeight*.5)top=Math.min(top,r.top)}
  const base=parseFloat(getComputedStyle(fab).getPropertyValue('--vf-bottom'))||24;
  const lift=top<innerHeight?Math.max(0,Math.round(innerHeight-top+12-base)):0;fab.style.setProperty('--vf-lift',lift+'px');fab.classList.toggle('above-bar',lift>0)})};
new MutationObserver(ms=>{if(ms.some(m=>!fab.contains(m.target)))syncBars()}).observe(document.body,{subtree:true,childList:true,attributes:true,attributeFilter:['hidden','class','style','data-mini-player','data-bottom-bar']});
addEventListener('resize',syncBars);syncBars();

window.eyraVoice={listening(){set('listening')},speaking(){set('speaking')},
  level(v){fab.style.setProperty('--vf-lvl',Math.max(0,Math.min(1,+v||0)).toFixed(2))},
  idle(){end('engine')},error,state:()=>fab.dataset.state,sound(on){fab.dataset.sound=on?'on':'off'}};
})();
