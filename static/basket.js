
document.addEventListener('DOMContentLoaded', function() {
    // Update basket count on page load
    updateBasketCount();
    
    // Add event listeners to "Add to Basket" buttons
    const addButtons = document.querySelectorAll('.add-to-basket');
    addButtons.forEach(button => {
        button.addEventListener('click', function() {
            const barcode = this.getAttribute('data-barcode');
            addToBasket(barcode, 1);
        });
    });
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
        updateBasketCount();
        showNotification('Product added to basket');
    })
    .catch(error => {
        console.error('Error adding to basket:', error);
    });
}

function updateBasketCount() {
    fetch('/api/basket/count')
    .then(response => response.json())
    .then(data => {
        document.getElementById('basket-count').textContent = data.count;
    });
}