/* Copied from eyra.ink journal menu + shared-footer reveal, with Подкаст in the nav only. */
(() => {
  const journalMenu = document.querySelector('#journal-menu');
  const journalMenuToggle = document.querySelector('.journal-menu-toggle');
  if (journalMenu && journalMenuToggle) {
    document.addEventListener('pointerdown', () => { document.documentElement.dataset.input = 'pointer'; }, {capture:true,passive:true});
    document.addEventListener('keydown', event => { if (!event.altKey && !event.ctrlKey && !event.metaKey) document.documentElement.dataset.input = 'keyboard'; }, true);
    let previousOverflow = '';
    journalMenuToggle.addEventListener('click', () => {
      previousOverflow = document.body.style.overflow;
      journalMenu.showModal();
      document.body.style.overflow = 'hidden';
      journalMenuToggle.setAttribute('aria-expanded', 'true');
    });
    journalMenu.querySelector('.journal-menu-close').addEventListener('click', () => journalMenu.close());
    journalMenu.addEventListener('click', event => {
      if (event.target !== journalMenu) return;
      const rect = journalMenu.getBoundingClientRect();
      if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) journalMenu.close();
    });
    journalMenu.addEventListener('close', () => {
      document.body.style.overflow = previousOverflow;
      journalMenuToggle.setAttribute('aria-expanded', 'false');
      if (matchMedia('(max-width:900px)').matches) journalMenuToggle.focus({preventScroll:true});
    });
    journalMenu.querySelectorAll('a').forEach(link => link.addEventListener('click', () => journalMenu.close()));
    matchMedia('(max-width:900px)').addEventListener('change', event => { if (!event.matches && journalMenu.open) journalMenu.close(); });
    window.addEventListener('pageshow', () => { if (journalMenu.open) journalMenu.close(); });
  }
})();

(() => {
  const footer=document.querySelector('.footer');
  const surface=document.querySelector('body>.eyra-content-surface,body>main');
  if(!footer||!surface)return;
  const root=document.documentElement;
  const motion=matchMedia('(prefers-reduced-motion:reduce)');
  const desktop=matchMedia('(min-width:761px)');
  let frame=0,lastCover='';
  // Clip the covered part too: the sticky footer must not paint through main
  // content tiles while the browser rasterizes a fast scroll.
  function updateCover(){
    frame=0;
    if(!root.classList.contains('footer-reveal'))return;
    const box=footer.getBoundingClientRect();
    const covered=Math.min(box.height,Math.max(0,surface.getBoundingClientRect().bottom-box.top));
    const value=covered>=box.height-.5?'100%':`${Math.ceil(covered)}px`;
    if(value!==lastCover){footer.style.setProperty('--footer-cover',value);lastCover=value;}
  }
  function scheduleCover(){if(!frame)frame=requestAnimationFrame(updateCover);}
  function fitFooterReveal(){
    // Mobile browser chrome resizes visualViewport during scrolling. Avoid
    // switching positioning mode mid-gesture; mobile uses ordinary flow.
    const playerPage=root.classList.contains('player-page');
    const tooShort=playerPage&&surface.scrollHeight<root.clientHeight-48;
    const enabled=desktop.matches&&!motion.matches&&footer.offsetHeight+48<=root.clientHeight&&!tooShort;
    root.classList.toggle('footer-reveal',enabled);
    if(enabled)updateCover();
    else{footer.style.removeProperty('--footer-cover');lastCover='';}
  }
  fitFooterReveal();
  const observer=new ResizeObserver(fitFooterReveal);
  observer.observe(footer);
  observer.observe(surface);
  window.addEventListener('scroll',scheduleCover,{passive:true});
  window.addEventListener('resize',fitFooterReveal,{passive:true});
  window.addEventListener('pageshow',fitFooterReveal);
  motion.addEventListener('change',fitFooterReveal);
  desktop.addEventListener('change',fitFooterReveal);
  document.fonts.ready.then(fitFooterReveal);
  footer.addEventListener('focusin',event=>{
    if(event.target.matches(':focus-visible')&&root.classList.contains('footer-reveal')&&surface.getBoundingClientRect().bottom>footer.getBoundingClientRect().top+1){
      window.scrollTo({top:root.scrollHeight-innerHeight,behavior:'instant'});
      updateCover();
    }
  });
})();
