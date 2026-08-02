const person = {
  name: "Ananya",
  greet() {
    console.log(`Hi, I am ${this.name}`);
  },
};

person.greet();

const greetFunction = person.greet;
greetFunction();

const boundGreet = person.greet.bind({ name: "Boboo" });
boundGreet();

//bind, call and apply
