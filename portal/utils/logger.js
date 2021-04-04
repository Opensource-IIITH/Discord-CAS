const info = (...params) => {
  console.log("[INFO]: ", ...params);
}

const warn = (...params) => {
  console.error("[WARN]: ", ...params);
}

const error = (...params) => {
  console.error("[ERROR]: ", ...params);
}

module.exports = {
  info,
  error,
  warn,
}
