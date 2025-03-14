document.addEventListener("DOMContentLoaded", function () {
    var updateBtns = document.querySelectorAll(".update-cart");

    updateBtns.forEach((btn) => {
        btn.addEventListener("click", function () {
            var productId = this.dataset.product;
            var action = this.dataset.action;
            console.log("Product ID:", productId, "Action:", action);

            if (user === "AnonymousUser") {
                addCookieItem(productId, action);
            } else {
                updateUserOrder(productId, action);
            }
        });
    });

    function updateUserOrder(productId, action) {
        console.log("User is authenticated, sending data...");

        fetch("/update_item/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken,
            },
            body: JSON.stringify({ productId: productId, action: action }),
        })
            .then((response) => response.json())
            .then((data) => {
                console.log("Cart updated:", data);
                document.getElementById("cart-total").innerText = data.cartItems;
            });
    }

    function addCookieItem(productId, action) {
        console.log("User is not authenticated");

        if (!cart[productId]) {
            cart[productId] = { quantity: 0 };
        }

        if (action === "add") {
            cart[productId]["quantity"] += 1;
        } else if (action === "remove") {
            cart[productId]["quantity"] -= 1;
            if (cart[productId]["quantity"] <= 0) {
                delete cart[productId];
            }
        }

        console.log("Cart:", cart);
        document.cookie = "cart=" + JSON.stringify(cart) + "; path=/";
        document.getElementById("cart-total").innerText = Object.values(cart).reduce((sum, item) => sum + item.quantity, 0);
    }

    // Razorpay Dummy Payment Integration
    var razorpayBtn = document.getElementById("razorpay-button");

    if (razorpayBtn) {
        razorpayBtn.addEventListener("click", function () {
            var options = {
                key: "rzp_test_YourKeyHere",
                amount: 50000, // Amount in paise (50000 = ₹500)
                currency: "INR",
                name: "Martella Store",
                description: "Test Payment",
                image: "/static/images/logo.png",
                handler: function (response) {
                    alert("Payment Successful! Payment ID: " + response.razorpay_payment_id);
                    window.location.href = "/order_success/";
                },
                prefill: {
                    name: "John Doe",
                    email: "john@example.com",
                    contact: "9876543210",
                },
                theme: {
                    color: "#3399cc",
                },
            };

            var rzp = new Razorpay(options);
            rzp.open();
        });
    }
});
