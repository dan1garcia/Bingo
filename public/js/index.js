// public/js/index.js (migrado desde root/index.js)
console.log('Public JS cargado');

// Modal Create Game logic
document.addEventListener('DOMContentLoaded', function () {
	const openBtn = document.getElementById('createCard');
	const overlay = document.getElementById('createModalOverlay');
	const closeBtn = document.getElementById('closeModalBtn');
	const cancelBtn = document.getElementById('cancelCreate');
	const form = document.getElementById('createGameForm');
	const gameName = document.getElementById('gameName');
	const playersCount = document.getElementById('playersCount');

	function openModal() {
		if (!overlay) return;
		overlay.classList.add('active');
		overlay.setAttribute('aria-hidden', 'false');
		// focus first input
		setTimeout(() => gameName && gameName.focus(), 40);
		document.addEventListener('keydown', handleKeydown);
	}

	function closeModal() {
		if (!overlay) return;
		overlay.classList.remove('active');
		overlay.setAttribute('aria-hidden', 'true');
		document.removeEventListener('keydown', handleKeydown);
	}

	function handleKeydown(e) {
		if (e.key === 'Escape') closeModal();
		if (e.key === 'Enter' && document.activeElement && document.activeElement.tagName !== 'INPUT') {
			// prevent accidental Enter from closing when outside inputs
		}
	}

	if (openBtn) {
		openBtn.addEventListener('click', openModal);
		openBtn.addEventListener('keypress', function (e) { if (e.key === 'Enter' || e.key === ' ') openModal(); });
	}

	if (overlay) {
		overlay.addEventListener('click', function (e) {
			if (e.target === overlay) closeModal();
		});
	}

	if (closeBtn) closeBtn.addEventListener('click', closeModal);
	if (cancelBtn) cancelBtn.addEventListener('click', closeModal);

	if (form) {
		form.addEventListener('submit', function (e) {
			e.preventDefault();
			const name = gameName.value && gameName.value.trim();
			const players = parseInt(playersCount.value, 10);
			if (!name) {
				alert('Introduce el nombre de la partida');
				gameName.focus();
				return;
			}
			if (isNaN(players) || players < 2 || players > 50) {
				alert('El número de jugadores debe estar entre 2 y 50');
				playersCount.focus();
				return;
			}

			// Aquí iría la llamada real al servidor para crear la partida.
			console.log('Crear partida:', { name, players });
			// Cerrar modal tras crear
			closeModal();
			// Crear tarjeta en 'Mis partidas'
			const container = document.getElementById('myGamesContainer');
			if (container) {
				// eliminar estado vacío si existe
				const empty = container.querySelector('.empty-state');
				if (empty) empty.remove();

				// generar código sencillo
				const code = 'BINGO' + Math.floor(Math.random() * 900 + 100);
				const now = new Date();
				const dateStr = now.toLocaleDateString();
				const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

				const card = document.createElement('div');
				card.className = 'game-card square';
				card.innerHTML = `
				  <div class="game-info">
				    <div class="game-title">${escapeHtml(name)}</div>
				    <div class="game-meta">
				      <div class="meta-item">Código: <strong class="code-value">${code}</strong></div>
				      <div class="meta-item">👥 ${players} jugadores</div>
				      <div class="meta-item">⏱ ${dateStr}, ${timeStr}</div>
				    </div>
				  </div>
				  <div style="width:100%">
				    <div class="pill">En curso</div>
				    <div class="spacer"></div>
				    <button class="join-btn">Unirse a la partida</button>
				  </div>
				`;

				// añadir evento al botón Unirse
				const joinBtn = card.querySelector('.join-btn');
				if (joinBtn) joinBtn.addEventListener('click', function () {
					alert('Unido a la partida: ' + name + ' (código ' + code + ')');
				});

				container.appendChild(card);
			}

			// Mostrar feedback rápido en consola
			console.log('Partida creada y añadida al DOM:', name, players);
		});
	}
});

// Util helper para evitar inyección básica en innerHTML
function escapeHtml(str) {
  if (!str) return '';
  return String(str).replace(/[&<>"']/g, function (s) {
    return ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":"&#39;"})[s];
  });
}
