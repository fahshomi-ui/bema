const { io } = require("socket.io-client");

const socket = io("https://bema-server-production.up.railway.app", {
  transports: ["websocket"],
});

socket.on("connect", () => {
  console.log("Connected to server");
  // Login as admin
  socket.emit("admin:register", { password: "admin123" });
});

socket.on("admin:authenticated", (success) => {
  if (success) {
    console.log("Logged in as admin");
    // Clear all data
    socket.emit("admin:clearAllData");
    console.log("Sent clearAllData command");
  } else {
    console.log("Login failed");
    socket.disconnect();
    process.exit(1);
  }
});

socket.on("allDataCleared", () => {
  console.log("All visitor data cleared successfully!");
  socket.disconnect();
  process.exit(0);
});

socket.on("connect_error", (err) => {
  console.log("Connection error:", err.message);
  process.exit(1);
});

// Timeout after 10 seconds
setTimeout(() => {
  console.log("Timeout - disconnecting");
  socket.disconnect();
  process.exit(1);
}, 10000);
