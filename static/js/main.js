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

async function addToCart(productId, quantity = 1) {
    const csrftoken = getCookie('csrftoken');
    try {
        const response = await fetch('/cart/add/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({
                'product_id': productId,
                'quantity': quantity
            })
        });
        
        const data = await response.json();
        if (response.ok) {
            // Update cart count in navbar if you have one
            if (data.cart_count !== undefined) {
                const cartCount = document.getElementById('cart-count');
                if (cartCount) {
                    cartCount.textContent = data.cart_count;
                }
            }
            alert('Product added to cart successfully!');
        } else {
            alert(data.error || 'Error adding product to cart');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error adding product to cart');
    }
}