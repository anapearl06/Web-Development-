import express from "express";

const app = express();
// basic configurations
app.use(express.json({ limit: "16kb" }))
app.use(express.urlencoded({ extended: true, limit: "16kb" }));
app.use(express.static("public"));


app.get("/", (req, res) => {
  res.send("Welcome to Basecampy");
});

export default app;


