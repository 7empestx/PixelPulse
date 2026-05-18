#include "WebDashboard.h"
#include <WiFi.h>

// ── Dashboard HTML (stored in flash, not RAM) ──
static const char DASHBOARD_HTML[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>PIXELPULSE // DASHBOARD</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0a0a0a;color:#00ff41;font-family:'Courier New','Lucida Console',monospace;font-size:14px;line-height:1.6;padding:16px;max-width:800px;margin:0 auto}
h1{font-size:1.3em;letter-spacing:2px}
h2{font-size:1em;border-bottom:1px solid #003a0f;padding-bottom:4px;margin-bottom:12px}
h3{font-size:.85em;color:#00ccff;margin-bottom:4px}
header{border-bottom:2px solid #00ff41;padding-bottom:8px;margin-bottom:16px}
#status-bar{display:flex;gap:14px;font-size:.75em;color:#00aa30;margin-top:4px;flex-wrap:wrap}
.panel{background:#111;border:1px solid #003a0f;padding:14px;margin-bottom:14px;border-radius:2px}
.mode-display{font-size:1.2em;margin-bottom:10px;display:flex;justify-content:space-between;align-items:center}
.mode-buttons{display:flex;gap:6px;margin-bottom:10px}
.mode-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:5px}
button{background:#1a1a1a;color:#00ff41;border:1px solid #00ff41;padding:7px 10px;font-family:inherit;font-size:.8em;cursor:pointer;transition:all .15s}
button:hover{background:#00ff41;color:#0a0a0a}
button.active{background:#00ff41;color:#0a0a0a}
button.paused{border-color:#ffaa00;color:#ffaa00}
button.paused:hover{background:#ffaa00;color:#0a0a0a}
.slider-row{display:flex;align-items:center;gap:10px}
input[type=range]{-webkit-appearance:none;flex:1;height:4px;background:#003a0f;outline:none}
input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:16px;height:16px;background:#00ff41;border-radius:2px;cursor:pointer}
input[type=text]{background:#1a1a1a;border:1px solid #003a0f;color:#00ff41;padding:5px 8px;font-family:inherit;font-size:.85em;width:100%;margin-top:3px;margin-bottom:6px}
input[type=text]:focus{border-color:#00ff41;outline:none}
label{display:block;font-size:.75em;color:#00aa30}
.data-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.data-card{background:#0d0d0d;border:1px solid #003a0f;padding:10px}
footer{margin-top:16px;font-size:.7em;color:#003a0f;border-top:1px solid #003a0f;padding-top:6px}
#config-status{color:#00ccff;margin-left:10px;font-size:.85em}
@media(max-width:600px){.mode-grid{grid-template-columns:repeat(2,1fr)}.data-grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<header>
<h1>&gt; PIXELPULSE_</h1>
<div id="status-bar">
<span id="ip">IP:--</span>
<span id="uptime">UP:--</span>
<span id="heap">HEAP:--</span>
<span id="rssi">RSSI:--</span>
</div>
</header>

<section class="panel">
<h2>&gt; MODE_CONTROL</h2>
<div class="mode-display">
<span id="current-mode">LOADING...</span>
<span id="mode-index">[0/0]</span>
</div>
<div class="mode-buttons">
<button onclick="prevMode()">&#9664; PREV</button>
<button onclick="togglePause()" id="pause-btn">&#10074;&#10074; PAUSE</button>
<button onclick="nextMode()">NEXT &#9654;</button>
</div>
<div class="mode-grid" id="mode-grid"></div>
</section>

<section class="panel">
<h2>&gt; BRIGHTNESS</h2>
<div class="slider-row">
<input type="range" id="brightness-slider" min="1" max="255" value="50">
<span id="brightness-value">50</span>
</div>
</section>

<section class="panel">
<h2>&gt; LIVE_DATA</h2>
<div class="data-grid">
<div class="data-card"><h3>WEATHER</h3><div id="weather-info">--</div></div>
<div class="data-card"><h3>CRYPTO</h3><div id="crypto-info">--</div></div>
<div class="data-card"><h3>FLIGHTS</h3><div id="flight-info">--</div></div>
</div>
</section>

<section class="panel">
<h2>&gt; CONFIG</h2>
<form id="config-form" onsubmit="saveConfig(event)">
<label>CITY<input type="text" id="cfg-city"></label>
<label>CRYPTO<input type="text" id="cfg-crypto"></label>
<label>ICAO<input type="text" id="cfg-icao"></label>
<label>NAME<input type="text" id="cfg-name"></label>
<label>OWM_KEY<input type="text" id="cfg-owm"></label>
<button type="submit">SAVE_CONFIG</button><span id="config-status"></span>
</form>
</section>

<footer>&gt; SYSTEM READY // <span id="footer-time"></span></footer>

<script>
async function api(p,o={}){const r=await fetch(p,{headers:{'Content-Type':'application/json'},...o});return r.json()}

function fmt(s){const h=Math.floor(s/3600),m=Math.floor((s%3600)/60),sec=s%60;return h+'h '+m+'m '+sec+'s'}

async function refreshStatus(){
try{
const s=await api('/api/status');
document.getElementById('current-mode').textContent=s.mode;
document.getElementById('mode-index').textContent='['+(s.modeIndex+1)+'/'+s.modeCount+']';
document.getElementById('ip').textContent='IP:'+s.ip;
document.getElementById('uptime').textContent='UP:'+fmt(s.uptime);
document.getElementById('heap').textContent='HEAP:'+Math.round(s.freeHeap/1024)+'KB';
document.getElementById('rssi').textContent='RSSI:'+s.wifiRssi+'dBm';
const btn=document.getElementById('pause-btn');
btn.textContent=s.paused?'\u25B6 RESUME':'\u23F8 PAUSE';
btn.className=s.paused?'paused':'';
document.querySelectorAll('.mode-btn').forEach((b,i)=>{b.className='mode-btn'+(i===s.modeIndex?' active':'')});
document.getElementById('brightness-slider').value=s.brightness;
document.getElementById('brightness-value').textContent=s.brightness;
}catch(e){}}

async function refreshData(){
try{
const d=await api('/api/data');
if(d.weather&&d.weather.valid)
document.getElementById('weather-info').innerHTML=d.weather.tempF.toFixed(1)+'&deg;F<br>'+d.weather.condition;
if(d.crypto&&d.crypto.valid){
const a=d.crypto.change24h>=0?'\u25B2':'\u25BC';
const c=d.crypto.change24h>=0?'#00ff41':'#ff0000';
document.getElementById('crypto-info').innerHTML=d.crypto.symbol+': $'+d.crypto.price.toLocaleString()+'<br><span style="color:'+c+'">'+a+' '+d.crypto.change24h.toFixed(2)+'%</span>';
}
if(d.flights&&d.flights.valid&&d.flights.entries.length>0)
document.getElementById('flight-info').innerHTML=d.flights.entries.map(f=>f.callsign).join('<br>');
else document.getElementById('flight-info').textContent='NO DATA';
}catch(e){}}

async function loadModes(){
const m=await api('/api/modes');
const g=document.getElementById('mode-grid');
g.innerHTML='';
m.modes.forEach((n,i)=>{const b=document.createElement('button');b.className='mode-btn'+(i===m.current?' active':'');b.textContent=n;b.onclick=()=>setMode(i);g.appendChild(b)});
}

async function setMode(i){await api('/api/mode',{method:'POST',body:JSON.stringify({index:i})});refreshStatus()}
async function nextMode(){await api('/api/mode/next',{method:'POST'});refreshStatus()}
async function prevMode(){await api('/api/mode/prev',{method:'POST'});refreshStatus()}
async function togglePause(){const s=await api('/api/status');await api('/api/mode/pause',{method:'POST',body:JSON.stringify({paused:!s.paused})});refreshStatus()}

let bto;
document.getElementById('brightness-slider').addEventListener('input',function(){
document.getElementById('brightness-value').textContent=this.value;
clearTimeout(bto);
bto=setTimeout(()=>{api('/api/brightness',{method:'POST',body:JSON.stringify({brightness:parseInt(this.value)})})},150);
});

async function loadConfig(){
const c=await api('/api/config');
document.getElementById('cfg-city').value=c.city||'';
document.getElementById('cfg-crypto').value=c.crypto||'';
document.getElementById('cfg-icao').value=c.icao||'';
document.getElementById('cfg-name').value=c.customerName||'';
document.getElementById('cfg-owm').value=c.owmApiKey||'';
}

async function saveConfig(e){
e.preventDefault();
const b={city:document.getElementById('cfg-city').value,crypto:document.getElementById('cfg-crypto').value,icao:document.getElementById('cfg-icao').value,customerName:document.getElementById('cfg-name').value,owmApiKey:document.getElementById('cfg-owm').value};
const r=await api('/api/config',{method:'POST',body:JSON.stringify(b)});
const st=document.getElementById('config-status');
st.textContent=r.ok?'SAVED':'ERROR';
setTimeout(()=>st.textContent='',3000);
}

loadModes();loadConfig();refreshStatus();refreshData();
setInterval(refreshStatus,2000);
setInterval(refreshData,10000);
setInterval(()=>{document.getElementById('footer-time').textContent=new Date().toLocaleTimeString()},1000);
</script>
</body>
</html>
)rawliteral";

// ── WebDashboard implementation ──

void WebDashboard::begin(ModeManager* modeManager, ApiPoller* apiPoller,
                         ConfigManager* configManager, Display* display) {
    _modeManager = modeManager;
    _apiPoller = apiPoller;
    _configManager = configManager;
    _display = display;
    _startTime = millis();

    _server.on("/", HTTP_GET, [this]() { handleRoot(); });
    _server.on("/api/status", HTTP_GET, [this]() { handleGetStatus(); });
    _server.on("/api/modes", HTTP_GET, [this]() { handleGetModes(); });
    _server.on("/api/mode", HTTP_POST, [this]() { handleSetMode(); });
    _server.on("/api/mode/next", HTTP_POST, [this]() { handleNextMode(); });
    _server.on("/api/mode/prev", HTTP_POST, [this]() { handlePrevMode(); });
    _server.on("/api/mode/pause", HTTP_POST, [this]() { handleSetPaused(); });
    _server.on("/api/brightness", HTTP_POST, [this]() { handleSetBrightness(); });
    _server.on("/api/config", HTTP_GET, [this]() { handleGetConfig(); });
    _server.on("/api/config", HTTP_POST, [this]() { handleSetConfig(); });
    _server.on("/api/data", HTTP_GET, [this]() { handleGetData(); });
    _server.onNotFound([this]() { handleNotFound(); });

    _server.begin();
    Serial.printf("[WEB] Dashboard: http://%s/\n", WiFi.localIP().toString().c_str());
}

void WebDashboard::update() {
    _server.handleClient();
}

// ── Route handlers ──

void WebDashboard::handleRoot() {
    _server.send_P(200, "text/html", DASHBOARD_HTML);
}

void WebDashboard::handleGetStatus() {
    JsonDocument doc;
    doc["mode"] = _modeManager->getCurrentModeName();
    doc["modeIndex"] = _modeManager->getCurrentModeIndex();
    doc["modeCount"] = _modeManager->getModeCount();
    doc["paused"] = _modeManager->isPaused();
    doc["brightness"] = _brightness;
    doc["ip"] = WiFi.localIP().toString();
    doc["uptime"] = (millis() - _startTime) / 1000;
    doc["freeHeap"] = ESP.getFreeHeap();
    doc["wifiRssi"] = WiFi.RSSI();

    String output;
    serializeJson(doc, output);
    _server.send(200, "application/json", output);
}

void WebDashboard::handleGetModes() {
    JsonDocument doc;
    JsonArray modes = doc["modes"].to<JsonArray>();
    for (int i = 0; i < _modeManager->getModeCount(); i++) {
        modes.add(_modeManager->getModeName(i));
    }
    doc["current"] = _modeManager->getCurrentModeIndex();
    doc["paused"] = _modeManager->isPaused();

    String output;
    serializeJson(doc, output);
    _server.send(200, "application/json", output);
}

void WebDashboard::handleSetMode() {
    JsonDocument doc;
    if (deserializeJson(doc, _server.arg("plain"))) {
        _server.send(400, "application/json", "{\"error\":\"invalid JSON\"}");
        return;
    }
    int index = doc["index"] | -1;
    if (index >= 0 && index < _modeManager->getModeCount()) {
        _modeManager->setMode(index);
        String output;
        JsonDocument resp;
        resp["ok"] = true;
        resp["mode"] = _modeManager->getModeName(index);
        serializeJson(resp, output);
        _server.send(200, "application/json", output);
    } else {
        _server.send(400, "application/json", "{\"error\":\"invalid index\"}");
    }
}

void WebDashboard::handleNextMode() {
    _modeManager->nextMode();
    JsonDocument resp;
    resp["ok"] = true;
    resp["mode"] = _modeManager->getCurrentModeName();
    String output;
    serializeJson(resp, output);
    _server.send(200, "application/json", output);
}

void WebDashboard::handlePrevMode() {
    _modeManager->prevMode();
    JsonDocument resp;
    resp["ok"] = true;
    resp["mode"] = _modeManager->getCurrentModeName();
    String output;
    serializeJson(resp, output);
    _server.send(200, "application/json", output);
}

void WebDashboard::handleSetPaused() {
    JsonDocument doc;
    if (deserializeJson(doc, _server.arg("plain"))) {
        _server.send(400, "application/json", "{\"error\":\"invalid JSON\"}");
        return;
    }
    bool paused = doc["paused"] | false;
    _modeManager->setPaused(paused);

    JsonDocument resp;
    resp["ok"] = true;
    resp["paused"] = paused;
    String output;
    serializeJson(resp, output);
    _server.send(200, "application/json", output);
}

void WebDashboard::handleSetBrightness() {
    JsonDocument doc;
    if (deserializeJson(doc, _server.arg("plain"))) {
        _server.send(400, "application/json", "{\"error\":\"invalid JSON\"}");
        return;
    }
    int val = doc["brightness"] | -1;
    if (val >= 1 && val <= 255) {
        _brightness = (uint8_t)val;
        // Access underlying DMA panel for brightness control
        if (_display && _display->dma()) {
            _display->dma()->setBrightness8(_brightness);
        }
        JsonDocument resp;
        resp["ok"] = true;
        resp["brightness"] = _brightness;
        String output;
        serializeJson(resp, output);
        _server.send(200, "application/json", output);
    } else {
        _server.send(400, "application/json", "{\"error\":\"brightness must be 1-255\"}");
    }
}

void WebDashboard::handleGetConfig() {
    PixelPulseConfig cfg = _configManager->getConfig();

    // Mask API key for security
    String maskedKey = cfg.owmApiKey;
    if (maskedKey.length() > 6) {
        maskedKey = maskedKey.substring(0, 4) + "****" + maskedKey.substring(maskedKey.length() - 2);
    }

    JsonDocument doc;
    doc["city"] = cfg.city;
    doc["crypto"] = cfg.crypto;
    doc["icao"] = cfg.icao;
    doc["customerName"] = cfg.customerName;
    doc["owmApiKey"] = maskedKey;

    String output;
    serializeJson(doc, output);
    _server.send(200, "application/json", output);
}

void WebDashboard::handleSetConfig() {
    JsonDocument doc;
    if (deserializeJson(doc, _server.arg("plain"))) {
        _server.send(400, "application/json", "{\"error\":\"invalid JSON\"}");
        return;
    }

    PixelPulseConfig cfg = _configManager->getConfig();

    if (doc["city"].is<const char*>())         cfg.city = doc["city"].as<String>();
    if (doc["crypto"].is<const char*>())       cfg.crypto = doc["crypto"].as<String>();
    if (doc["icao"].is<const char*>())         cfg.icao = doc["icao"].as<String>();
    if (doc["customerName"].is<const char*>()) cfg.customerName = doc["customerName"].as<String>();

    // Only update API key if it doesn't look like the masked version
    if (doc["owmApiKey"].is<const char*>()) {
        String newKey = doc["owmApiKey"].as<String>();
        if (newKey.length() > 0 && newKey.indexOf("****") < 0) {
            cfg.owmApiKey = newKey;
        }
    }

    _configManager->saveConfig(cfg);

    // Re-initialize API poller with new config
    _apiPoller->begin(cfg);

    _server.send(200, "application/json", "{\"ok\":true}");
}

void WebDashboard::handleGetData() {
    JsonDocument doc;

    WeatherData w = _apiPoller->getWeather();
    JsonObject weather = doc["weather"].to<JsonObject>();
    weather["tempF"] = w.tempF;
    weather["tempC"] = w.tempC;
    weather["condition"] = w.condition;
    weather["valid"] = w.valid;

    CryptoData c = _apiPoller->getCrypto();
    JsonObject crypto = doc["crypto"].to<JsonObject>();
    crypto["price"] = c.price;
    crypto["change24h"] = c.change24h;
    crypto["symbol"] = c.symbol;
    crypto["valid"] = c.valid;

    FlightData f = _apiPoller->getFlights();
    JsonObject flights = doc["flights"].to<JsonObject>();
    JsonArray entries = flights["entries"].to<JsonArray>();
    for (const auto& e : f.flights) {
        JsonObject entry = entries.add<JsonObject>();
        entry["callsign"] = e.callsign;
        entry["origin"] = e.origin;
    }
    flights["valid"] = f.valid;

    String output;
    serializeJson(doc, output);
    _server.send(200, "application/json", output);
}

void WebDashboard::handleNotFound() {
    _server.send(404, "application/json", "{\"error\":\"not found\"}");
}
