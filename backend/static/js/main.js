// Minimal static JS for local testing
document.addEventListener('DOMContentLoaded', function () {
	console.log('static/main.js loaded')
	var body = document.querySelector('body')
	if (body) body.classList.add('static-loaded')
	var el = document.querySelector('.js-ready')
	if (el) el.textContent = 'JS loaded ✓'
})
