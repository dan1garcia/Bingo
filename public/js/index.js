// public/js/index.js (migrado desde root/index.js)
console.log('Public JS cargado');

// Util helper para evitar inyección básica en innerHTML
function escapeHtml(str) {
  if (!str) return '';
  return String(str).replace(/[&<>"']/g, (s) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":"&#39;"})[s]);
}

// Modal Create Game logic
document.addEventListener('DOMContentLoaded', function () {
	const openBtn = document.getElementById('createCard');
	const overlay = document.getElementById('createModalOverlay');
	const closeBtn = document.getElementById('closeModalBtn');
	const cancelBtn = document.getElementById('cancelCreate');
	const form = document.getElementById('createGameForm');
	const gameName = document.getElementById('gameName');
	const playersCount = document.getElementById('playersCount');

	// --- Selectores para Login y Registro ---
	const loginForm = document.getElementById('loginForm');
	const registerForm = document.getElementById('registerForm');
	const logoutButton = document.getElementById('logoutButton');

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
		form.addEventListener('submit', async function (e) {
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

			try {
				// Formatear la fecha al formato que MySQL/MariaDB entiende: YYYY-MM-DD HH:MM:SS
				const now = new Date();
				const formattedDate = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`;

				const response = await fetch('/api/partidas', {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json',
					},
					body: JSON.stringify({
						nombre_partida: name,
						// Nota: El backend no usa 'players' actualmente, pero lo enviamos por si se añade en el futuro.
						players: players,
						fecha_inicio: formattedDate,
						estado: 'en_curso'
					}),
				});

				if (!response.ok) {
					const errorData = await response.json();
					throw new Error(errorData.message || errorData.error || 'Error al crear la partida');
				}

				const result = await response.json();
				console.log('Partida creada:', result);

				// Cerrar modal tras crear
				closeModal();

				// Opcional: Recargar la página para ver la nueva partida desde la base de datos.
				// Esto es más simple que añadirla manualmente y asegura que los datos son correctos.
				window.location.reload();

			} catch (error) {
				console.error('Error en la creación de la partida:', error);
				alert(error.message);
			}
		});
	}

	// --- Lógica de Autenticación ---

	if (registerForm) {
		registerForm.addEventListener('submit', async (e) => {
			e.preventDefault();
			const nombre = registerForm.elements['nombre'].value;
			const correo = registerForm.elements['correo'].value;
			const contrasena = registerForm.elements['contrasena'].value;

			try {
				const response = await fetch('/api/auth/register', {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({ nombre, correo, contrasena }),
				});

				const result = await response.json();

				if (!response.ok) {
					throw new Error(result.message || 'Error en el registro.');
				}

				alert(result.message); // "Registro exitoso"
				window.location.href = '/login'; // Redirigir al login

			} catch (error) {
				console.error('Error al registrar:', error);
				alert(error.message);
			}
		});
	}

	if (loginForm) {
		loginForm.addEventListener('submit', async (e) => {
			e.preventDefault();
			const correo = loginForm.elements['correo'].value;
			const contrasena = loginForm.elements['contrasena'].value;

			try {
				const response = await fetch('/api/auth/login', {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({ correo, contrasena }),
				});

				const result = await response.json();

				if (!response.ok) {
					throw new Error(result.message || 'Error al iniciar sesión.');
				}

				// Redirigir a la URL que nos indica el backend
				window.location.href = result.redirectUrl || '/';
			} catch (error) {
				console.error('Error en el inicio de sesión:', error);
				alert(error.message);
			}
		});
	}

	if (logoutButton) {
		logoutButton.addEventListener('click', async (e) => {
			e.preventDefault();

			try {
				const response = await fetch('/api/auth/logout', {
					method: 'POST',
				});

				const result = await response.json();

				if (!response.ok) {
					throw new Error(result.message || 'Error al cerrar sesión.');
				}

				window.location.href = result.redirectUrl || '/login';
			} catch (error) {
				console.error('Error al cerrar sesión:', error);
				alert(error.message);
			}
		});
	}

	// --- Lógica para cargar partidas del usuario ---
	const myGamesContainer = document.getElementById('myGamesContainer');

	async function loadUserGames() {
		if (!myGamesContainer) return; // No estamos en la página de usuarios

		try {
			const response = await fetch('/api/partidas');
			if (!response.ok) {
				throw new Error('No se pudieron cargar las partidas.');
			}
			const games = await response.json();

			// Limpiar el contenedor antes de añadir las nuevas tarjetas
			myGamesContainer.innerHTML = '';

			if (games.length === 0) {
				// Mostrar estado vacío si no hay partidas
				myGamesContainer.innerHTML = `
					<div class="empty-state">
						<p>Aún no has creado ninguna partida.</p>
						<p>¡Crea una para empezar a jugar!</p>
					</div>
				`;
			} else {
				games.forEach(game => {
					const card = createGameCard(game);
					myGamesContainer.appendChild(card);
				});
			}
		} catch (error) {
			console.error('Error al cargar partidas:', error);
			myGamesContainer.innerHTML = `<p class="error-message">Error al cargar tus partidas. Inténtalo de nuevo más tarde.</p>`;
		}
	}

	function createGameCard(game) {
		const card = document.createElement('div');
		card.className = 'game-card square';
		const gameDate = new Date(game.fecha_inicio);
		const dateStr = gameDate.toLocaleDateString();
		const timeStr = gameDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

		card.innerHTML = `
		  <div class="game-info">
			<div class="game-title">${escapeHtml(game.nombre_partida)}</div>
			<div class="game-meta">
			  <div class="meta-item">ID: <strong class="code-value">${escapeHtml(game.id_partidas)}</strong></div>
			  <div class="meta-item">⏱ ${dateStr}, ${timeStr}</div>
			</div>
		  </div>
		  <div style="width:100%">
			<div class="pill ${game.estado === 'en_curso' ? 'active' : ''}">${escapeHtml(game.estado)}</div>
			<div class="spacer"></div>
			<button class="join-btn" onclick="window.location.href='/game/${escapeHtml(game.id_partidas)}'">Unirse a la partida</button>
		  </div>`;
		return card;
	}

	// Cargar las partidas cuando el DOM esté listo
	loadUserGames();
});
