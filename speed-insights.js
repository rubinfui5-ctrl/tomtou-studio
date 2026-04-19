// Vercel Speed Insights initialization
// This creates a queue for Speed Insights events and loads the tracking script
(function() {
  // Initialize the queue if it doesn't exist
  if (window.si) return;
  
  window.si = function a(...params) {
    window.siq = window.siq || [];
    window.siq.push(params);
  };

  // Check if script already exists
  const scriptSrc = '/_vercel/speed-insights/script.js';
  if (document.head.querySelector(`script[src*="${scriptSrc}"]`)) return;

  // Create and inject the script
  const script = document.createElement('script');
  script.src = scriptSrc;
  script.defer = true;
  
  // Add SDK metadata
  script.dataset.sdkn = '@vercel/speed-insights';
  script.dataset.sdkv = '2.0.0';
  
  script.onerror = () => {
    console.log(
      `[Vercel Speed Insights] Failed to load script from ${scriptSrc}. Please check if any content blockers are enabled and try again.`
    );
  };
  
  document.head.appendChild(script);
})();
