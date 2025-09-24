var updateButtons = document.getElementsByClassName("update-cart")
var cartTotalNav = document.getElementById("cart-totalnav")
var cartTotalItem = document.getElementById("cart-totalItem")
var cartTotalPrice = document.getElementById("cart-totalPrice")

var url = '/update_item/'


for (const updateButton of updateButtons) {
    updateButton.addEventListener("click", function () {
        var productId = this.getAttribute("data-product")
        var action = this.getAttribute("data-action")
        console.log('productId', productId, 'Action', action)
        console.log('User', user)

        if (user == "AnonymousUser") {
            addCookieItem(productId, action)
        } else {
            UpdateUserItem(this, productId, action)
        }
    })
}


// For non-login user
function addCookieItem(productId, action) {
    console.log("Not logged in")

    if (action == "add") {
        if (!cart[productId]) {
            cart[productId] = { 'quantity': 1 };
        } else {
            cart[productId]['quantity'] += 1;
        }
        showToast("Product added to cart");
    } else if (action == "remove") {
        if (cart[productId]) {
            cart[productId]['quantity'] -= 1;
            if (cart[productId]['quantity'] <= 0) {
                delete cart[productId];
            }
            showToast("Product removed from cart");
        }
    }

    // Update cart cookie
    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/";

    // Update cart badge in navbar
    const cartBadge = document.querySelector(".cart-badge");
    if (cartBadge) {
        let totalQuantity = Object.values(cart).reduce((sum, item) => sum + item.quantity, 0);
        cartBadge.textContent = totalQuantity;
    }

    // Optionally: update quantity display in cart page if open
    const quantitySpans = document.querySelectorAll(`.chg-quantity[data-product='${productId}']`);
    quantitySpans.forEach(span => {
        const parent = span.parentElement;
        if (parent) {
            const qtySpan = parent.querySelector("span");
            if (qtySpan) qtySpan.textContent = cart[productId] ? cart[productId]['quantity'] : 0;
        }
    });
}

// function UpdateUserItem(productId, action) {
//     console.log("User logged in. Item to be added:", productId, "\nAction: ", action)

//     var url = '/update_item/'
//     var options = {
//         method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken, },
//         body: JSON.stringify({ 'productId': productId, 'action': action })
//     }

//     fetch(url, options = options)
//         .then((response) => response.json()) //return the promise
//         .then((data) => console.log('Data: ', data));

// }

// AJAX from W3schools
function UpdateUserItem(button, productId, action) {
    let xhr = new XMLHttpRequest();
    xhr.onload = function () {
        console.log("Perform success")
        let res_dict = JSON.parse(xhr.responseText)
        cartTotalNav.innerHTML = res_dict.cart_total
        // currently inefficient way of dealing with update in AJAX
        // TODO
        try {
            cartTotalItem.innerHTML = "Items: " + res_dict.cart_total
            cartTotalPrice.innerHTML = "$ " + (res_dict.cart_totalPrice).toFixed(2)
            button.parentElement.parentElement.children[0].innerHTML = res_dict.quantity
            button.parentElement.parentElement.parentElement.children[4].innerHTML = (res_dict.quantity * res_dict.unitprice).toFixed(2)
        } catch (error) {
            console.log("Catch", error)
        }

        if (action === "add") 
        {
            showToast("Product added to cart");
        } 
        else if (action === "remove")
        {
            showToast("Product removed from cart");
        }

    }
    xhr.open("POST", url)
    xhr.setRequestHeader('Content-Type', 'application/json')
    xhr.setRequestHeader('X-CSRFToken', csrftoken)
    xhr.send(JSON.stringify({ 'productId': productId, 'action': action }))
}

