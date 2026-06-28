import { Navigate } from 'react-router-dom';
import { getSavedAuthToken, getSavedIsDemo, getSavedUser } from '../../lib/auth';

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: string[];
}

export const ProtectedRoute = ({ children, allowedRoles }: ProtectedRouteProps) => {
  const token = getSavedAuthToken();
  const isDemo = getSavedIsDemo();
  const user = getSavedUser();

  if (!token && !isDemo) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && user && !allowedRoles.includes(user.role.toLowerCase())) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};
