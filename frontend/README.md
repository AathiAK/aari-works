# Aari Works Frontend

React + Vite frontend for the Aari Works e-commerce application.

## Local development (standalone, outside Docker)
\`\`\`bash
npm install
npm run dev
\`\`\`

Normally this runs inside Docker Compose, proxied through Nginx — see the root README.

## Structure
- `src/pages/` — top-level route components (Login, Products, Cart, Checkout, etc.)
- `src/components/` — reusable UI pieces
- `src/layouts/` — page layout wrappers (e.g., admin layout vs. customer layout)
- `src/services/api.js` — Axios instance and API call functions
- `src/context/` — React context (e.g., auth state)
- `src/hooks/` — custom hooks
