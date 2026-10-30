import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App.jsx';
import { AlertasProvider } from './contexts/AlertasContext.jsx';
import { AuthProvider } from './contexts/AuthContext.jsx';
import './styles/global.css';

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <AlertasProvider>
        <AuthProvider>
          <App />
        </AuthProvider>
      </AlertasProvider>
    </BrowserRouter>
  </StrictMode>,
);
