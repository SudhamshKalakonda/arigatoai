(function() {
  const API_URL = 'http://localhost:8000/api/ask';
  const WIDGET_KEY = new URLSearchParams(document.currentScript.src.split('?')[1]).get('key') || 'arigato';

  const style = document.createElement('style');
  style.textContent = `
    #aai-btn {
      position: fixed; bottom: 24px; right: 24px;
      width: 56px; height: 56px; border-radius: 50%;
      background: #00BFA5; border: none; cursor: pointer;
      z-index: 99999; box-shadow: 0 4px 16px rgba(0,191,165,0.5);
      display: flex; align-items: center; justify-content: center;
      transition: background 0.2s, transform 0.2s;
    }
    #aai-btn:hover { background: #00897B; transform: scale(1.05); }
    #aai-box {
      position: fixed; bottom: 92px; right: 24px;
      width: 370px; height: 530px;
      background: white; border-radius: 16px;
      box-shadow: 0 8px 40px rgba(0,0,0,0.18);
      display: none; flex-direction: column;
      z-index: 99999; font-family: 'Segoe UI', sans-serif;
      overflow: hidden;
    }
    #aai-box.open { display: flex; }
    #aai-header {
      background: #00BFA5; color: white;
      padding: 14px 16px; flex-shrink: 0;
      display: flex; justify-content: space-between; align-items: center;
    }
    #aai-header .title { font-size: 15px; font-weight: 700; }
    #aai-header .sub { font-size: 11px; opacity: 0.85; margin-top: 2px; }
    #aai-close {
      background: none; border: none; color: white;
      font-size: 18px; cursor: pointer; opacity: 0.8; padding: 4px;
    }
    #aai-close:hover { opacity: 1; }
    #aai-msgs {
      flex: 1; overflow-y: auto; padding: 16px;
      display: flex; flex-direction: column; gap: 10px;
      background: #f7fdfc;
    }
    .aai-ai {
      max-width: 94%; padding: 12px 14px;
      background: white; color: #1a1a1a;
      border-radius: 12px; border-bottom-left-radius: 4px;
      font-size: 13.5px; line-height: 1.6; align-self: flex-start;
      box-shadow: 0 1px 4px rgba(0,0,0,0.07);
      border-left: 3px solid #00BFA5;
    }
    .aai-user {
      max-width: 80%; padding: 10px 14px;
      background: #00BFA5; color: white;
      border-radius: 12px; border-bottom-right-radius: 4px;
      font-size: 13.5px; line-height: 1.5; align-self: flex-end;
    }
    .aai-ai ol { padding-left: 20px; margin: 8px 0 4px; }
    .aai-ai ul { padding-left: 20px; margin: 8px 0 4px; }
    .aai-ai li { margin-bottom: 7px; line-height: 1.65; }
    .aai-ai p { margin: 0 0 7px; }
    .aai-ai p:last-child { margin-bottom: 0; }
    .aai-ai strong { color: #00897B; font-weight: 600; }
    .aai-src {
      font-size: 11px; color: #00897B; margin-top: 8px;
      padding-top: 8px; border-top: 1px solid #e0faf5;
    }
    .aai-typing {
      display: flex; gap: 5px; padding: 12px 14px;
      background: white; border-radius: 12px;
      border-bottom-left-radius: 4px; align-self: flex-start;
      border-left: 3px solid #00BFA5;
      box-shadow: 0 1px 4px rgba(0,0,0,0.07);
    }
    .aai-typing span {
      width: 7px; height: 7px; background: #00BFA5;
      border-radius: 50%; animation: aai-bounce 1.2s infinite;
    }
    .aai-typing span:nth-child(2) { animation-delay: 0.2s; }
    .aai-typing span:nth-child(3) { animation-delay: 0.4s; }
    @keyframes aai-bounce {
      0%,60%,100% { transform: translateY(0); }
      30% { transform: translateY(-5px); }
    }
    #aai-input-row {
      padding: 12px; border-top: 1px solid #e8f8f5;
      display: flex; gap: 8px; background: white; flex-shrink: 0;
    }
    #aai-input {
      flex: 1; padding: 10px 14px;
      border: 1.5px solid #c8f0ea; border-radius: 24px;
      font-size: 13.5px; outline: none; font-family: inherit;
    }
    #aai-input:focus { border-color: #00BFA5; }
    #aai-send {
      width: 38px; height: 38px; border-radius: 50%;
      background: #00BFA5; border: none; cursor: pointer;
      display: flex; align-items: center; justify-content: center;
      flex-shrink: 0; transition: background 0.2s;
    }
    #aai-send:hover { background: #00897B; }
    #aai-brand {
      text-align: center; font-size: 10px; color: #00897B;
      padding: 5px; background: white; flex-shrink: 0;
    }
  `;
  document.head.appendChild(style);

  document.body.insertAdjacentHTML('beforeend', `
    <button id="aai-btn" title="Ask a tax question">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
      </svg>
    </button>
    <div id="aai-box">
      <div id="aai-header">
        <div>
          <div class="title">ArigatoAI Assistant</div>
          <div class="sub">Ask any tax or compliance question</div>
        </div>
        <button id="aai-close">&#x2715;</button>
      </div>
      <div id="aai-msgs">
        <div class="aai-ai">Hi! I am ArigatoAI. Ask me anything about income tax, GST, EPF, or TDS.</div>
      </div>
      <div id="aai-input-row">
        <input id="aai-input" type="text" placeholder="Type your questions here..."/>
        <button id="aai-send">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="22" y1="2" x2="11" y2="13"/>
            <polygon points="22 2 15 22 11 13 2 9 22 2"/>
          </svg>
        </button>
      </div>
      <div id="aai-brand">Powered by ArigatoAI</div>
    </div>
  `);

  const box = document.getElementById('aai-box');
  const msgs = document.getElementById('aai-msgs');
  const input = document.getElementById('aai-input');

  document.getElementById('aai-btn').onclick = () => box.classList.toggle('open');
  document.getElementById('aai-close').onclick = () => box.classList.remove('open');

  function format(text) {
    let t = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>');

    t = t.replace(/\s+(\d+)\.\s+/g, '\n$1. ');

    const lines = t.split('\n');
    let html = '', inOl = false, inUl = false;

    for (let line of lines) {
      line = line.trim();
      if (!line) continue;
      const ol = line.match(/^(\d+)\.\s+(.+)/);
      const ul = line.match(/^[-•]\s+(.+)/);
      if (ol) {
        if (!inOl) { if (inUl) { html += '</ul>'; inUl = false; } html += '<ol>'; inOl = true; }
        html += '<li>' + ol[2] + '</li>';
      } else if (ul) {
        if (!inUl) { if (inOl) { html += '</ol>'; inOl = false; } html += '<ul>'; inUl = true; }
        html += '<li>' + ul[1] + '</li>';
      } else {
        if (inOl) { html += '</ol>'; inOl = false; }
        if (inUl) { html += '</ul>'; inUl = false; }
        html += '<p>' + line + '</p>';
      }
    }
    if (inOl) html += '</ol>';
    if (inUl) html += '</ul>';
    return html;
  }

  function addMsg(text, type, sources) {
    const div = document.createElement('div');
    div.className = type === 'user' ? 'aai-user' : 'aai-ai';
    if (type === 'ai') {
      div.innerHTML = format(text);
      if (sources && sources.length) {
        const s = document.createElement('div');
        s.className = 'aai-src';
        try { s.textContent = 'Source: ' + sources.map(function(u) { return new URL(u).hostname; }).join(', '); }
        catch(e) { s.textContent = 'Source: ' + sources.join(', '); }
        div.appendChild(s);
      }
    } else {
      div.textContent = text;
    }
    msgs.appendChild(div);
    msgs.scrollTop = msgs.scrollHeight;
  }

  function showTyping() {
    const d = document.createElement('div');
    d.className = 'aai-typing';
    d.id = 'aai-typing';
    d.innerHTML = '<span></span><span></span><span></span>';
    msgs.appendChild(d);
    msgs.scrollTop = msgs.scrollHeight;
  }

  function hideTyping() {
    const t = document.getElementById('aai-typing');
    if (t) t.remove();
  }

  async function ask() {
    const q = input.value.trim();
    if (!q) return;
    input.value = '';
    addMsg(q, 'user');
    showTyping();
    try {
      const res = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: q, firm_id: WIDGET_KEY })
      });
      const data = await res.json();
      hideTyping();
      addMsg(data.answer, 'ai', data.sources);
    } catch(e) {
      hideTyping();
      addMsg('Sorry, could not connect. Please try again.', 'ai');
    }
  }

  document.getElementById('aai-send').onclick = ask;
  input.onkeydown = function(e) { if (e.key === 'Enter') ask(); };

})();