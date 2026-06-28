import type { UserProfile } from '../types';

export const getSavedAuthToken = () => localStorage.getItem('token') || '';
export const getSavedIsDemo = () => sessionStorage.getItem('demo_active') === 'true';

export const getSavedUser = (): UserProfile | null => {
  const stored = sessionStorage.getItem('user_profile');
  return stored ? JSON.parse(stored) : null;
};

export const setDemoUser = () => {
  sessionStorage.setItem('demo_active', 'true');
  sessionStorage.setItem('user_profile', JSON.stringify({
    id: 99,
    full_name: 'Abhiram',
    email: 'demo@salescopilot.com',
    role: 'admin',
  }));
};

export const clearAuth = () => {
  localStorage.removeItem('token');
  sessionStorage.removeItem('demo_active');
  sessionStorage.removeItem('user_profile');
};
