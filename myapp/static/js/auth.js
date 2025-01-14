class AuthUI {
    constructor() {
        this.form = document.getElementById('authForm');
        this.inputs = document.querySelectorAll('.input-group input');
        this.buttons = document.querySelectorAll('.btn');
        this.init();
    }

    init() {
        this.setupFormAnimation();
        this.setupInputEffects();
        this.setupButtonEffects();
    }

    setupFormAnimation() {
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.animateSubmit();
        });
    }

    setupInputEffects() {
        this.inputs.forEach(input => {
            input.addEventListener('focus', () => this.onInputFocus(input));
            input.addEventListener('blur', () => this.onInputBlur(input));
        });
    }

    setupButtonEffects() {
        this.buttons.forEach(button => {
            button.addEventListener('mousemove', (e) => this.handleButtonHover(e, button));
            button.addEventListener('mouseleave', () => this.resetButtonEffect(button));
        });
    }

    onInputFocus(input) {
        input.parentElement.classList.add('focused');
        this.createInputRipple(input);
    }

    onInputBlur(input) {
        if (input.value === '') {
            input.parentElement.classList.remove('focused');
        }
    }

    createInputRipple(input) {
        const ripple = document.createElement('div');
        ripple.className = 'input-ripple';
        input.parentElement.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 1000);
    }

    handleButtonHover(e, button) {
        const rect = button.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        button.style.setProperty('--x', `${x}px`);
        button.style.setProperty('--y', `${y}px`);
    }

    resetButtonEffect(button) {
        button.style.setProperty('--x', '50%');
        button.style.setProperty('--y', '50%');
    }

    animateSubmit() {
        const button = this.form.querySelector('button[type="submit"]');
        button.classList.add('loading');
        
        setTimeout(() => {
            button.classList.remove('loading');
            this.showSuccess();
        }, 1500);
    }

    showSuccess() {
        const container = document.querySelector('.container');
        container.classList.add('success');
        
        setTimeout(() => {
            container.classList.remove('success');
        }, 1500);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new AuthUI();
});