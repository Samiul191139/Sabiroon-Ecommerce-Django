// Wait for DOM to load
document.addEventListener("DOMContentLoaded", function() {

    function getCookie(name){
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++){
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')){
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    var updateButtons = document.getElementsByClassName("update-cart");
    var cartTotalNav = document.getElementById("cart-totalnav");
    var cartTotalItem = document.getElementById("cart-totalItem");
    var cartTotalPrice = document.getElementById("cart-totalPrice");
    var url = '/update_item/';


    for (const updateButton of updateButtons) {
        updateButton.addEventListener("click", function () {
            var productId = this.getAttribute("data-product");
            var action = this.getAttribute("data-action");
            console.log('productId', productId, 'Action', action);
            console.log('User', user);

            if (user === "AnonymousUser") {
                addCookieItem(productId, action);
            } else {
                UpdateUserItem(this, productId, action);
            }
        });
    }

    function addCookieItem(productId, action) {
        console.log("Not logged in");
        if (action === "add") {
            if (cart[productId] == undefined) {
                cart[productId] = { 'quantity': 1 };
            } else {
                cart[productId]['quantity'] += 1;
            }
        } else if (action === "remove") {
            cart[productId]['quantity'] -= 1;
            if (cart[productId]['quantity'] <= 0) {
                console.log("Remove item");
                delete cart[productId];
            }
        }
        console.log("Cart", cart);
        document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/";
        location.reload();
    }

    function UpdateUserItem(button, productId, action) {
        const xhr = new XMLHttpRequest();

        xhr.onload = function () {
            console.log("Perform success");
            let res_dict = JSON.parse(xhr.responseText);

            // Update navbar badge
            const badge = document.querySelector('.cart-badge');
            if (badge) badge.innerText = res_dict.cart_total;

            if (cartTotalNav) cartTotalNav.innerText = res_dict.cart_total;
            if (cartTotalItem) cartTotalItem.innerText = "Items: " + res_dict.cart_total;
            if (cartTotalPrice) cartTotalPrice.innerText = "৳ " + (res_dict.cart_totalPrice).toFixed(2);

            // ✅ FIX: find the parent .cart-item div instead of <tr>
            const cartItemDiv = button.closest('.cart-item');
            if (cartItemDiv) {
                const qtySpan = cartItemDiv.querySelector('.item-quantity');
                const totalSpan = cartItemDiv.querySelector('.item-total');

                if (qtySpan) qtySpan.innerText = res_dict.quantity;
                if (totalSpan) totalSpan.innerText = "৳" + res_dict.item_total.toFixed(2);

                // // Remove div if quantity is 0
                // if (res_dict.quantity === 0) {
                //     cartItemDiv.remove();
                // }
            }

            // Toast (optional)
            if (action === "add") {
                showToast("Product added to cart");
            } else if (action === "remove") {
                showToast("Product removed from cart");
            }
            location.reload();

            // ✅ If last item removed → reload to update "Your cart is empty"
            if (res_dict.cart_total === 0) {
                location.reload();
            }
        };

        xhr.open("POST", '/update_item/');
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.setRequestHeader('X-CSRFToken', window.csrftoken);
        xhr.send(JSON.stringify({ productId, action }));
    }

});
