// Task 1: Simple Generator

// Generate numbers from 1 to 3
function* numberGenerator() {
  yield 1;
  yield 2;
  yield 3;
}

// Task 2: Custom Iterator

// Create an iterator for a given range
function rangeIterator(start, end) {
  let current = start;

  return {
    next() {
      if (current <= end) {
        return {
          value: current++,
          done: false,
        };
      }

      return {
        value: undefined,
        done: true,
      };
    },
  };
}

// Task 3: Fibonacci Generator

// Generate Fibonacci numbers indefinitely
function* fibonacciGenerator() {
  let first = 1;
  let second = 1;

  while (true) {
    yield first;

    let next = first + second;
    first = second;
    second = next;
  }
}

// Test Cases

// Task 1
const numbers = numberGenerator();

console.log(numbers.next().value); // 1
console.log(numbers.next().value); // 2
console.log(numbers.next().value); // 3
console.log(numbers.next().done); // true

// Task 2
const range = rangeIterator(1, 5);

console.log(range.next()); // { value: 1, done: false }
console.log(range.next()); // { value: 2, done: false }
console.log(range.next()); // { value: 3, done: false }
console.log(range.next()); // { value: 4, done: false }
console.log(range.next()); // { value: 5, done: false }
console.log(range.next()); // { value: undefined, done: true }

// Task 3
const fibonacci = fibonacciGenerator();

console.log(fibonacci.next().value); // 1
console.log(fibonacci.next().value); // 1
console.log(fibonacci.next().value); // 2
console.log(fibonacci.next().value); // 3
console.log(fibonacci.next().value); // 5
console.log(fibonacci.next().value); // 8
console.log(fibonacci.next().value); // 13
console.log(fibonacci.next().value); // 21  4
console.log(fibonacci.next().value); // 34
console.log(fibonacci.next().value); // 55
