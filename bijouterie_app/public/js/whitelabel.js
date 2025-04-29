// Convert SVG to PNG for better compatibility
const svgToPng = () => {
    // Create an image element to load the SVG
    const img = new Image();
    img.onload = function() {
        // Create a canvas element
        const canvas = document.createElement('canvas');
        canvas.width = 200;
        canvas.height = 60;
        const ctx = canvas.getContext('2d');
        
        // Draw the SVG on the canvas
        ctx.drawImage(img, 0, 0);
        
        // Convert canvas to PNG data URL
        const pngDataUrl = canvas.toDataURL('image/png');
        
        // Store the PNG data URL in localStorage for use in the theme
        localStorage.setItem('jewelry_logo_png', pngDataUrl);
    };
    
    // Load the SVG
    img.src = '/assets/bijouterie_app/images/jewelry_logo.svg';
};

// Apply whitelabel changes
const applyWhitelabel = () => {
    // Replace ERPNext logo with jewelry logo
    const logoImg = localStorage.getItem('jewelry_logo_png');
    if (logoImg) {
        // Find all instances of the ERPNext logo and replace them
        document.querySelectorAll('.navbar-brand img').forEach(img => {
            img.src = logoImg;
            img.style.height = '30px';
        });
    }
    
    // Replace page title
    if (document.title.includes('ERPNext') || document.title.includes('Frappe')) {
        document.title = document.title.replace('ERPNext', 'Bijouterie').replace('Frappe', 'Bijouterie');
    }
    
    // Hide ERPNext/Frappe references in the DOM
    const hideERPNextReferences = () => {
        // Hide elements containing ERPNext or Frappe text
        document.querySelectorAll('*').forEach(el => {
            if (el.innerText && (el.innerText.includes('ERPNext') || el.innerText.includes('Frappe'))) {
                if (el.tagName !== 'SCRIPT' && el.tagName !== 'STYLE') {
                    if (el.innerText.trim() === 'ERPNext' || el.innerText.trim() === 'Frappe') {
                        el.style.display = 'none';
                    } else {
                        el.innerText = el.innerText.replace(/ERPNext/g, 'Bijouterie').replace(/Frappe/g, 'Bijouterie');
                    }
                }
            }
        });
    };
    
    // Run initially and observe DOM changes
    hideERPNextReferences();
    
    // Create a mutation observer to handle dynamically added content
    const observer = new MutationObserver((mutations) => {
        hideERPNextReferences();
    });
    
    // Start observing the document body for DOM changes
    observer.observe(document.body, { childList: true, subtree: true });
};

// Initialize theme and whitelabel features
frappe.ui.form.on('*', {
    onload: function() {
        svgToPng();
        setTimeout(applyWhitelabel, 1000); // Delay to ensure DOM is loaded
    },
    refresh: function() {
        setTimeout(applyWhitelabel, 1000); // Apply on refresh as well
    }
});

// Apply on document ready
$(document).ready(function() {
    svgToPng();
    setTimeout(applyWhitelabel, 1000);
});
