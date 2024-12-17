// vue.config.js
module.exports = {
  pages: {
    index: {
      entry: 'client/src/main.js',
      template: 'public/index.html',
      filename: 'index.html',
      publicPath: './'
    },
  },
}
