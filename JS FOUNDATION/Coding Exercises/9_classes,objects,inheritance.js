// Task 1, 2 & 3: Classes, Objects, and Inheritance

// Parent Class
class Vehicle {
  constructor(make, model) {
    this.make = make;
    this.model = model;
  }

  // Return vehicle details
  getDetails() {
    return `Make: ${this.make}, Model: ${this.model}`;
  }

  // Move method
  move() {
    return "The vehicle is moving";
  }

  // Check if an object is a Vehicle
  static isVehicle(obj) {
    return obj instanceof Vehicle;
  }
}

// Child Class
class Car extends Vehicle {
  constructor(make, model) {
    super(make, model);
  }

  // Start the car engine
  startEngine() {
    return "Engine started";
  }

  // Override the move method
  move() {
    return "The car is driving";
  }
}

// Create Objects
const vehicle = new Vehicle("Toyota", "Hilux");
const car = new Car("Tesla", "Model S");

// Test Cases

// Task 1
console.log(vehicle.getDetails()); // Make: Toyota, Model: Hilux
console.log(car.getDetails()); // Make: Tesla, Model: Model S
console.log(car.startEngine()); // Engine started

// Task 2
console.log(vehicle.move()); // The vehicle is moving
console.log(car.move()); // The car is driving

// Task 3
console.log(Vehicle.isVehicle(vehicle)); // true
console.log(Vehicle.isVehicle(car)); // true
console.log(Vehicle.isVehicle({})); // false
