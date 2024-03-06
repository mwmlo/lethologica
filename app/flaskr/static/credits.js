const creditsPopupBtn = document.getElementById('creditsPopup');
const closeCreditsPopupBtn = document.getElementById('closeCreditsPopup');
const creditsPopup = document.getElementById('credits');

const aboutPopupBtn = document.getElementById('aboutPopup');
const closeAboutPopupBtn = document.getElementById('closeAboutPopup');
const aboutPopup = document.getElementById('about');

creditsPopupBtn.addEventListener('click', function () {
  creditsPopup.style.display = 'block';
});

closeCreditsPopupBtn.addEventListener('click', function () {
  creditsPopup.style.display = 'none';
});

aboutPopupBtn.addEventListener('click', () => {
  aboutPopup.style.display = 'block';
});

closeAboutPopupBtn.addEventListener('click', () => {
  aboutPopup.style.display = 'none';
});

window.addEventListener('click', function (event) {
  if (event.target === creditsPopup) {
    creditsPopup.style.display = 'none';
  }

  else if (event.target === aboutPopup) {
    aboutPopup.style.display = 'none';
  }
});
