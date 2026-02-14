import React from 'react';

function Permissions() {

  // 1. Camera aur Mic Permission
  const requestCameraMic = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
      alert("Camera aur Mic ki permission mil gayi! 📷🎤");
      // stream ko baad mein kisi video tag se connect kar sakte hain
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
    if (!("Notification" in window)) {
      alert("Aapka browser notifications support nahi karta!");
      return;
    }
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

  // 5. Contacts Permission (Mobile Chrome par check karein)
  const getContacts = async () => {
    if ('contacts' in navigator && 'ContactsManager' in window) {
      try {
        const contacts = await navigator.contacts.select(['name', 'tel'], { multiple: false });
        if (contacts.length > 0) {
          alert(`Contact select kiya: ${contacts[0].name} 📱`);
        }
      } catch (err) {
        alert("Contact select nahi hua! ❌");
      }
    } else {
      alert("Aapka browser Contacts support nahi karta (Phone me try karein).");
    }
  };

  // Buttons ka simple design
  const btnStyle = {
    padding: '12px',
    margin: '8px 0',
    backgroundColor: '#007BFF',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '16px',
    width: '100%',
    fontWeight: 'bold'
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif', maxWidth: '400px', margin: 'auto', border: '1px solid #ccc', borderRadius: '10px', marginTop: '20px' }}>
      <h2 style={{ textAlign: 'center' }}>BaseKey App Permissions 🚀</h2>
      <p style={{ textAlign: 'center', color: '#555' }}>Niche diye gaye buttons ko test karein:</p>
      
      <button onClick={requestCameraMic} style={btnStyle}>📷 Allow Camera & Mic</button>
      <button onClick={requestLocation} style={btnStyle}>📍 Get My Location</button>
      <button onClick={requestNotification} style={btnStyle}>🔔 Enable Notifications</button>
      <button onClick={copyToClipboard} style={btnStyle}>📋 Copy App Link</button>
      <button onClick={getContacts} style={{...btnStyle, backgroundColor: '#28a745'}}>📱 Pick a Contact</button>

      {/* File/Photo Upload Box */}
      <div style={{ marginTop: '20px', padding: '10px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
        <label style={{ fontWeight: 'bold', display: 'block', marginBottom: '8px' }}>📂 Upload Photo / File:</label>
        <input type="file" accept="image/*" style={{ width: '100%' }} />
      </div>
    </div>
  );
}

export default Permissions;
