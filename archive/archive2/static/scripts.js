async function updateBeerCount(delta) {
    const beerCountElement = document.querySelector('#beer-count');
    let beerCount = parseInt(beerCountElement.innerText);
    const nickname = 'Bob522';  // Zmień na odpowiednią wartość (np. na dynamiczną)

    beerCount += delta;
    if (beerCount < 0) beerCount = 0;  // Zapewnia, że liczba piwa nie spadnie poniżej 0.

    // Zaktualizuj widok
    beerCountElement.innerText = beerCount;

    // Wyślij zapytanie do serwera w celu aktualizacji liczby piwa
    await fetch('/update_beer_count', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ nickname: nickname, beerCount: beerCount }),
    });
}

// Obsługuje kliknięcia przycisków
document.getElementById('beer-increment').addEventListener('click', () => updateBeerCount(1));
document.getElementById('beer-decrement').addEventListener('click', () => updateBeerCount(-1));

// Pobranie początkowych danych
async function fetchStats() {
    const response = await fetch('/stats');
    const data = await response.json();
    document.querySelector('#total-games').innerText = data.total_games;
    // Dodatkowo załaduj liczbę piwa dla użytkownika
    const beerCountResponse = await fetch(`/get_beer_count?nickname=Bob522`);  // Jeśli chcesz dynamicznie
    const beerCountData = await beerCountResponse.json();
    document.querySelector('#beer-count').innerText = beerCountData.beer_count || 0;
}

fetchStats();



