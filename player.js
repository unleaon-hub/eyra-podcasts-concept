(function(){
  const $ = (s, r=document) => r.querySelector(s);
  const $$ = (s, r=document) => [...r.querySelectorAll(s)];
  const speeds = [1, 1.25, 1.5, 2];
  let speedIndex = 0;
  let playing = document.body.classList.contains("is-playing");
  let progress = Number(document.body.dataset.progress || 0.42);
  let timer = null;

  function iconPlay(){return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.5v13l11-6.5-11-6.5z" fill="currentColor" stroke="none"/></svg>'}
  function iconPause(){return '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="6.5" y="5" width="3.5" height="14" rx="1" fill="currentColor" stroke="none"/><rect x="14" y="5" width="3.5" height="14" rx="1" fill="currentColor" stroke="none"/></svg>'}

  function isGlobalPlay(btn){
    return btn.closest(".mini-player, .full-player, .continue, .wave, .show-actions, .show-sticky, .now-page, .ritual");
  }
  function setIcon(btn, on){
    const html = on ? iconPause() : iconPlay();
    const svg = btn.querySelector("svg");
    if(svg) svg.outerHTML = html;
    else btn.insertAdjacentHTML("afterbegin", html);
    btn.setAttribute("aria-pressed", String(on));
    if(!btn.dataset.keepLabel){
      btn.setAttribute("aria-label", on ? "Пауза" : "Слушать");
    }
  }
  function setPlaying(on){
    playing = on;
    document.body.classList.toggle("is-playing", on);
    $$("[data-play]").forEach(btn=>{
      if(isGlobalPlay(btn) || btn.closest(".ep-item.is-active, .ep-row.is-active, .episode.is-active")){
        setIcon(btn, on);
        btn.classList.toggle("is-playing", on);
        if(btn.classList.contains("play-circle") || btn.classList.contains("btn-round-play") || btn.classList.contains("play-float") || btn.classList.contains("main")){
          btn.classList.toggle("is-on", on);
        }
      }
    });
    if(on) startTick(); else stopTick();
  }
  function startTick(){
    stopTick();
    timer = setInterval(()=>{
      progress = Math.min(0.995, progress + 0.00045);
      applyProgress();
    }, 400);
  }
  function stopTick(){ if(timer) clearInterval(timer); timer=null; }
  function fmt(sec){
    sec=Math.max(0,Math.floor(sec));
    return Math.floor(sec/60)+":"+String(sec%60).padStart(2,"0");
  }
  function applyProgress(){
    const dur = Number(document.body.dataset.duration || 7*60);
    const cur = progress * dur;
    $$("[data-progress]").forEach(el=>{ el.style.setProperty("--p", (progress*100).toFixed(2)+"%"); });
    $$("[data-time-cur]").forEach(el=>{ el.textContent = fmt(cur); });
    $$("[data-time-left]").forEach(el=>{ el.textContent = "-"+fmt(dur-cur); });
  }
  function openFull(open){
    const fp = $("#full-player");
    if(!fp) return;
    fp.classList.toggle("is-open", open);
    if(open) fp.removeAttribute("hidden"); else fp.setAttribute("hidden","");
    fp.setAttribute("aria-hidden", String(!open));
    document.body.style.overflow = open ? "hidden" : "";
    if(open){
      fp.setAttribute("tabindex","-1");
      try{ fp.focus({preventScroll:true}); }catch(e){ fp.focus(); }
    }
  }
  function cycleSpeed(){
    speedIndex = (speedIndex+1)%speeds.length;
    const label = (speeds[speedIndex]%1===0? speeds[speedIndex]+"×" : String(speeds[speedIndex]).replace(".",",")+"×");
    $$("[data-speed]").forEach(el=>{ el.textContent = label; el.setAttribute("aria-label","Скорость "+label); });
  }

  document.addEventListener("click", (e)=>{
    const play = e.target.closest("[data-play]");
    if(play){
      e.preventDefault();
      const ep = play.closest("[data-episode], .ep-item, .ep-row, .card-ep, .card-show");
      if(ep){
        $$(".ep-item.is-active, .ep-row.is-active, .episode.is-active").forEach(n=>n.classList.remove("is-active"));
        ep.classList.add("is-active");
      }
      setPlaying(!playing);
      return;
    }
    const open = e.target.closest("[data-open-full]");
    if(open){ e.preventDefault(); openFull(true); return; }
    const close = e.target.closest("[data-close-full]");
    if(close){ e.preventDefault(); openFull(false); return; }
    const spd = e.target.closest("[data-speed]");
    if(spd){ e.preventDefault(); cycleSpeed(); return; }
    const mood = e.target.closest(".mood-btns button, .moods .chip, .filter, [data-filter]");
    if(mood){
      e.preventDefault();
      const group = mood.parentElement;
      $$("button, .chip, .filter", group).forEach(c=>{
        c.classList.toggle("is-on", c===mood);
        c.setAttribute("aria-pressed", String(c===mood));
      });
      return;
    }
    const view = e.target.closest("[data-view]");
    if(view){
      e.preventDefault();
      $$("[data-view]").forEach(b=>b.classList.toggle("is-on", b===view));
      const table = $(".ep-table");
      if(table) table.classList.toggle("is-compact", view.dataset.view==="compact");
      return;
    }
    const arrow = e.target.closest("[data-shelf-scroll]");
    if(arrow){
      e.preventDefault();
      const id = arrow.dataset.shelfScroll;
      const dir = Number(arrow.dataset.dir || 1);
      const rail = document.getElementById(id) || arrow.closest(".shelf")?.querySelector(".rail");
      if(rail) rail.scrollBy({left: dir * Math.min(rail.clientWidth*0.8, 640), behavior:"smooth"});
      return;
    }
    const like = e.target.closest(".like");
    if(like){
      e.preventDefault();
      like.classList.toggle("is-on");
      like.setAttribute("aria-pressed", String(like.classList.contains("is-on")));
      return;
    }
    const sleep = e.target.closest("[data-sleep]");
    if(sleep){
      e.preventDefault();
      const opts=["Выкл","15 мин","30 мин","45 мин"];
      let i = opts.indexOf(sleep.dataset.state||"Выкл");
      i = (i+1)%opts.length;
      sleep.dataset.state = opts[i];
      sleep.setAttribute("aria-label","Таймер сна: "+opts[i]);
      const lab = sleep.querySelector("[data-sleep-label]");
      if(lab) lab.textContent = opts[i]==="Выкл" ? "Таймер" : opts[i];
    }
  });
  document.addEventListener("keydown",(e)=>{
    if(e.key==="Escape") openFull(false);
    if(e.key===" " && !/input|textarea|button|a/i.test(e.target.tagName)){
      e.preventDefault(); setPlaying(!playing);
    }
  });

  setPlaying(playing);
  applyProgress();
  if($("#full-player") && document.body.dataset.openFull==="1"){
    openFull(true);
  }
})();
