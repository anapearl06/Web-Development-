// Task 1: Bind the Correct Context

const person = {
  name: "Hitesh",

  // Return an introduction
  introduce() {
    return `Hi, I'm ${this.name}`;
  },
};

// Function that executes a callback
function showIntroduction(callback) {
  console.log(callback());
}

// Bind the correct context
const boundIntroduce = person.introduce.bind(person);

// Task 2: Using call()

// Introduce a person using 'this'
function introduce() {
  return `Hello, my name is ${this.name}`;
}

const person1 = {
  name: "Ananya",
};

const person2 = {
  name: "Rahul",
};

// Task 3: Using apply()

// Add two numbers and multiply the result
function sum(num1, num2) {
  return (num1 + num2) * this.multiplier;
}

const multiplier1 = {
  multiplier: 2,
};

const multiplier2 = {
  multiplier: 5,
};

// Test Cases

// Task 1
showIntroduction(boundIntroduce);
// Hi, I'm Hitesh

// Task 2
console.log(introduce.call(person1));
// Hello, my name is Ananya

console.log(introduce.call(person2));
// Hello, my name is Rahul

// Task 3
console.log(sum.apply(multiplier1, [10, 20])); // 60
console.log(sum.apply(multiplier2, [10, 20])); // 150
console.log(sum.apply(multiplier1, [5, 15])); // 40
console.log(sum.apply(multiplier2, [5, 15])); // 75

