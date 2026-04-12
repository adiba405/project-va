const API_URL = '/api';
const getToken = () => localStorage.getItem('token');
const setToken = (v) => localStorage.setItem('token', v);
const clearToken = () => localStorage.removeItem('token');

async function apiFetch(endpoint, method='GET', body=null){
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  const token = getToken(); if(token) opts.headers.Authorization = `Bearer ${token}`;
  if(body) opts.body = JSON.stringify(body);

  try {
    const res = await fetch(`${API_URL}${endpoint}`, opts);
    const payload = await res.json().catch(()=>null);

    if (!res.ok) {
      if (res.status === 401) {
        clearToken();
        window.location.href = 'index.html';
        return { success: false, message: 'Unauthorized. Redirecting to login.' };
      }
      return payload || { success: false, message: `Server error ${res.status}` };
    }

    return payload || { success: false, message: 'Empty response from server' };
  } catch (error) {
    return { success: false, message: `Network error: ${error.message}` };
  }
}

async function apiUpload(endpoint, formData) {
  const token = getToken();
  const opts = { method: 'POST', body: formData, headers: {} };
  if (token) opts.headers.Authorization = `Bearer ${token}`;

  try {
    const res = await fetch(`${API_URL}${endpoint}`, opts);
    const payload = await res.json().catch(()=>null);

    if (!res.ok) {
      if (res.status === 401) {
        clearToken();
        window.location.href = 'index.html';
        return { success: false, message: 'Unauthorized. Redirecting to login.' };
      }
      return payload || { success: false, message: `Server error ${res.status}` };
    }

    return payload || { success: false, message: 'Empty response from server' };
  } catch (error) {
    return { success: false, message: `Network error: ${error.message}` };
  }
}

function showMsg(el, msg, duration=4000){ 
  if(!el) return; 
  el.textContent = msg; 
  el.style.display = 'block';
  el.style.padding = '0.8rem';
  el.style.borderRadius = '6px';
  el.style.marginBottom = '1rem';
  el.style.backgroundColor = '#e8f5e9';
  el.style.color = '#2e7d32';
  el.style.border = '1px solid #c8e6c9';
  setTimeout(()=>{ el.textContent=''; el.style.display='none'; }, duration); 
}

function requireAuth(){ if(!getToken()){ window.location.href = 'index.html'; }}

function setData(name, data){ localStorage.setItem(name, JSON.stringify(data)); }
function getData(name){ const v = localStorage.getItem(name); return v ? JSON.parse(v) : null; }

function applyDarkMode(isDark) {
  if(isDark) {
    document.body.style.background = '#2E2639';
    document.body.style.color = '#E8DFF5';
    document.querySelectorAll('.card').forEach(el => {
      el.style.background = '#3D3447';
      el.style.boxShadow = '0 4px 20px rgba(0,0,0,0.2)';
    });
    document.querySelectorAll('.input-field, textarea').forEach(el => {
      el.style.background = '#4A4254';
      el.style.color = '#E8DFF5';
      el.style.borderColor = '#5A536B';
    });
    document.querySelectorAll('.btn').forEach(el => {
      el.style.background = 'linear-gradient(135deg, #B89FD4 0%, #A8899B 100%)';
      el.style.color = '#fff';
    });
    document.querySelectorAll('label').forEach(el => {
      el.style.color = '#E8DFF5';
    });
    document.querySelectorAll('.navbar').forEach(el => {
      el.style.background = 'rgba(61, 52, 71, 0.95)';
      el.style.color = '#E8DFF5';
    });
    document.querySelectorAll('.navbar a').forEach(el => {
      el.style.color = '#E8DFF5';
    });
  } else {
    document.body.style.background = 'linear-gradient(135deg, #E8DFF5 0%, #F3E8FF 100%)';
    document.body.style.color = '#5C4B63';
    document.querySelectorAll('.card').forEach(el => {
      el.style.background = '#fff';
      el.style.boxShadow = '0 4px 20px rgba(201,174,231,0.15)';
    });
    document.querySelectorAll('.input-field, textarea').forEach(el => {
      el.style.background = '#fff';
      el.style.color = '#5C4B63';
      el.style.borderColor = '#E8DFF5';
    });
    document.querySelectorAll('.btn').forEach(el => {
      el.style.background = '';
      el.style.color = '';
    });
    document.querySelectorAll('label').forEach(el => {
      el.style.color = '#5C4B63';
    });
    document.querySelectorAll('.navbar').forEach(el => {
      el.style.background = '';
      el.style.color = '';
    });
    document.querySelectorAll('.navbar a').forEach(el => {
      el.style.color = '';
    });
  }
}

function initDarkMode() {
  const isDark = localStorage.getItem('darkMode') === 'true';
  applyDarkMode(isDark);
  const toggle = document.getElementById('dark-mode-toggle');
  if(toggle) {
    toggle.checked = isDark;
    toggle.onchange = () => {
      localStorage.setItem('darkMode', toggle.checked);
      applyDarkMode(toggle.checked);
    };
  }
}
