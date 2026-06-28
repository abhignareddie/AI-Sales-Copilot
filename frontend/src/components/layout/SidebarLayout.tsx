import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard, Users, Calendar, Mail, Ticket, Sparkles, BookOpen,
  Brain, History, Sliders, Shield, ClipboardCheck, Bot, BarChart2,
  Search, Bell, Sun, Moon, ChevronRight, LogOut,
} from 'lucide-react';
import { toast } from 'sonner';
import { clearAuth, getSavedIsDemo, getSavedUser } from '../../lib/auth';

interface SidebarLayoutProps {
  children: React.ReactNode;
}

export const SidebarLayout = ({ children }: SidebarLayoutProps) => {
  const [collapsed, setCollapsed] = useState(false);
  const [darkMode, setDarkMode] = useState(document.documentElement.classList.contains('dark'));
  const location = useLocation();
  const navigate = useNavigate();
  const user = getSavedUser() || { full_name: 'Demo User', email: 'demo@salescopilot.com', role: 'admin' };
  const isDemoModeActive = getSavedIsDemo();
  const userInitials = user.full_name?.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase() || 'US';

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    document.documentElement.classList.toggle('dark');
  };

  const handleLogout = () => {
    clearAuth();
    toast.info('Logged out successfully');
    navigate('/login');
  };

  const navItems = [
    { label: 'Dashboard', path: '/', icon: LayoutDashboard },
    { label: 'Customers', path: '/customers', icon: Users },
    { label: 'Meetings', path: '/meetings', icon: Calendar },
    { label: 'Emails', path: '/emails', icon: Mail },
    { label: 'Support Tickets', path: '/support-tickets', icon: Ticket },
    { label: 'Recommendations', path: '/recommendations', icon: Sparkles },
    { label: 'Review Queue', path: '/review', icon: ClipboardCheck },
    { label: 'Agent Trace', path: '/copilot', icon: Bot },
    { label: 'Knowledge Base', path: '/knowledge', icon: BookOpen },
    { label: 'Memory', path: '/memory', icon: Brain },
    { label: 'Audit Logs', path: '/audit-logs', icon: History },
    { label: 'BI Analytics', path: '/analytics', icon: BarChart2 },
    { label: 'System Security', path: '/security', icon: Shield, roles: ['admin', 'manager'] },
    { label: 'Settings', path: '/settings', icon: Sliders },
  ];

  const filteredNavItems = navItems.filter(item => !item.roles || item.roles.includes(user.role.toLowerCase()));

  const breadcrumb = location.pathname === '/'
    ? 'Executive Dashboard'
    : location.pathname.split('/').filter(Boolean).map(s => s.replace(/-/g, ' ')).join(' / ');

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50 dark:bg-gray-950">
      <aside className={`flex flex-col bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 transition-all duration-300 ${collapsed ? 'w-20' : 'w-64'}`}>
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-800">
          {!collapsed ? (
            <div className="flex items-center space-x-2">
              <div className="bg-blue-600 p-1.5 rounded-lg text-white"><Sparkles className="h-5 w-5" /></div>
              <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-blue-600 to-indigo-500 bg-clip-text text-transparent">SalesCopilot</span>
            </div>
          ) : (
            <div className="bg-blue-600 p-1.5 rounded-lg text-white mx-auto"><Sparkles className="h-5 w-5" /></div>
          )}
        </div>

        {isDemoModeActive && !collapsed && (
          <div className="mx-4 my-2 p-2 bg-amber-500/10 border border-amber-500/20 rounded-lg text-[10px] text-amber-500 font-bold tracking-wider uppercase text-center animate-pulse">
            Demo Mode Active
          </div>
        )}

        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          {filteredNavItems.map(item => {
            const isActive = location.pathname === item.path || (item.path !== '/' && location.pathname.startsWith(item.path));
            const Icon = item.icon;
            return (
              <Link key={item.path} to={item.path} className={`flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${isActive ? 'bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400' : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800/50'}`}>
                <Icon className={`h-5 w-5 ${isActive ? 'text-blue-600 dark:text-blue-400' : 'text-gray-400'}`} />
                {!collapsed && <span>{item.label}</span>}
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-gray-200 dark:border-gray-800 space-y-3">
          <button onClick={toggleDarkMode} className="flex items-center space-x-3 w-full px-3 py-2 rounded-lg text-sm font-medium text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800/50">
            {darkMode ? <Sun className="h-5 w-5 text-amber-500" /> : <Moon className="h-5 w-5 text-gray-400" />}
            {!collapsed && <span>{darkMode ? 'Light Mode' : 'Dark Mode'}</span>}
          </button>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="h-9 w-9 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center font-semibold text-blue-600 dark:text-blue-400">{userInitials}</div>
              {!collapsed && (
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold truncate text-gray-900 dark:text-gray-100">{user.full_name}</p>
                  <p className="text-xs text-gray-500 truncate capitalize">{user.role}</p>
                </div>
              )}
            </div>
            {!collapsed && (
              <button onClick={handleLogout} className="text-gray-400 hover:text-red-500 p-1" title="Log Out"><LogOut className="h-4 w-4" /></button>
            )}
          </div>
        </div>
      </aside>

      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="h-16 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between px-6 z-10">
          <div className="flex items-center space-x-4">
            <button onClick={() => setCollapsed(!collapsed)} className="text-gray-500 hover:text-gray-700 dark:text-gray-400">
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" /></svg>
            </button>
            <div className="text-sm text-gray-500 dark:text-gray-400 flex items-center space-x-2">
              <span>Platform</span><ChevronRight className="h-4 w-4" />
              <span className="text-gray-900 dark:text-gray-100 font-semibold capitalize">{breadcrumb}</span>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <div className="relative w-64 hidden md:block">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
              <input type="text" placeholder="Global search..." className="w-full pl-9 pr-4 py-1.5 bg-gray-100 dark:bg-gray-800 border-none rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 text-gray-900 dark:text-gray-100" />
            </div>
            <button className="relative p-1.5 text-gray-400 hover:text-gray-600"><Bell className="h-5 w-5" /><span className="absolute top-1.5 right-1.5 h-2 w-2 bg-red-500 rounded-full" /></button>
          </div>
        </header>
        <main className="flex-1 overflow-y-auto p-6 bg-gray-50 dark:bg-gray-950">{children}</main>
      </div>
    </div>
  );
};
