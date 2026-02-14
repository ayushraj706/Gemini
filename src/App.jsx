// File: src/App.jsx
import React from 'react';
// Nayi file ko yahan 'import' karein
import Permissions from './Permissions'; 

function App() {
  return (
    <div>
      <h1>Mera BaseKey Startup</h1>
      
      {/* Yahan aapka Permissions wala component render ho jayega */}
      <Permissions /> 
      
    </div>
  );
}

export default App;

