// Task 1: Counter Using Closures
function createCounter() {
  // Store the counter value
  let count = 0;

  // Return a function that updates the counter
  return function () {
    count++;
    return count;
  };
}

// Task 2: Rate Limiter
function rateLimiter(fn, limit) {
  // Store the last execution time
  let lastCalled = 0;

  // Return a new function
  return function (...args) {
    const currentTime = Date.now();

    // Check if the limit has passed
    if (currentTime - lastCalled >= limit) {
      lastCalled = currentTime;
      return fn(...args);
    }

    return "Rate limit exceeded";
  };
}

// Task 3: Memoization
function memoize(fn) {
  // Store cached results
  const cache = {};

  // Return a memoized function
  return function (...args) {
    const key = JSON.stringify(args);

    // Return cached result if available
    if (key in cache) {
      return cache[key];
    }

    // Store and return the new result
    cache[key] = fn(...args);
    return cache[key];
  };
}

// Sample Functions

function greet(name) {
  return `Hello, ${name}!`;
}

function add(a, b) {
  console.log("Calculating...");
  return a + b;
}

// Test Cases

// Task 1
const counter = createCounter();

console.log(counter()); // 1
console.log(counter()); // 2
console.log(counter()); // 3

// Task 2
const limitedGreet = rateLimiter(greet, 3000);

console.log(limitedGreet("Ananya")); // Hello, Ananya!
console.log(limitedGreet("Ananya")); // Rate limit exceeded

setTimeout(() => {
  console.log(limitedGreet("Ananya")); // Hello, Ananya! (after 3 seconds)
}, 3000);

// Task 3
const memoizedAdd = memoize(add);

console.log(memoizedAdd(5, 10)); // Calculating...
// 15

console.log(memoizedAdd(5, 10)); // 15 (cached)

console.log(memoizedAdd(7, 8)); // Calculating...
// 15

console.log(memoizedAdd(7, 8)); // 15 (cached)

console.log(memoizedAdd(1, 2)); // Calculating...
// 3

console.log(memoizedAdd(1, 2)); // 3 (cached)

console.log(memoizedAdd(3, 4)); // Calculating...
// 7

console.log(memoizedAdd(3, 4)); // 7 (cached)

console.log(memoizedAdd(5, 6)); // Calculating...
// 11

console.log(memoizedAdd(5, 6)); // 11 (cached)

console.log(memoizedAdd(7, 8)); // Calculating...
// 15

console.log(memoizedAdd(7, 8)); // 15 (cached)

