'use strict';

const fs = require('node:fs');
const path = require('node:path');

const rawUrl = process.env.VITE_SOCKET_URL?.trim();
if (!rawUrl) {
  throw new Error('VITE_SOCKET_URL is required for the Netlify build');
}

let parsedUrl;
try {
  parsedUrl = new URL(rawUrl);
} catch {
  throw new Error('VITE_SOCKET_URL must be a valid HTTP(S) URL');
}
if (!['http:', 'https:'].includes(parsedUrl.protocol) ||
    parsedUrl.username || parsedUrl.password ||
    parsedUrl.pathname !== '/' || parsedUrl.search || parsedUrl.hash) {
  throw new Error('VITE_SOCKET_URL must be an HTTP(S) origin without a path, credentials, query or hash');
}

const file = path.resolve(__dirname, '../client/public/visitor-tracking.js');
const marker = "'__VITE_SOCKET_URL__'";
const source = fs.readFileSync(file, 'utf8');
if (source.split(marker).length !== 2) {
  throw new Error('Expected exactly one Socket URL placeholder in visitor-tracking.js');
}
fs.writeFileSync(file, source.replace(marker, JSON.stringify(parsedUrl.origin)), 'utf8');
console.log('Configured visitor-tracking.js from VITE_SOCKET_URL');
