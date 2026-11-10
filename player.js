(function(){
  const $ = (s, r=document) => r.querySelector(s);
  const $$ = (s, r=document) => [...r.querySelectorAll(s)];
  const speeds = [1, 1.25, 1.5, 2];
  let speedIndex = 0;
  const STORE = "eyra.podcast.playback";
  function readStore(){
    try{ return JSON.parse(localStorage.getItem(STORE) || "{}"); }catch(e){ return {}; }
  }
  function writeStore(){
    try{
      const prev = readStore();
      const now = window.EYRA_NOW || {};
      localStorage.setItem(STORE, JSON.stringify({
        progress, playing, speedIndex, updated: Date.now(),
        expert: now.expert || prev.expert,
        episode: now.episode || prev.episode,
        href: now.href || prev.href,
        title: now.title || prev.title,
        name: now.name || prev.name,
        category: now.category || prev.category,
        eyebrow: now.eyebrow || prev.eyebrow,
        role: now.role || prev.role,
        photo: now.photo || prev.photo,
        accent: now.accent || prev.accent,
        url: now.url || prev.url,
        duration: now.duration || prev.duration
      }));
    }catch(e){}
  }
  function isPlayerPage(){
    return !!(document.querySelector(".now-page") && /player\.html/.test(location.pathname));
  }
  function podcastReferrer(){
    const ref = document.referrer;
    if(!ref) return null;
    try{
      const u = new URL(ref);
      if(u.origin !== location.origin) return null;
      const file = (u.pathname.split("/").pop() || "index.html") || "index.html";
      const ok = /^(hub|show|topic|mood|experts|index)\.html$/.test(file) || file === "" || file === "eyra-podcasts-concept";
      return ok ? (u.pathname + u.search + u.hash) : null;
    }catch(e){ return null; }
  }
  function goPlayerBack(){
    writeStore();
    const ref = podcastReferrer();
    if(ref && history.length > 1){ history.back(); return; }
    const slug = (window.EYRA_NOW && window.EYRA_NOW.expert) || "";
    location.href = slug ? "show.html?e="+encodeURIComponent(slug) : "hub.html";
  }
  function closePlayer(){
    writeStore();
    const ref = podcastReferrer();
    if(ref && history.length > 1){ history.back(); return; }
    if(ref){ location.href = ref; return; }
    location.href = "hub.html";
  }
  function restoreMiniFromStore(){
    if(isPlayerPage()) return;
    const s = readStore();
    const mini = document.querySelector(".mini-player");
    if(!mini || !s || !s.episode) return;
    const img = mini.querySelector(".typo-cover img");
    if(img && s.photo){ img.src = s.photo; img.alt = s.name || ""; }
    const ty = mini.querySelector(".typo-cover");
    if(ty && s.accent) ty.style.setProperty("--accent", s.accent);
    const eye = mini.querySelector(".typo-cover .eyebrow");
    if(eye && s.eyebrow) eye.textContent = s.eyebrow;
    const coverB = mini.querySelector(".typo-cover b");
    if(coverB && s.title) coverB.textContent = s.title;
    const title = mini.querySelector(".meta b");
    if(title && s.title) title.textContent = s.title;
    const sub = mini.querySelector(".meta span");
    if(sub) sub.textContent = [s.name, s.category].filter(Boolean).join(" · ");
    const href = s.href || ("player.html?e="+(s.expert||"")+"&ep="+(s.episode||""));
    mini.querySelectorAll("[data-open-player]").forEach(a=>{
      if(a.tagName === "A") a.href = href;
    });
    const read = mini.querySelector(".read-quiet, .read-link");
    if(read && s.url){
      read.href = s.url;
      read.setAttribute("target","_blank");
      read.setAttribute("rel","noopener");
    }
    if(s.duration) document.body.dataset.duration = String(s.duration);
    window.EYRA_NOW = Object.assign({}, window.EYRA_NOW, {
      expert: s.expert, episode: s.episode, href: href,
      title: s.title, name: s.name, category: s.category, eyebrow: s.eyebrow,
      role: s.role, photo: s.photo, accent: s.accent, url: s.url, duration: s.duration
    });
    mini.hidden = false;
    mini.removeAttribute("aria-hidden");
    if(typeof s.progress === "number" && Number.isFinite(s.progress)){
      progress = Math.min(0.995, Math.max(0, s.progress));
    }
    if(typeof s.playing === "boolean") playing = s.playing;
    if(typeof s.speedIndex === "number" && s.speedIndex >= 0 && s.speedIndex < speeds.length){
      speedIndex = s.speedIndex;
    }
  }
  function playerHref(){
    const base = (window.EYRA_NOW && window.EYRA_NOW.href) ? window.EYRA_NOW.href : "player.html";
    const u = new URL(base, location.href);
    u.searchParams.set("p", progress.toFixed(4));
    u.searchParams.set("play", playing ? "1" : "0");
    if(speedIndex) u.searchParams.set("spd", String(speeds[speedIndex]));
    return u.pathname + u.search + u.hash;
  }
  function goToPlayer(e){
    if(e) e.preventDefault();
    writeStore();
    const onPlayer = document.querySelector(".now-page") && /player\.html/.test(location.pathname);
    if(onPlayer){
      window.scrollTo({top:0, behavior:"smooth"});
      return;
    }
    location.href = playerHref();
  }
  const params = new URLSearchParams(location.search);
  const stored = readStore();
  let playing = document.body.classList.contains("is-playing");
  let progress = Number(document.body.dataset.progress || 0.42);
  let timer = null;
  if(params.has("p") && Number.isFinite(Number(params.get("p")))){
    progress = Math.min(0.995, Math.max(0, Number(params.get("p"))));
  }else if(typeof stored.progress === "number" && Number.isFinite(stored.progress)){
    progress = Math.min(0.995, Math.max(0, stored.progress));
  }
  if(params.has("play")){
    playing = params.get("play") !== "0";
  }else if(typeof stored.playing === "boolean"){
    playing = stored.playing;
  }
  if(params.has("spd")){
    const s = Number(String(params.get("spd")).replace(",", "."));
    const idx = speeds.indexOf(s);
    if(idx >= 0) speedIndex = idx;
  }else if(typeof stored.speedIndex === "number" && stored.speedIndex >= 0 && stored.speedIndex < speeds.length){
    speedIndex = stored.speedIndex;
  }

  function iconPlay(){return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.5v13l11-6.5-11-6.5z" fill="currentColor" stroke="none"/></svg>'}
  function iconPause(){return '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="6.5" y="5" width="3.5" height="14" rx="1" fill="currentColor" stroke="none"/><rect x="14" y="5" width="3.5" height="14" rx="1" fill="currentColor" stroke="none"/></svg>'}

  function isGlobalPlay(btn){
    return btn.closest(".mini-player, .continue, .wave, .show-actions, .show-sticky, .now-page, .ritual, .feature");
  }
  function setIcon(btn, on){
    if(btn.classList.contains("ep-card-num")){
      btn.setAttribute("aria-pressed", String(on));
      return;
    }
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
    writeStore();
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
    writeStore();
  }
  function applySpeed(){
    const label = (speeds[speedIndex]%1===0? speeds[speedIndex]+"×" : String(speeds[speedIndex]).replace(".",",")+"×");
    $$("[data-speed]").forEach(el=>{ el.textContent = label; el.setAttribute("aria-label","Скорость "+label); });
    writeStore();
  }
  function cycleSpeed(){
    speedIndex = (speedIndex+1)%speeds.length;
    applySpeed();
  }

  document.addEventListener("click", (e)=>{
    const play = e.target.closest("[data-play]");
    if(play){
      e.preventDefault();
      e.stopPropagation();
      const ep = play.closest("[data-episode], .ep-item, .ep-row, .card-ep, .card-show");
      if(ep){
        $$(".ep-item.is-active, .ep-row.is-active, .episode.is-active").forEach(n=>n.classList.remove("is-active"));
        ep.classList.add("is-active");
      }
      setPlaying(!playing);
      return;
    }
    const openPlayer = e.target.closest("[data-open-player]");
    if(openPlayer){ goToPlayer(e); return; }
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
      return;
    }
    const backBtn = e.target.closest("[data-player-back]");
    if(backBtn){ e.preventDefault(); goPlayerBack(); return; }
    const closeBtn = e.target.closest("[data-player-close]");
    if(closeBtn){ e.preventDefault(); closePlayer(); return; }
  });
  document.addEventListener("keydown",(e)=>{
    if(e.key==="Escape" && isPlayerPage()){
      const menu = document.querySelector(".journal-menu");
      if(menu && menu.open) return;
      e.preventDefault();
      closePlayer();
      return;
    }
    if(e.key===" " && !/input|textarea|button|a/i.test(e.target.tagName)){
      e.preventDefault(); setPlaying(!playing);
    }
  });


  function initFeature(){
    const root = document.querySelector("[data-feature]");
    if(!root) return;
    const slides = [...root.querySelectorAll("[data-feat-slide]")];
    const dashes = [...root.querySelectorAll(".feature-dash")];
    const ups = [...root.querySelectorAll(".feature-up-card")];
    const n = slides.length;
    if(!n) return;
    let i = 0;
    let timer = null;
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    function go(next){
      i = (next + n) % n;
      slides.forEach((s,k)=>s.classList.toggle("is-on", k===i));
      dashes.forEach((b,k)=>b.classList.toggle("is-on", k===i));
      ups.forEach((b,k)=>b.classList.toggle("is-current", k===i));
      restart();
    }
    function restart(){
      if(timer){ clearTimeout(timer); timer=null; }
      if(reduce) return;
      if(root.matches(":hover")) return;
      timer = setTimeout(()=>go(i+1), 7000);
    }
    root.addEventListener("click",(e)=>{
      const prev = e.target.closest("[data-feat-prev]");
      const next = e.target.closest("[data-feat-next]");
      const jump = e.target.closest("[data-feat-go]");
      if(prev){ e.preventDefault(); go(i-1); }
      else if(next){ e.preventDefault(); go(i+1); }
      else if(jump){ e.preventDefault(); go(Number(jump.dataset.featGo)); }
    });
    root.addEventListener("mouseenter",()=>{ if(timer){ clearTimeout(timer); timer=null; } });
    root.addEventListener("mouseleave", restart);
    let x0=null;
    root.addEventListener("touchstart",(e)=>{ x0=e.changedTouches[0].clientX; }, {passive:true});
    root.addEventListener("touchend",(e)=>{
      if(x0==null) return;
      const dx=e.changedTouches[0].clientX-x0; x0=null;
      if(Math.abs(dx)>40) go(i + (dx<0?1:-1));
    }, {passive:true});
    restart();
  }
  initFeature();


  function initShowMore(){
    const btn=document.querySelector("[data-show-more]");
    if(!btn) return;
    btn.addEventListener("click",()=>{
      document.querySelectorAll(".ep-item.is-more, .mood-ep.is-more").forEach(el=>el.classList.remove("is-more"));
      btn.hidden=true;
    });
  }
  initShowMore();

  function initMiniOnPlayerPage(){
    const now = document.querySelector(".now-stage") || document.querySelector(".now-page");
    if(!now) return;
    const root = document.documentElement;
    root.classList.add("player-page", "now-in-view");
    root.style.setProperty("--mini", "0px");
    const mini = document.querySelector(".mini-player");
    if(mini){
      mini.hidden = true;
      mini.setAttribute("aria-hidden", "true");
    }
  }

  restoreMiniFromStore();
  applySpeed();
  setPlaying(playing);
  applyProgress();
  initMiniOnPlayerPage();
  window.addEventListener("pageshow", (e)=>{
    if(isPlayerPage()) return;
    const s = readStore();
    if(!s || !s.episode) return;
    if(typeof s.progress === "number") progress = Math.min(0.995, Math.max(0, s.progress));
    if(typeof s.playing === "boolean") playing = s.playing;
    if(typeof s.speedIndex === "number" && s.speedIndex >= 0 && s.speedIndex < speeds.length) speedIndex = s.speedIndex;
    restoreMiniFromStore();
    applySpeed();
    setPlaying(playing);
    applyProgress();
  });
  window.EYRA_PLAYBACK = { sync: writeStore, back: goPlayerBack, close: closePlayer };
  if(params.has("p") || params.has("play") || params.has("spd")){
    try{
      const u = new URL(location.href);
      u.searchParams.delete("p");
      u.searchParams.delete("play");
      u.searchParams.delete("spd");
      history.replaceState(null, "", u.pathname + (u.searchParams.toString() ? "?"+u.searchParams.toString() : "") + u.hash);
    }catch(e){}
  }
})();
