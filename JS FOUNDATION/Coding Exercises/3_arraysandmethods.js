// Task 1: Filter Numbers
function filterNumbers(arr) {
    // Return only number values from the array
    return arr.filter(item => typeof item === "number");
}


// Task 2: Reverse Array
function reverseArray(arr) {
    // Return a reversed copy of the array
    return [...arr].reverse();
}


// Task 3: Find Maximum
function findMax(arr) {
    // Return the largest number in the array
    return Math.max(...arr);
}


// Task 4: Remove Duplicates
function removeDuplicates(arr) {
    // Remove duplicate values using Set
    return [...new Set(arr)];
}


// Task 5: Flatten Nested Array
function flattenArray(arr) {
    // Flatten the nested array into a single array
    return arr.flat(Infinity);
}


// Test Cases

// Task 1
console.log(filterNumbers([1, "Hello", true, 25, "JS", 50]));      // [1, 25, 50]

// Task 2
console.log(reverseArray([1, 2, 3, 4, 5]));                        // [5, 4, 3, 2, 1]

// Task 3
console.log(findMax([10, 45, 78, 32, 15]));                        // 78

// Task 4
console.log(removeDuplicates([1, 2, 2, 3, 4, 4, 5]));              // [1, 2, 3, 4, 5]

// Task 5
console.log(flattenArray([1, [2, [3, 4], 5], 6]));                 // [1, 2, 3, 4, 5, 6]