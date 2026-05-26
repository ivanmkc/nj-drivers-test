import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import '../index.css';
import { MockApp } from './MockApp';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <MockApp />
  </StrictMode>,
);
