// WebApp initialization
document.addEventListener('DOMContentLoaded', function() {
    // Initialize map
    const map = L.map('map').setView([41.3110, 69.2797], 10); // Toshkent markazi
    
    // Add tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
    
    // Initialize marker cluster group
    const markers = L.markerClusterGroup({
        chunkedLoading: true,
        maxClusterRadius: 80
    });
    
    // Add marker cluster to map
    map.addLayer(markers);
    
    // Get active listings from the bot's backend
    loadActiveListings();
    
    // Function to load active listings
    function loadActiveListings() {
        // In a real implementation, this would fetch from your bot's API
        // For now, we'll use a simulated API call
        document.getElementById('loader').classList.remove('hidden');
        
        // This would be replaced with actual API call to your backend
        setTimeout(() => {
            // Simulate API response with test data
            const listings = getTestListings();
            displayListingsOnMap(listings);
            document.getElementById('loader').classList.add('hidden');
        }, 1000);
    }
    
    // Function to display listings on map
    function displayListingsOnMap(listings) {
        markers.clearLayers();
        
        listings.forEach(listing => {
            if (listing.location) {
                const [lat, lng] = listing.location.split(',').map(coord => parseFloat(coord.trim()));
                
                if (!isNaN(lat) && !isNaN(lng)) {
                    // Create custom icon based on category
                    const icon = L.divIcon({
                        className: `custom-marker ${getCategoryClass(listing.category)}`,
                        html: `<div>${getCategoryEmoji(listing.category)}</div>`,
                        iconSize: [30, 30],
                        iconAnchor: [15, 15]
                    });
                    
                    const marker = L.marker([lat, lng], { icon: icon });
                    
                    // Add popup with basic info
                    marker.bindPopup(`
                        <strong>${listing.title}</strong><br>
                        Turi: ${listing.category}<br>
                        Narxi: ${listing.price} ${listing.currency}<br>
                        <button onclick="requestListingDetails(${listing.id})">Batafsil ma'lumot</button>
                    `);
                    
                    // Add click event for showing details panel
                    marker.on('click', function() {
                        showListingDetails(listing);
                    });
                    
                    markers.addLayer(marker);
                }
            }
        });
    }
    
    // Function to show listing details in the panel
    function showListingDetails(listing) {
        document.getElementById('listing-title').textContent = listing.title;
        document.getElementById('listing-category').textContent = listing.category;
        document.getElementById('listing-price').textContent = `${listing.price} ${listing.currency}`;
        document.getElementById('listing-floor').textContent = `${listing.floor}-qavat`;
        document.getElementById('listing-rooms').textContent = `${listing.rooms} xona`;
        
        // Store the current listing for the details button
        document.getElementById('show-more').dataset.listingId = listing.id;
        
        document.getElementById('listing-details').classList.remove('hidden');
    }
    
    // Close details panel
    document.getElementById('close-details').addEventListener('click', function() {
        document.getElementById('listing-details').classList.add('hidden');
    });
    
    // Request more details button
    document.getElementById('show-more').addEventListener('click', function() {
        const listingId = this.dataset.listingId;
        if (listingId) {
            requestListingDetails(parseInt(listingId));
        }
    });
    
    // Generate test data (replace with actual API call)
    function getTestListings() {
        return [
            {
                id: 1,
                title: "Yangi uy, oilaga",
                category: "Oilaga",
                price: "500,000",
                currency: "so'm",
                floor: "3",
                rooms: "3",
                location: "41.3110, 69.2797"
            },
            {
                id: 2,
                title: "Qizlar uchun kvartira",
                category: "Qizlarga",
                price: "450,000",
                currency: "so'm",
                floor: "5",
                rooms: "2",
                location: "41.3150, 69.2850"
            },
            {
                id: 3,
                title: "Bollarga qulay uy",
                category: "Bollarga",
                price: "600,000",
                currency: "so'm",
                floor: "2",
                rooms: "4",
                location: "41.3050, 69.2750"
            }
        ];
    }
    
    // Helper function to get category class
    function getCategoryClass(category) {
        const classes = {
            "Oilaga": "family-listing",
            "Qizlarga": "girls-listing",
            "Bollarga": "kids-listing",
            "Hammaga": "all-listing"
        };
        return classes[category] || "default-listing";
    }
    
    // Helper function to get category emoji
    function getCategoryEmoji(category) {
        const emojis = {
            "Oilaga": "👨‍👩‍👧‍👦",
            "Qizlarga": "👩",
            "Bollarga": "👶",
            "Hammaga": "👥"
        };
        return emojis[category] || "🏠";
    }
});

// Function to request listing details (to be called from Telegram bot)
function requestListingDetails(listingId) {
    // This will send a message to the Telegram bot with the listing ID
    if (window.Telegram && window.Telegram.WebApp) {
        Telegram.WebApp.sendData(JSON.stringify({
            action: "listing_details",
            listing_id: listingId
        }));
    } else {
        // For testing outside Telegram
        alert(`Batafsil ma'lumot so'raldi: Elon ID ${listingId}`);
    }
}

// Initialize Telegram WebApp
if (window.Telegram && window.Telegram.WebApp) {
    Telegram.WebApp.ready();
    Telegram.WebApp.expand();
}