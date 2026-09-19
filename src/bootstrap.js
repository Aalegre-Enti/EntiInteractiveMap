import { loadConfig } from './config.js';

const retry = document.getElementById('retry-button');
async function start() {
  retry.hidden = true;
  document.getElementById('map-viewport').setAttribute('aria-busy', 'true');
  for (const id of ['zoom-in', 'zoom-out', 'reset-view']) document.getElementById(id).disabled = true;
  document.querySelector('.loading-spinner').hidden = false;
  document.getElementById('map-message-text').textContent = 'S’està carregant el mapa…';
  try {
    const config = await loadConfig(new URL('./config.json', document.baseURI));
    const { startApp } = await import('./app.js');
    startApp(config);
    retry.removeEventListener('click', start);
  } catch (error) {
    console.error(error);
    document.querySelector('.loading-spinner').hidden = true;
    document.getElementById('map-message-text').textContent = 'El mapa no està disponible. Torna-ho a provar.';
    document.getElementById('map-viewport').setAttribute('aria-busy', 'false');
    retry.hidden = false;
  }
}
retry.addEventListener('click', start);
start();
