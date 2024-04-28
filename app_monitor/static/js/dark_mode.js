function getSystemColorScheme() {
  if (window.matchMedia) {
    if(window.matchMedia('(prefers-color-scheme: dark)').matches){
      return 'dark';
    } else {
      return 'light';
    }
  }
  return 'light';
}

document.addEventListener('DOMContentLoaded', (event) => {
    const htmlElement = document.documentElement;
    const lightIcon = document.getElementById('icon-light');
    const darkIcon = document.getElementById('icon-dark');
    const autoIcon = document.getElementById('icon-auto');

    // Set the default theme to dark if no setting is found in local storage
    let currentTheme = localStorage.getItem('bsTheme') || 'system';
    if (currentTheme === 'system') {
        htmlElement.setAttribute('data-bs-theme', getSystemColorScheme());
        autoIcon.style.display = 'inline';
    } else {
        htmlElement.setAttribute('data-bs-theme', currentTheme);
        if (currentTheme === 'light') {
            lightIcon.style.display = 'inline';
        } else {
            darkIcon.style.display = 'inline';
        }
    }

    const toDark = document.getElementById('id_dark_mode');
    toDark.addEventListener('click', function () {
        localStorage.setItem('bsTheme', 'dark');
    });

    const toLight = document.getElementById('id_light_mode');
    toLight.addEventListener('click', function () {
        localStorage.setItem('bsTheme', 'light');
    });

    const toAuto = document.getElementById('id_system_mode');
    toAuto.addEventListener('click', function () {
        localStorage.setItem('bsTheme', 'system');
    });
});