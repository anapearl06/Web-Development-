// Task 1: Square Numbers
const squareNumbers = (arr) => {
  // Return a new array with squared values
  return arr.map((num) => num * num);
};

// Task 2: Filter Even Numbers
const filterEvenNumbers = (arr) => {
  // Return only even numbers
  return arr.filter((num) => num % 2 === 0);
};

// Task 3: Sum of Positive Numbers
const sumPositiveNumbers = (arr) => {
  // Filter positive numbers and calculate their sum
  return arr.filter((num) => num > 0).reduce((sum, num) => sum + num, 0);
};

// Task 4: Get Names
const getNames = (arr) => {
  // Return an array containing only names
  return arr.map((person) => person.name);
};

// Task 5: Find Longest Word
const findLongestWord = (arr) => {
  // Return the longest word
  return arr.reduce((longest, word) =>
    word.length > longest.length ? word : longest,
  );
};

// Test Cases

// Task 1
console.log(squareNumbers([1, 2, 3, 4, 5])); // [1, 4, 9, 16, 25]

// Task 2
console.log(filterEvenNumbers([1, 2, 3, 4, 5, 6])); // [2, 4, 6]

// Task 3
console.log(sumPositiveNumbers([-5, 10, -2, 8, 3])); // 21

// Task 4
console.log(
  getNames([
    { name: "Ananya", age: 20 },
    { name: "Ashutosh", age: 21 },
    { name: "Payal", age: 19 },
  ]),
); // ["Ananya", "Ashutosh", "Payal"]

// Task 5
console.log(findLongestWord(["cat", "elephant", "tiger", "giraffe"])); // "elephant"
