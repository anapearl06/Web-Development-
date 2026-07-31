// Task 1 & 2: Functional Constructor with Error Handling

// Functional Constructor
function Person(name, age) {
  // Validate age
  if (typeof age !== "number" || age <= 0) {
    throw new Error("Age must be a positive number.");
  }

  // Initialize properties
  this.name = name;
  this.age = age;

  // Add greet method
  this.greet = function () {
    return `Hello, my name is ${this.name}`;
  };
}

// Test Cases

// Valid Person
try {
  const person1 = new Person("Hitesh", 19.5);

  console.log(person1.greet()); // Hello, my name is Hitesh
  console.log(person1.age); // 19.5
} catch (error) {
  console.log(error.message);
}

// Invalid Person
try {
  const person2 = new Person("Ananya", -5);

  console.log(person2.greet());
} catch (error) {
  console.log(error.message); // Age must be a positive number.
}
