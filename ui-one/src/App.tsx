import React, { useState } from 'react';
import { ChatComponent2 } from './ChatComponent2';
import { BackgroundBoxesDemo } from './BackgroundBoxesDemo';
import './App.css';

function App() {
  const [recentSearches, setRecentSearches] = useState<string[]>([]); // State for recent searches

  return (
    <div className="flex flex-col h-screen">
      <header className="bg-gradient-to-r from-blue-500 via-blue-600 to-blue-700 text-white p-6 rounded-b-lg shadow-lg flex justify-center items-center">
  <h1 className="text-4xl font-extrabold tracking-wide leading-tight transform transition-all hover:scale-105">
    Factualize.ai
  </h1>
</header>
      <main className="flex-1 relative">
        <BackgroundBoxesDemo />
        <div className="absolute inset-0 flex items-center justify-center">
          <ChatComponent2 setRecentSearches={setRecentSearches} recentSearches={recentSearches} />
        </div>
      </main>
      <div className="p-4">
      </div>
    </div>
  );
}

export default App;