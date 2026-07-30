// Task 1: String to Number
function stringToNumber(str) {
  // Convert string to number
  let num = Number(str);

  // Return message if conversion fails
  if (isNaN(num)) {
    return "Not a number";
  }

  return num;
}

// Task 2: Flip Boolean
function flipBoolean(value) {
  // Convert to boolean and flip it
  return !Boolean(value);
}

// Task 3: Check Type
function whatAmI(value) {
  // Try converting the input to a number
  let converted = Number(value);

  // If conversion is successful
  if (!isNaN(converted)) {
    return "I'm a number!";
  }

  // If the input is a string
  if (typeof value === "string") {
    return "I'm a string!";
  }
}

// Task 4: Truthy or Falsy
function isItTruthy(value) {
  // Check if the value is truthy
  if (value) {
    return "It's truthy!";
  }

  return "It's falsey!";
}

// Test Cases

// Task 1
console.log(stringToNumber("123")); // 123
console.log(stringToNumber("45.6")); // 45.6
console.log(stringToNumber("hello")); // Not a number

// Task 2
console.log(flipBoolean(true)); // false
console.log(flipBoolean(false)); // true
console.log(flipBoolean(0)); // true
console.log(flipBoolean("Hi")); // false

// Task 3
console.log(whatAmI("42")); // I'm a number!
console.log(whatAmI("Hello")); // I'm a string!

// Task 4
console.log(isItTruthy(1)); // It's truthy!
console.log(isItTruthy(0)); // It's falsey!
console.log(isItTruthy("")); // It's falsey!
console.log(isItTruthy("JavaScript")); // It's truthy!
