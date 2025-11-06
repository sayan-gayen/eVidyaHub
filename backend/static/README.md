# Static files for local testing

This folder contains minimal static assets used for local testing and development.

Files added:
- `favicon.svg` — a small SVG logo used by `index.html` and templates.
- `index.html` — a tiny static landing page that links the CSS and JS.
- `css/style.css` — starter styles.
- `js/main.js` — tiny script that marks when JS has loaded.
- `robots.txt` — default allow-all.

To serve these files locally (from `backend`):

```powershell
cd 'C:\Users\saman\Desktop\Project 2\backend\static'
& 'C:\Users\saman\Desktop\Project 2\backend\.venv\Scripts\python.exe' -m http.server 3000
```

Then open http://127.0.0.1:3000/index.html in your browser.
