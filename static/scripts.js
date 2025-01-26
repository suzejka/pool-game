document.addEventListener('DOMContentLoaded', () => {
  const views = document.querySelectorAll('[id^="view-"]');
  const buttons = document.querySelectorAll('.btn');
  const loginForm = document.getElementById('login-form');
  const addGameForm = document.getElementById('add-game-form');
  const addBeerBtn = document.getElementById('add-beer-btn');

  let stats = {
    wins: 0,
    beers: 0,
  };

  const updateStats = () => {
    document.getElementById('stat-wins').textContent = stats.wins;
    document.getElementById('stat-beers').textContent = stats.beers;
  };

  const showView = (viewId) => {
    views.forEach((view) => {
      view.classList.toggle('hidden', view.id !== viewId);
    });
  };

  buttons.forEach((button) => {
    button.addEventListener('click', () => {
      const targetView = button.getAttribute('data-target');
      showView(targetView);
    });
  });

  loginForm.addEventListener('submit', (e) => {
    e.preventDefault();
    showView('view-home');
  });

  addGameForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const opponent = document.getElementById('opponent').value;
    const result = document.getElementById('result').value;
    if (result.startsWith('5-')) {
      stats.wins += 1;
    }
    const friendList = document.getElementById('friends-list');
    const newFriend = document.createElement('li');
    newFriend.classList.add('flex', 'justify-between');
    newFriend.innerHTML = `<span>${opponent}</span><span>Wynik: ${result}</span>`;
    friendList.appendChild(newFriend);
    updateStats();
    showView('view-home');
  });

  addBeerBtn.addEventListener('click', () => {
    stats.beers += 1;
    updateStats();
  });

  showView('view-login');
});
