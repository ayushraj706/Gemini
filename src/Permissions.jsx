// File: src/App.jsx ya src/Permissions.jsx
import React from 'react';

function App() {

  // 1. Camera aur Mic Permission
  const requestCameraMic = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
      alert("Camera aur Mic ki permission mil gayi! 📷🎤");
      // stream ko video tag mein use kar sakte hain
    } catch (err) {
      alert("User ne Camera/Mic block kar diya! ❌");
    }
  };

  // 2. Location Permission
  const requestLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          alert(`Location mil gayi! 📍\nLat: ${position.coords.latitude}\nLng: ${position.coords.longitude}`);
        },
        (error) => {
          alert("Location block kar di gayi! ❌");
        }
      );
    } else {
      alert("Browser location support nahi karta!");
    }
  };

  // 3. Notification Permission
  const requestNotification = () => {
    Notification.requestPermission().then((permission) => {
      if (permission === "granted") {
        new Notification("BaseKey mein aapka swagat hai! 🔔");
        alert("Notification ON ho gaye! ✅");
      } else {
        alert("Notification block kar diye gaye! ❌");
      }
    });
  };

  // 4. Clipboard Permission (Text Copy)
  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText("https://basekey.online");
      alert("Link copy ho gaya! 📋");
    } catch (err) {
      alert("Copy fail ho gaya! ❌");
    }
  };

  // 5. Contacts Permission (Sirf Mobile Chrome par chalega)
  const getContacts = async () => {
    if ('contacts' in navigator && 'ContactsManager' in window) {
      try {
        const contacts = await navigator.contacts.select(['name', 'tel'], { multiple: false });
        alert(`Contact select kiya: ${contacts[0].name} 📱`);
      } catch (err) {
        alert("Contact select nahi hua! ❌");
      }
    } else {
      alert("Aapka browser Contacts support nahi karta (Mobile me try karein).");
    }
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif', textAlign: 'center' }}>
      <h1>BaseKey App Permissions 🚀</h1>
      <p>Niche diye gaye buttons par click karke permissions test karein:</p>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxWidth: '300px', margin: 'auto' }}>
        
        <button onClick={requestCameraMic} style={btnStyle}>📷 Allow Camera & Mic</button>
        <button onClick={requestLocation} style={btnStyle}>📍 Get My Location</button>
        <button onClick={requestNotification} style={btnStyle}>🔔 Enable Notifications</button>
        <button onClick={copyToClipboard} style={btnStyle}>📋 Copy App Link</button>
        <button onClick={getContacts} style={btnStyle}>📱 Pick a Contact</button>

        {/* File aur Photo ke liye JavaScript function nahi, seedha HTML input lagta hai */}
        <label style={{ marginTop: '10px', fontWeight: 'bold' }}>📂 Upload Photo / File:</label>
        <input type="file" accept="image/*" style={{ padding: '10px' }} />

      </div>
    </div>
  );
}

// Button ka thoda sa design (CSS)
const btnStyle = {
  padding: '12px',
  backgroundColor: '#007BFF',
  color: 'white',
  border: 'none',
  borderRadius: '8px',
  cursor: 'pointer',
  fontSize: '16px'
};

export default App;
