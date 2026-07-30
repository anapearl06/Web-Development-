// Task 1: Using 'this' in an Object
const person = {
  name: "Hitesh",
  age: 19.5,

  // Return a self introduction
  introduce() {
    return `Hi, my name is ${this.name} and I am ${this.age} years old`;
  },
};

// Task 2: Nested Functions
function outer() {
  // Inner function
  function inner() {
    return "Inner function called";
  }

  // Call and return the inner function
  return inner();
}

// Test Cases

// Task 1
console.log(person.introduce());
// Hi, my name is Hitesh and I am 19.5 years old

// Task 2
console.log(outer());
// Inner function called
