import express from "express";
import dotenv from "dotenv";

dotenv.config();

const app = express();
const port = process.env.PORT || 3000;

app.get("/", (req, res) => {
  res.send("Hello World!");
});

app.listen(port, () => {
    console.log(`Example app listening on port https://localhost:${port}`);
    console.log("Starting the Backend Project Management Application");
    console.log("Value of myusername:", process.env.USERNAME);
});

// let myusername = process.env.USERNAME;

// console.log("Value of myusername:", myusername);
//console.log("Starting the Backend Project Management Application");
