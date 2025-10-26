'use client';

interface AuthStatusProps {
  isAuthenticated: boolean;
  onAuthChange: () => void;
}

export default function AuthStatus({ isAuthenticated, onAuthChange }: AuthStatusProps) {
  const handleLogin = async () => {
    try {
      const response = await fetch('http://localhost:8000/auth/login');
      const data = await response.json();
      window.location.href = data.auth_url;
    } catch (error) {
      console.error('Error initiating login:', error);
    }
  };

  return (
    <div className="mb-6 bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">
            Google Calendar Authentication
          </h2>
          <p className="text-gray-600">
            {isAuthenticated 
              ? 'Connected to Google Calendar' 
              : 'Connect your Google Calendar to schedule meetings'}
          </p>
        </div>
        <div>
          {isAuthenticated ? (
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span className="text-green-700 font-semibold">Connected</span>
            </div>
          ) : (
            <button
              onClick={handleLogin}
              className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold transition"
            >
              Connect Calendar
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
