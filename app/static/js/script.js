const body = document.querySelector('body');
const sidebar = body ? body.querySelector('nav.sidebar') : null;
const toggle = document.querySelector('.sidebar .toggle');

if (toggle && sidebar) {
    toggle.addEventListener('click', () => sidebar.classList.toggle('close'));
}

const signToVoiceNav = document.getElementById('signToVoiceNav');
if (signToVoiceNav) {
    signToVoiceNav.addEventListener('click', (event) => {
        event.preventDefault();
        const modalElement = document.getElementById('voiceDevelopmentModal');
        if (modalElement && window.bootstrap) {
            bootstrap.Modal.getOrCreateInstance(modalElement).show();
        } else {
            alert('This feature is still under development process.');
        }
    });
}

const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');

if (prevBtn) {
    prevBtn.addEventListener('click', () => {
        const container = document.querySelector('.gallery-container');
        if (container) container.scrollLeft -= 300;
    });
}

if (nextBtn) {
    nextBtn.addEventListener('click', () => {
        const container = document.querySelector('.gallery-container');
        if (container) container.scrollLeft += 300;
    });
}