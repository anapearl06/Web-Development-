document.addEventListener("DOMContentLoaded", () => {
  const products = [
    {
      id: 1,
      name: "⌨️ Mechanical Keyboard",
      price: 2499,
    },
    {
      id: 2,
      name: "🖱️ Wireless Mouse",
      price: 899,
    },
    {
      id: 3,
      name: "🎧 Bluetooth Headphones",
      price: 3499,
    },
    {
      id: 4,
      name: "💻 Laptop Stand",
      price: 1299,
    },
    {
      id: 5,
      name: "📱 Phone Holder",
      price: 499,
    },
    {
      id: 6,
      name: "⌚ Smart Watch",
      price: 5499,
    },
  ];

  const cart = [];

  const productList = document.getElementById("product-list");
  const cartItems = document.getElementById("cart-items");
  const emptyCartMessage = document.getElementById("empty-cart");
  const cartTotal = document.getElementById("cart-total");
  const totalPriceDisplay = document.getElementById("total-price");
  const checkoutBtn = document.getElementById("checkout-btn");

  // Display Products
  products.forEach((product) => {
    const productDiv = document.createElement("div");

    productDiv.classList.add("product");

    productDiv.innerHTML = `
            <div class="product-info">
                <h3>${product.name}</h3>
                <p>₹${product.price.toLocaleString("en-IN")}</p>
            </div>

            <button data-id="${product.id}">
                Add to Cart
            </button>
        `;

    productList.appendChild(productDiv);
  });

  // Add Product to Cart
  productList.addEventListener("click", (event) => {
    if (event.target.tagName === "BUTTON") {
      const productId = Number(event.target.dataset.id);

      const product = products.find((item) => item.id === productId);

      addToCart(product);
    }
  });

  function addToCart(product) {
    cart.push(product);

    renderCart();
  }

  // Render Cart
  function renderCart() {
    cartItems.innerHTML = "";

    let totalPrice = 0;

    if (cart.length === 0) {
      emptyCartMessage.classList.remove("hidden");

      cartTotal.classList.add("hidden");

      totalPriceDisplay.textContent = "₹0";

      return;
    }

    emptyCartMessage.classList.add("hidden");

    cartTotal.classList.remove("hidden");

    cart.forEach((item) => {
      totalPrice += item.price;

      const cartItem = document.createElement("div");

      cartItem.classList.add("cart-item");

      cartItem.innerHTML = `
                <span>${item.name}</span>
                <span>₹${item.price.toLocaleString("en-IN")}</span>
            `;

      cartItems.appendChild(cartItem);
    });

    totalPriceDisplay.textContent = `₹${totalPrice.toLocaleString("en-IN")}`;
  }

  // Checkout
  checkoutBtn.addEventListener("click", () => {
    if (cart.length === 0) {
      alert("🛒 Your cart is empty!");

      return;
    }

    alert("🎉 Order placed successfully!\n\nThank you for shopping with us ❤️");

    cart.length = 0;

    renderCart();
  });
});
