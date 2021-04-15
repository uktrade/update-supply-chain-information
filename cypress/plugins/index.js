module.exports = (on, config) => {
  on('task', {
    table(message) {
      console.table(message)
      return null
    },
  })
}
