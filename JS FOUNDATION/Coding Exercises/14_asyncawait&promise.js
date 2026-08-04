// Task 1: Async-Await with Promise.all

// Simulate fetching user data
function fetchUser() {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve("User fetched");
    }, 1000);
  });
}

// Simulate fetching posts
function fetchPosts() {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve("Posts fetched");
    }, 1000);
  });
}

// Fetch both promises simultaneously
async function fetchAllData() {
  try {
    const [user, posts] = await Promise.all([fetchUser(), fetchPosts()]);

    console.log(user);
    console.log(posts);
  } catch (error) {
    console.log(error);
  }
}

// Task 2: Error Handling with Promise.all

// Promise that resolves successfully
function fetchSuccess() {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve("Data fetched successfully");
    }, 1000);
  });
}

// Promise that rejects
function fetchFailure() {
  return new Promise((_, reject) => {
    setTimeout(() => {
      reject("Something went wrong!");
    }, 1000);
  });
}

// Handle success and failure
async function handlePromises() {
  try {
    const result = await Promise.all([fetchSuccess(), fetchFailure()]);

    console.log(result);
  } catch (error) {
    console.log(error);
  }
}

// Task 3: Promise.race with Timeout

// Return the promise result or timeout message
async function fetchWithTimeout(promise, timeout) {
  const timeoutPromise = new Promise((resolve) => {
    setTimeout(() => {
      resolve("Timeout exceeded");
    }, timeout);
  });

  return Promise.race([promise, timeoutPromise]);
}

// Test Cases

// Task 1
fetchAllData();
// Output (after 1 second):
// User fetched
// Posts fetched

// Task 2
handlePromises();
// Output (after 1 second):
// Something went wrong!

// Task 3

// Promise that resolves in 1 second
const fastPromise = new Promise((resolve) => {
  setTimeout(() => {
    resolve("Data received");
  }, 1000);
});

// Promise that resolves in 3 seconds
const slowPromise = new Promise((resolve) => {
  setTimeout(() => {
    resolve("Slow data received");
  }, 3000);
});

// Test: Success before timeout
fetchWithTimeout(fastPromise, 2000).then((result) => {
  console.log(result); // Data received
});

// Test: Timeout before promise resolves
fetchWithTimeout(slowPromise, 2000).then((result) => {
  console.log(result); // Timeout exceeded
});

