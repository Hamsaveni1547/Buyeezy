function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function setButtonState(button, state) {
    if (state === 'adding') {
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding...';
    } else if (state === 'added') {
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-check"></i> Added!';
    } else if (state === 'error') {
        button.disabled = false;
        button.innerHTML = '<i class="fas fa-cart-plus"></i> Add to Cart';
    } else {
        button.disabled = false;
        button.innerHTML = '<i class="fas fa-cart-plus"></i> Add to Cart';
    }
}

function handleAddToCart(productId, button, quantity = 1) {
    const csrftoken = getCookie('csrftoken');

    // Show loading state
    setButtonState(button, 'adding');

    fetch('/cart/add/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
            'product_id': productId,
            'quantity': parseInt(quantity) || 1
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.cart_count !== undefined) {
            const cartCount = document.getElementById('cart-count');
            if (cartCount) {
                cartCount.textContent = data.cart_count;
            }
        }
        setButtonState(button, 'added');
        setTimeout(() => setButtonState(button, 'normal'), 1500);
    })
    .catch(error => {
        console.error('Error:', error);
        setButtonState(button, 'error');
        alert('Error adding product to cart');
    });
}