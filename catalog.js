/* EYRA podcast catalog — show, player, topic, mood, experts */
(function(){
  const NAME_SLUG = {
    "Ася":"asya","Кира":"kira","Вера":"vera","Лера":"lera","Мира":"mira",
    "Ника":"nika","Ева":"eva","Майя":"maya","София":"sofia","Алиса":"alisa"
  };
  const TOPICS = [
    {slug:"emotsii", name:"Эмоции и отношения", short:"Эмоции", accent:"#ddb79c", button:"#efdfd0"},
    {slug:"pitanie", name:"Питание и привычки", short:"Питание", accent:"#b9cebb", button:"#e1ebdd"},
    {slug:"astrologiya", name:"Астрология", short:"Астрология", accent:"#d8b988", button:"#f0e3cf"},
    {slug:"taro", name:"Таро", short:"Таро", accent:"#d4b8c9", button:"#e9dce6"},
    {slug:"numerologiya", name:"Нумерология", short:"Числа", accent:"#c7b9df", button:"#e7dff1"},
    {slug:"karera", name:"Карьера и самопрезентация", short:"Карьера", accent:"#d4afa3", button:"#eddbd0"},
    {slug:"obshchenie", name:"Друзья и связи", short:"Связи", accent:"#d8ba78", button:"#efe2c4", also:["netvorking"]},
    {slug:"dosug", name:"Отдых и впечатления", short:"Отдых", accent:"#a8bdd9", button:"#dce6f2"},
    {slug:"finansy", name:"Личные финансы", short:"Финансы", accent:"#b9c58e", button:"#e4e9cf"},
    {slug:"znakomstva", name:"Знакомства", short:"Знакомства", accent:"#d8a9ba", button:"#eedde4"}
  ];
  const NEW_TOPIC = {slug:"new", name:"Новое", short:"Новое", accent:"#ccb78f", button:"#efe4d2"};
  const MOODS = [
    {slug:"vecher", name:"Вечер", tint:"#c5d4eb", accent:"#8fa9cc", re:/вечер|ноч[ьюие]|перед сном|пятниц/i, fallback:"dosug"},
    {slug:"sily", name:"Силы", tint:"#d2e0c8", accent:"#9bb89a", re:/(?<![А-Яа-яЁё])сил[аыуе](?![А-Яа-яЁё])|выгор|восстанов|устал|энерг|истощен|нет сил|мало сил/i, fallback:"dosug"},
    {slug:"trevoga", name:"Тревога", tint:"#f0dccb", accent:"#ddb79c", re:/тревог|страх|волнен|паник|беспокой|отказ|одиноч|бессон/i, fallback:"emotsii"},
    {slug:"utro", name:"Утро", tint:"#f3e4c4", accent:"#d8b988", re:/(?<![А-Яа-яЁё])утр[оаеу](?![А-Яа-яЁё])|завтрак|с утра|утрен|подъ[её]м|начать день/i, fallback:"pitanie"},
    {slug:"vyhodnye", name:"Выходные", tint:"#d4d6f2", accent:"#a8abd4", re:/выходн|суббот|воскресень/i, fallback:"dosug"},
    {slug:"privychki", name:"Привычки", tint:"#c8eedd", accent:"#8ec9b0", re:/привычк|ритуал|режим дня|меню на|рутин|регуляр/i, fallback:"pitanie"}
  ];
  const $ = (s, r=document) => r.querySelector(s);
  const $$ = (s, r=document) => [...r.querySelectorAll(s)];
  let experts = [];
  let articles = [];

  function expert(id){
    if(!id) return experts.find(x=>x.slug==="maya") || experts[0];
    const key = String(id).toLowerCase();
    return experts.find(x=>x.slug===key) || experts.find(x=>x.name===id) || expert("maya");
  }
  function slugOf(article){ return NAME_SLUG[article.expert] || "maya"; }
  function episodesOf(ex){ return articles.filter(a=>a.expert===ex.name); }
  function episodeBySlug(slug){ return articles.find(a=>a.slug===slug); }
  function topicBy(id){
    if(!id || id==="new") return NEW_TOPIC;
    if(id==="netvorking") return TOPICS.find(t=>t.slug==="obshchenie");
    return TOPICS.find(t=>t.slug===id) || NEW_TOPIC;
  }
  function topicSlugs(t){
    if(t.slug==="new") return null;
    return [t.slug].concat(t.also||[]);
  }
  function episodesOfTopic(t){
    if(t.slug==="new") return articles.slice();
    const slugs = topicSlugs(t);
    return articles.filter(a=>slugs.includes(a.rubric));
  }
  function moodBy(id){ return MOODS.find(m=>m.slug===id) || MOODS[0]; }
  function interleaveByExpert(list){
    const bags = new Map();
    for(const a of list){
      const k = a.expert;
      if(!bags.has(k)) bags.set(k, []);
      bags.get(k).push(a);
    }
    const qs = [...bags.values()];
    const out = [];
    while(qs.some(q=>q.length)){
      for(const q of qs){ if(q.length) out.push(q.shift()); }
    }
    return out;
  }
  function episodesOfMood(m){
    const hit = articles.filter(a=>m.re.test(a.title+" "+(a.excerpt||"")));
    const used = new Set(hit.map(a=>a.slug));
    const counts = {};
    const uniq = () => Object.keys(counts).length;
    for(const a of hit) counts[a.expert]=(counts[a.expert]||0)+1;
    for(const a of articles){
      if(hit.length>=14 && uniq()>=4) break;
      if(used.has(a.slug)) continue;
      const same = a.rubric===m.fallback || (m.fallback==="obshchenie" && a.rubric==="netvorking");
      const n = counts[a.expert]||0;
      const needFaces = uniq()<4 && n===0;
      if((same && n<3) || needFaces || (!same && n<1 && hit.length<12)){
        hit.push(a); used.add(a.slug);
        counts[a.expert]=n+1;
      }
    }
    return interleaveByExpert(hit);
  }
  function showHref(ex){ return "show.html?e=" + ex.slug; }
  function topicHref(t){ return "topic.html?t=" + t.slug; }
  function moodHref(m){ return "mood.html?m=" + m.slug; }
  function playerHref(ep, extra){
    let href = "player.html?e=" + slugOf(ep) + "&ep=" + encodeURIComponent(ep.slug);
    if(extra && extra.t) href += "&t=" + encodeURIComponent(extra.t);
    if(extra && extra.m) href += "&m=" + encodeURIComponent(extra.m);
    return href;
  }
  function params(){ return new URLSearchParams(location.search); }
  function escapeHtml(s){
    return String(s).replace(/[&<>"']/g, c=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c]));
  }
  function playSvg(){
    return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.5v13l11-6.5-11-6.5z" fill="currentColor" stroke="none"/></svg>';
  }


  function eschePlaqueHtml(a, ex){
    const href = playerHref(a);
    const pastel = ex.button || "#efe4d2";
    return '<article class="esche-plaque" data-episode data-slug="'+a.slug+'" style="--accent:'+ex.accent+';--plaque:'+pastel+'">'+
      '<a class="esche-face" href="'+href+'">'+
        '<b>'+escapeHtml(a.title)+'</b>'+
        '<span class="mins">'+a.minutes+' мин</span>'+
      '</a>'+
      '<a class="play-float" href="'+href+'" aria-label="Слушать «'+escapeHtml(a.title)+'»">'+playSvg()+'</a>'+
    '</article>';
  }

  function fillExpertCard(root, ex){
    if(!root || !ex) return;
    const sec = root.querySelector("section.expert") || root;
    sec.id = ex.slug;
    sec.setAttribute("aria-labelledby", ex.slug + "-title");
    sec.style.setProperty("--accent", ex.accent);
    sec.style.setProperty("--button", ex.button);
    const h2 = sec.querySelector("h2");
    if(h2){ h2.id = ex.slug + "-title"; h2.innerHTML = ex.card.titleHtml; }
    const benefit = sec.querySelector(".benefit");
    if(benefit) benefit.textContent = ex.card.benefit;
    const desc = sec.querySelector(".expert-description");
    if(desc) desc.textContent = ex.card.description;
    const themes = sec.querySelector(".themes");
    if(themes) themes.innerHTML = ex.card.themes.map(t=>"<span>"+escapeHtml(t)+"</span>").join("");
    const cta = sec.querySelector("a.cta");
    if(cta){
      cta.href = ex.page;
      cta.setAttribute("data-expert-link", ex.slug);
      const span = cta.querySelector("span");
      if(span) span.textContent = ex.card.cta;
    }
    const portrait = sec.querySelector("a.portrait");
    if(portrait){
      portrait.href = ex.page;
      portrait.setAttribute("data-expert-link", ex.slug);
      portrait.setAttribute("aria-label", "Познакомиться: " + ex.name + " — " + ex.role.toLowerCase());
      const img = portrait.querySelector("img");
      if(img){
        img.src = ex.portrait;
        if(ex.portraitSrcset) img.srcset = ex.portraitSrcset; else img.removeAttribute("srcset");
        img.alt = ex.card.title;
      }
      const label = portrait.querySelector(".video-trigger > span:last-child");
      if(label){
        label.innerHTML = escapeHtml(ex.card.cta) + "<small>На личной странице эксперта</small>";
      }
    }
  }

  const CROP = ["50% 16%","62% 18%","38% 20%","50% 28%","44% 14%","58% 22%"];

  function renderEpTable(table, eps, extra){
    if(!table) return;
    extra = extra || {};
    const moreBtn = table.querySelector("[data-show-more]") || document.querySelector("[data-show-more]");
    $$(".ep-item, .mood-ep", table).forEach(n=>n.remove());
    const head = table.querySelector(".head");
    if(head) head.hidden = true;
    const frag = document.createDocumentFragment();
    const useCover = !!extra.cover;
    eps.forEach((ep, i)=>{
      const ex = expert(slugOf(ep));
      const href = playerHref(ep, extra);
      const artEl = document.createElement("article");
      const started = extra.markStarted !== false && i===0;
      artEl.className = "ep-item" + (useCover ? " has-cover" : " has-num") + (started ? " is-active is-started" : "") + (i>=10 ? " is-more" : "");
      artEl.dataset.episode = "";
      artEl.dataset.slug = ep.slug;
      artEl.style.setProperty("--accent", ex.accent);
      const label = 'Слушать «'+escapeHtml(ep.title)+'»';
      const eq = '<span class="eq" aria-hidden="true"><i></i><i></i><i></i></span>';
      const thumb = useCover
        ? '<a class="ep-card-thumb" href="'+href+'" style="--crop:'+CROP[i%CROP.length]+'"><img src="'+ex.photo+'" alt=""></a>'
        : '<button class="ep-card-num" data-play aria-label="'+label+'" type="button"><span class="n">'+(i+1)+'</span>'+eq+'</button>';
      const meta = extra.host
        ? '<p class="ep-meta">'+(useCover?eq:"")+'<span class="ep-meta-txt"><a href="'+showHref(ex)+'">'+escapeHtml(ex.name)+'</a> · '+ep.minutes+' мин</span></p>'
        : '<p class="ep-meta">'+(useCover?eq:"")+'<span class="ep-meta-txt">'+ep.minutes+' мин</span></p>';
      const pip = started ? '<div class="progress-pip"><i style="width:42%"></i></div>' : '';
      const hint = (i===0 && extra.upNext) ? '<p class="eyebrow ep-up-hint">Далее через 5 с</p>' : '';
      artEl.innerHTML =
        thumb+
        '<div class="ep-body">'+hint+'<p class="t"><a href="'+href+'">'+escapeHtml(ep.title)+'</a></p>'+meta+'</div>'+
        '<button class="btn-round-play ep-card-play" data-play type="button" aria-label="'+label+'">'+playSvg()+'</button>'+
        '<button class="like" type="button" aria-label="В сохранённые"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M12 19s-7-4.4-7-9a4 4 0 0 1 7-2 4 4 0 0 1 7 2c0 4.6-7 9-7 9z"/></svg></button>'+
        pip;
      frag.appendChild(artEl);
    });
    if(moreBtn && moreBtn.parentElement===table) table.insertBefore(frag, moreBtn);
    else table.appendChild(frag);
    if(moreBtn) moreBtn.hidden = eps.length <= 10;
  }

  function leadOfTopic(t){
    return experts.find(o=>o.rubric===t.slug) || expert("maya");
  }
  function rubricTileHtml(x, opts){
    opts = opts || {};
    const lead = leadOfTopic(x);
    const first = (episodesOfTopic(x) || [])[0];
    const play = first ? playerHref(first, {t:x.slug}) + "&play=1" : topicHref(x);
    const cls = "rubric-tile" + (opts.big ? " big" : "") + (opts.alt ? " alt" : "");
    const title = opts.fullName ? x.name : (opts.short===false ? x.name : (opts.big ? x.name : x.short));
    return '<div class="'+cls+'" style="--accent:'+x.accent+'">'+
      '<a class="rubric-tile-hit" href="'+topicHref(x)+'">'+
        '<img src="'+lead.photo+'" alt="'+escapeHtml(lead.name)+'">'+
        '<b>'+escapeHtml(title)+'</b>'+
      '</a>'+
      '<a class="play-float" href="'+play+'" aria-label="Слушать: '+escapeHtml(x.name)+'">'+playSvg()+'</a>'+
    '</div>';
  }

  function rubricPlaqueHtml(x){
    const lead = leadOfTopic(x);
    const first = (episodesOfTopic(x) || [])[0];
    const play = first ? playerHref(first, {t:x.slug}) + "&play=1" : topicHref(x);
    const accent = x.accent || lead.accent;
    return '<div class="rubric-plaque" style="--accent:'+accent+'">'+
      '<a class="rubric-plaque-hit" href="'+topicHref(x)+'">'+
        '<img class="rubric-plaque-ava" src="'+lead.photo+'" alt="'+escapeHtml(lead.name)+'" width="80" height="80">'+
        '<b>'+escapeHtml(x.name)+'</b>'+
      '</a>'+
      '<a class="play-float" href="'+play+'" aria-label="Слушать: '+escapeHtml(x.name)+'">'+playSvg()+'</a>'+
    '</div>';
  }

  function facesHtml(exs){
    return exs.map(o=>
      '<a href="'+showHref(o)+'" aria-label="Колонка: '+escapeHtml(o.name)+'" style="--accent:'+o.accent+'">'+
      '<img src="'+o.photo+'" alt="'+escapeHtml(o.name)+'"></a>'
    ).join("");
  }

  function initShow(){
    const q = params();
    const ex = expert(q.get("e") || "maya");
    const eps = episodesOf(ex);
    const topic = TOPICS.find(t=>t.slug===ex.rubric) || NEW_TOPIC;
    document.title = ex.category + " — " + ex.name + " — EYRA";
    document.documentElement.style.setProperty("--accent", ex.accent);
    $$(".show-hero-bg, .show-hero, .host").forEach(el=>el.style.setProperty("--accent", ex.accent));
    const crumb = $(".show-crumb");
    if(crumb) crumb.innerHTML = '<a href="hub.html">Подкасты</a> · <a href="'+topicHref(topic)+'">'+escapeHtml(ex.category)+'</a>';
    const art = $(".show-hero .hero-art img");
    if(art){ art.src = ex.photo; art.alt = ex.name; }
    const eye = $(".show-hero .typo-copy .eyebrow");
    if(eye) eye.textContent = "Колонка · " + ex.name;
    const coverTitle = $(".show-hero .typo-copy b");
    if(coverTitle) coverTitle.textContent = ex.category;
    const h1 = $(".show-copy h1");
    if(h1) h1.textContent = ex.category;
    const dek = $(".show-copy .dek");
    if(dek) dek.textContent = ex.dek;
    const host = $(".show-copy .host");
    if(host){
      host.innerHTML = '<span class="host-name">'+escapeHtml(ex.name)+'</span><span class="host-rest"> · '+escapeHtml(ex.role)+' · <a href="'+ex.page+'" rel="noopener">Страница эксперта</a></span>';
    }
    const read = $(".show-actions a.read-quiet, .show-actions a.btn-ghost:not(.like)");
    if(read){ read.href = (eps[0] && eps[0].url) || ex.journal; read.setAttribute("target","_blank"); read.setAttribute("rel","noopener"); }
    if(eps[0]) document.body.dataset.duration = String(eps[0].minutes * 60);
    renderEpTable($(".ep-table"), eps, {});
    fillExpertCard($(".catalog-expert-slot"), ex);
    const rail = $("#other-cols .rail");
    if(rail){
      rail.innerHTML = experts.filter(o=>o.slug!==ex.slug).map(o=>
        '<a class="card-expert" href="'+showHref(o)+'" style="--accent:'+o.accent+'">'+
          '<div class="avatar-wrap"><span class="avatar-photo"><img src="'+o.photo+'" alt="'+escapeHtml(o.name)+'" width="200" height="200"></span></div>'+
          '<b>'+escapeHtml(o.name)+'</b><span>'+escapeHtml(o.roleShort)+'</span></a>'
      ).join("");
    }
  }

  function queueFrom(ep, q){
    if(q.get("m")) return episodesOfMood(moodBy(q.get("m"))).filter(a=>a.slug!==ep.slug);
    if(q.get("t")) return episodesOfTopic(topicBy(q.get("t"))).filter(a=>a.slug!==ep.slug);
    return episodesOf(expert(slugOf(ep))).filter(a=>a.slug!==ep.slug);
  }

  function initPlayer(){
    const q = params();
    let ep = q.get("ep") ? episodeBySlug(q.get("ep")) : null;
    let ex = expert(q.get("e") || (ep ? slugOf(ep) : "maya"));
    const eps = episodesOf(ex);
    if(!ep) ep = eps.find(a=>a.featured) || eps[0];
    if(!ep) return;
    ex = expert(slugOf(ep));
    const topic = TOPICS.find(t=>t.slug===ep.rubric || (t.also||[]).includes(ep.rubric)) || topicBy(ex.rubric);
    const extra = {};
    if(q.get("t")) extra.t = q.get("t");
    if(q.get("m")) extra.m = q.get("m");
    const rest = queueFrom(ep, q);

    document.title = ep.title + " — EYRA";
    document.body.dataset.duration = String((ep.minutes||7)*60);
    $$(".now-art-wrap, .now-art-wrap .typo-cover, .host-line").forEach(el=>el.style.setProperty("--accent", ex.accent));
    const cover = $(".now-art-wrap .typo-cover img") || $(".now-art-wrap img");
    if(cover){ cover.src = ex.photo; cover.alt = ex.name; }
    const eye = $(".now-art-wrap .eyebrow");
    if(eye) eye.textContent = ex.eyebrow;
    const coverB = $(".now-art-wrap .typo-copy b");
    if(coverB) coverB.textContent = ep.title;
    const showLink = $(".now-copy .show-link");
    if(showLink){ showLink.href = showHref(ex); showLink.textContent = ex.category; }
    const h1 = $(".now-copy h1");
    if(h1) h1.textContent = ep.title;
    const host = $(".now-copy .host-line");
    if(host){
      host.style.removeProperty("--accent");
      host.innerHTML = '<span class="host-name"><a href="'+showHref(ex)+'">'+escapeHtml(ex.name)+'</a></span><span class="host-rest"> · '+escapeHtml(ex.role)+' · '+ep.minutes+' мин</span>';
    }
    $$(".now-copy .read-quiet, .now-copy .mode-switch a").forEach(a=>{
      a.href = ep.url;
      a.setAttribute("target","_blank");
      a.setAttribute("rel","noopener");
    });
    const about = $(".now-extra p");
    if(about) about.textContent = ep.excerpt || "";
    const crumb = $(".now-page > .crumb");
    if(crumb) crumb.innerHTML = '<a href="hub.html">Подкасты</a> · <a href="'+topicHref(topic)+'">'+escapeHtml(topic.name)+'</a>';

    const dalee = rest.slice(0,6);
    const daleeMix = new Set(dalee.map(a=>slugOf(a))).size > 1;
    renderEpTable($("#dalee-list"), dalee, Object.assign({}, extra, {host:true, cover:daleeMix, markStarted:false, upNext:true}));

    const escheTitle = $("#esche .h-section");
    if(escheTitle) escheTitle.textContent = "Ещё у " + ex.genitive;
    const escheAll = $("#esche .shelf-tools a");
    if(escheAll) escheAll.href = showHref(ex);
    const taken = new Set(dalee.map(a=>a.slug));
    taken.add(ep.slug);
    const escheEps = eps.filter(a=>!taken.has(a.slug)).slice(0,6);
    const escheList = $("#esche-list, #esche .rail, #esche .ep-table");
    const escheSec = $("#esche");
    if(escheList){
      escheList.classList.add("rail","esche-rail");
      escheList.classList.remove("ep-table","esche-list");
      escheList.innerHTML = escheEps.map(a=>eschePlaqueHtml(a, ex)).join("");
    }
    if(escheSec) escheSec.hidden = !escheEps.length;

    const alike = $("#alike-grid, .alike-grid");
    if(alike){
      const others = articles.filter(a=>a.expert!==ex.name);
      const picked = [];
      for(const a of others){
        if(picked.some(p=>p.expert===a.expert)) continue;
        picked.push(a);
        if(picked.length===4) break;
      }
      for(const a of others){
        if(picked.length===4) break;
        if(!picked.some(p=>p.slug===a.slug)) picked.push(a);
      }
      renderEpTable(alike, picked, {host:true, cover:true, markStarted:false});
    }

    fillExpertCard($(".catalog-expert-slot"), ex);

    const miniCover = $(".mini-player .typo-cover img");
    if(miniCover){ miniCover.src = ex.photo; miniCover.alt = ex.name; }
    const miniTy = $(".mini-player .typo-cover");
    if(miniTy) miniTy.style.setProperty("--accent", ex.accent);
    const miniEye = $(".mini-player .typo-cover .eyebrow");
    if(miniEye) miniEye.textContent = ex.eyebrow;
    const miniCoverB = $(".mini-player .typo-cover b");
    if(miniCoverB) miniCoverB.textContent = ep.title;
    const miniTitle = $(".mini-player .meta b");
    if(miniTitle) miniTitle.textContent = ep.title;
    const miniSub = $(".mini-player .meta span");
    if(miniSub) miniSub.textContent = ex.name + " · " + ex.category;
    $$(".mini-player [data-open-player]").forEach(a=>{
      if(a.tagName==="A") a.href = playerHref(ep, extra);
    });
    const readMini = $(".mini-player .read-quiet, .mini-player .read-link");
    if(readMini){ readMini.href = ep.url; readMini.setAttribute("target","_blank"); readMini.setAttribute("rel","noopener"); }

    window.EYRA_NOW = { expert: ex.slug, episode: ep.slug, href: playerHref(ep, extra) };
  }

  function initTopic(){
    const q = params();
    const t = topicBy(q.get("t") || "dosug");
    const eps = episodesOfTopic(t);
    const exs = [];
    const seen = new Set();
    for(const a of eps){
      const s = slugOf(a);
      if(seen.has(s)) continue;
      seen.add(s); exs.push(expert(s));
    }
    const lead = exs[0] || expert("maya");
    document.title = t.name + " — EYRA";
    const hero = $(".topic-hero");
    if(hero){
      hero.style.setProperty("--accent", t.accent);
      hero.style.setProperty("--button", t.button || "#efe4d2");
      const photos = hero.querySelector(".topic-photos");
      if(photos){
        let html = '<img class="topic-lead" src="'+lead.photo+'" alt="'+escapeHtml(lead.name)+'">';
        if(exs.length>=2){
          html += '<div class="topic-others">'+exs.slice(1,4).map(o=>
            '<a href="'+showHref(o)+'" style="--accent:'+o.accent+'" aria-label="Колонка: '+escapeHtml(o.name)+'"><img src="'+o.photo+'" alt="'+escapeHtml(o.name)+'"></a>'
          ).join("")+'</div>';
        }
        photos.innerHTML = html;
      }
    }
    const crumb = $(".topic-copy .crumb, .topic-hero .crumb");
    if(crumb) crumb.innerHTML = '<a href="hub.html">Подкасты</a> · '+escapeHtml(t.name);
    const eye = $(".topic-copy .eyebrow");
    if(eye) eye.textContent = t.slug==="new" ? "Новое" : "Рубрика";
    const h1 = $(".topic-copy h1");
    if(h1) h1.textContent = t.name;
    const play = $("a.hero-play, [data-listen-queue]", hero || document);
    if(play && eps[0]) play.href = playerHref(eps[0], {t:t.slug}) + "&play=1";
    if(eps[0]) document.body.dataset.duration = String(eps[0].minutes*60);
    const topicMix = new Set(eps.map(a=>slugOf(a))).size > 1;
    renderEpTable($(".ep-table"), eps, {host:true, cover:topicMix, t:t.slug});
    const rail = $("#topic-experts .rail, #topic-experts");
    const expWrap = $("#topic-experts .rail") || $("#topic-experts-rail");
    if(expWrap){
      expWrap.innerHTML = exs.map(o=>
        '<a class="card-expert" href="'+showHref(o)+'" style="--accent:'+o.accent+'">'+
          '<div class="avatar-wrap"><span class="avatar-photo"><img src="'+o.photo+'" alt="'+escapeHtml(o.name)+'" width="200" height="200"></span></div>'+
          '<b>'+escapeHtml(o.name)+'</b><span>'+escapeHtml(o.roleShort)+'</span></a>'
      ).join("");
    }
    const others = $("#other-topics");
    if(others){
      const list = t.slug==="new" ? TOPICS : TOPICS.filter(x=>x.slug!==t.slug);
      others.classList.remove("is-ten");
      others.innerHTML = list.slice(0,8).map(x=>
        '<a class="topic-tile" href="'+topicHref(x)+'" style="--accent:'+x.accent+';--plaque:'+x.button+';background:'+x.button+'"><b>'+escapeHtml(x.short)+'</b></a>'
      ).join("");
    }
  }

  function initMood(){
    const q = params();
    const m = moodBy(q.get("m") || "vecher");
    const eps = episodesOfMood(m);
    document.title = m.name + " — EYRA";
    const exs = [];
    const seen = new Set();
    for(const a of eps){
      const s = slugOf(a);
      if(seen.has(s)) continue;
      seen.add(s); exs.push(expert(s));
    }
    const hero = $(".mood-hero");
    if(hero){
      hero.style.setProperty("--mood-tint", m.tint);
      hero.style.setProperty("--accent", m.accent);
      hero.setAttribute("data-mood", m.slug);
      const cluster = hero.querySelector(".mood-cluster");
      if(cluster){
        const faces = (exs.length ? exs : [expert("maya")]).slice(0,4);
        cluster.innerHTML = faces.map(o=>
          '<a href="'+showHref(o)+'" style="--accent:'+o.accent+'" aria-label="Колонка: '+escapeHtml(o.name)+'"><img src="'+o.photo+'" alt="'+escapeHtml(o.name)+'"></a>'
        ).join("");
      }
    }
    const crumb = $(".mood-hero .crumb");
    if(crumb) crumb.innerHTML = '<a href="hub.html">Подкасты</a> · '+escapeHtml(m.name);
    const eye = $(".mood-hero .eyebrow");
    if(eye) eye.textContent = "Настроение";
    const h1 = $(".mood-hero h1");
    if(h1) h1.textContent = m.name;
    const play = $(".mood-hero a.hero-play, .mood-hero [data-listen-queue]");
    if(play && eps[0]) play.href = playerHref(eps[0], {m:m.slug}) + "&play=1";
    if(eps[0]) document.body.dataset.duration = String(eps[0].minutes*60);
    renderEpTable($(".mood-eps"), eps, {host:true, cover:true, m:m.slug});
    const chips = $("#other-moods");
    if(chips){
      chips.innerHTML = MOODS.map(x=>
        '<a class="mood-plaque'+(x.slug===m.slug?' is-on':'')+'" href="'+moodHref(x)+'" style="--plaque:'+x.tint+';background:'+x.tint+'"><b>'+escapeHtml(x.name)+'</b></a>'
      ).join("");
    }
  }

  function initExpertsPage(){
    document.title = "Эксперты — подкаст EYRA";
    const grid = $(".experts-page-grid");
    if(!grid) return;
    grid.innerHTML = experts.map(o=>
      '<a class="card-expert" href="'+showHref(o)+'" style="--accent:'+o.accent+'">'+
        '<div class="avatar-wrap"><span class="avatar-photo"><img src="'+o.photo+'" alt="'+escapeHtml(o.name)+'" width="200" height="200"></span></div>'+
        '<b>'+escapeHtml(o.name)+'</b><span>'+escapeHtml(o.roleShort)+'</span></a>'
    ).join("");
  }

  async function boot(){
    try{
      const [e, a] = await Promise.all([
        fetch("experts.json").then(r=>r.json()),
        fetch("articles.json").then(r=>r.json())
      ]);
      experts = e; articles = a;
    }catch(err){ console.warn("catalog load failed", err); return; }
    window.EYRA = { expert, episodesOf, episodeBySlug, showHref, playerHref, slugOf, topicBy, moodBy, experts, articles };
    if($(".show-hero")) initShow();
    if($(".now-page")) initPlayer();
    if($(".topic-hero")) initTopic();
    if($(".mood-hero")) initMood();
    if($(".experts-page-grid")) initExpertsPage();
  }
  boot();
})();
