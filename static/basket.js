document.addEventListener('DOMContentLoaded', function() {
    // Set up event listeners for the Add to Basket button
    const addToBasketBtn = document.querySelector('.add-to-basket');
    if (addToBasketBtn) {
        addToBasketBtn.addEventListener('click', function() {
            const barcode = this.getAttribute('data-barcode');
            addToBasket(barcode, 1);
        });
    }

    // Update basket count when page loads
    updateBasketCount();
});

function addToBasket(barcode, quantity) {
    fetch('/api/basket/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            barcode: barcode,
            quantity: quantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateBasketCount();
            showAddedMessage();
        }
    })
    .catch(error => console.error('Error adding to basket:', error));
}

// Function to update the basket count
async function updateBasketCount() {
    try {
        const response = await fetch('/api/basket/count');
        const data = await response.json();
        const basketCount = document.getElementById('basket-count');
        if (basketCount) {
            basketCount.textContent = data.count;
        }
    } catch (error) {
        console.error('Error getting basket count:', error);
    }
}

// Update basket count when page loads
document.addEventListener('DOMContentLoaded', updateBasketCount);

// Export the function so it can be used by other scripts
window.updateBasketCount = updateBasketCount;

function showAddedMessage() {
    // Create a message element
    const message = document.createElement('div');
    message.className = 'added-to-basket-message';
    message.textContent = 'Product added to basket!';
    
    // Add it to the page
    document.body.appendChild(message);
    
    // Remove after 3 seconds
    setTimeout(() => {
        message.remove();
    }, 3000);
}