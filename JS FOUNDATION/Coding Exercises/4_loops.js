// Task 1: Sum of First N Natural Numbers
function sumOfN(n) {
  // Store the sum
  let sum = 0;

  // Add numbers from 1 to n
  for (let i = 1; i <= n; i++) {
    sum += i;
  }

  return sum;
}

// Task 2: Multiplication Table
function printMultiplicationTable(n) {
  // Store the table in an array
  let table = [];

  // Generate multiplication table from 1 to 10
  for (let i = 1; i <= 10; i++) {
    table.push(`${n} * ${i} = ${n * i}`);
  }

  return table;
}

// Task 3: Count Vowels
function countVowels(str) {
  // Store all vowels
  let vowels = "aeiouAEIOU";
  let count = 0;

  // Check each character
  for (let char of str) {
    if (vowels.includes(char)) {
      count++;
    }
  }

  return count;
}

// Test Cases

// Task 1
console.log(sumOfN(5)); // 15
console.log(sumOfN(10)); // 55

// Task 2
console.log(printMultiplicationTable(2));
/* [
   '2 * 1 = 2',
   '2 * 2 = 4',
   ...
   '2 * 10 = 20'
] */

console.log(printMultiplicationTable(5));
// [
//   '5 * 1 = 5',
//   '5 * 2 = 10',
//   ...
//   '5 * 10 = 50'
// ]

// Task 3
console.log(countVowels("Hello World")); // 3
console.log(countVowels("JavaScript")); // 3
console.log(countVowels("AEIOU")); // 5
console.log(countVowels("ChatGPT")); // 1
