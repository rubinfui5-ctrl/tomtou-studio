import React from 'react';
import ReactDOM from 'react-dom/client';

function App() {
  return (
    <div style={{background:'#070707',minHeight:'100vh',color:'#fff',fontFamily:'monospace',padding:'40px',display:'flex',alignItems:'center',justifyContent:'center'}}>
      <div style={{textAlign:'center'}}>
        <h1 style={{color:'#00aaff',fontSize:'36px',letterSpacing:'6px'}}>TOM x TOU</h1>
        <p style={{color:'#555',letterSpacing:'3px'}}>INSTAGRAM AI STUDIO</p>
        <p style={{color:'#00ff88',marginTop:'20px'}}>LIVE AND RUNNING</p>
      </div>
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
