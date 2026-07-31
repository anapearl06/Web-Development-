// Task: Prototype Chaining

// Parent Constructor
function Animal() {}

// Add method to Animal's prototype
Animal.prototype.speak = function () {
  return "Animal speaking";
};

// Child Constructor
function Dog() {}

// Inherit Animal's prototype
Dog.prototype = Object.create(Animal.prototype);

// Restore the constructor reference
Dog.prototype.constructor = Dog;

// Add method to Dog's prototype
Dog.prototype.bark = function () {
  return "Woof!";
};

// Create a Dog object
const dog = new Dog();

// Test Cases

// Method inherited from Animal
console.log(dog.speak()); // Animal speaking

// Method defined in Dog
console.log(dog.bark()); // Woof!

// Prototype chain verification
console.log(dog instanceof Dog); // true
console.log(dog instanceof Animal); // true

// Check the constructor
console.log(dog.constructor === Dog); // true
